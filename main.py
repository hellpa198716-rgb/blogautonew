import os
import feedparser
from ai_client import generate_article_data
from image_service import get_unsplash_image, upload_image_to_wordpress
from wordpress import post_to_wordpress

POSTED_URLS_FILE = "posted_urls.txt"

def load_posted_urls():
    if os.path.exists(POSTED_URLS_FILE):
        with open(POSTED_URLS_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_posted_url(url):
    with open(POSTED_URLS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{url}\n")

def fetch_latest_topics():
    # 검색 수명이 길고 경쟁률이 낮은 정보형 검색 키워드 타깃 RSS 수집
    rss_urls = [
        "https://news.google.com/rss/search?q=%EC%8B%A0%EC%B2%AD+%EB%B0%A9%EB%B2%95+%EC%9E%90%EA%B2%A9+%ED%99%98%EA%B8%89%EA%B8%88&hl=ko&gl=KR&ceid=KR:ko",
        "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko"
    ]
    
    entries = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        entries.extend(feed.entries)
        
    return entries

def insert_inline_image(content, image_url, alt_text):
    """첫 번째 <h2> 소제목 바로 위에 고화질 본문 이미지 자연스럽게 배치"""
    inline_html = f'''
    <div style="text-align: center; margin: 30px 0;">
        <img src="{image_url}" alt="{alt_text}" style="max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />
    </div>
    '''
    if "<h2>" in content:
        return content.replace("<h2>", f"{inline_html}\n<h2>", 1)
    else:
        return inline_html + content

def main():
    posted_urls = load_posted_urls()
    entries = fetch_latest_topics()

    target_entry = None
    for entry in entries:
        if entry.link not in posted_urls:
            target_entry = entry
            break

    if not target_entry:
        print("새롭게 작성할 수 있는 정보형 주제가 없습니다.")
        return

    print(f"새로운 가이드 주제 수집 완료: {target_entry.title}")

    # 1. 정보형 장문 가이드 생성 (prompts.py)
    article_data = generate_article_data(target_entry.title, target_entry.get("summary", ""))
    if not article_data:
        print("AI 아티클 생성 실패로 프로세스를 종료합니다.")
        return

    wp_url = os.getenv("WP_URL")
    wp_user = os.getenv("WP_USER")
    wp_password = os.getenv("WP_APP_PASSWORD")

    # 2. 이미지 수집 및 본문 <h2> 위에 배치
    media_id = None
    search_keyword = article_data.get("search_keyword", "finance")
    image_url = get_unsplash_image(search_keyword)

    if image_url and wp_url:
        alt_text = article_data.get("focus_keyword", article_data.get("title", "Guide Image"))
        media_id = upload_image_to_wordpress(image_url, wp_url, wp_user, wp_password, alt_text=alt_text)
        article_data["content"] = insert_inline_image(article_data["content"], image_url, alt_text)

    # 3. 워드프레스 포스팅 (wordpress.py)
    success = post_to_wordpress(article_data, media_id=media_id)

    if success:
        save_posted_url(target_entry.link)
        print("성공적으로 새 가이드 글이 발행되고 기록되었습니다.")
    else:
        print("워드프레스 포스팅 실패")

if __name__ == "__main__":
    main()
