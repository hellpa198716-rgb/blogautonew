import os
import feedparser
import requests
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

def fetch_latest_news():
    rss_url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    return feed.entries

def main():
    posted_urls = load_posted_urls()
    news_entries = fetch_latest_news()

    target_entry = None
    for entry in news_entries:
        if entry.link not in posted_urls:
            target_entry = entry
            break

    if not target_entry:
        print("새롭게 포스팅할 신규 뉴스 기사가 없습니다.")
        return

    print(f"새 기사 수집 완료: {target_entry.title}")

    # 1. AI 아티클 생성
    article_data = generate_article_data(target_entry.title, target_entry.get("summary", ""))
    if not article_data:
        print("AI 아티클 생성 실패로 프로세스를 종료합니다.")
        return

    wp_url = os.getenv("WP_URL")
    wp_user = os.getenv("WP_USER")
    wp_password = os.getenv("WP_APP_PASSWORD")

    # 2. 대표 이미지 업로드 및 본문 중간 이미지 구성
    media_id = None
    search_keyword = article_data.get("search_keyword", "news")
    image_url = get_unsplash_image(search_keyword)

    if image_url and wp_url:
        alt_text = article_data.get("title", "Featured Image")
        # 워드프레스 미디어 라이브러리에 업로드 및 media_id 획득
        media_id = upload_image_to_wordpress(image_url, wp_url, wp_user, wp_password, alt_text=alt_text)
        
        # 본문 상단/중간에 이미지 태그 예쁘게 삽입 (SEO alt 태그 포함)
        inline_img_html = f'''
        <div style="text-align: center; margin: 20px 0;">
            <img src="{image_url}" alt="{alt_text}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />
        </div>
        '''
        # 기존 본문에 이미지 태그 추가
        article_data["content"] = inline_img_html + article_data.get("content", "")

    # 3. 워드프레스 최종 포스팅 전송
    success = post_to_wordpress(article_data, media_id=media_id)

    if success:
        save_posted_url(target_entry.link)
        print("성공적으로 새 아티클이 발행되고 중복 URL 목록에 등록되었습니다.")
    else:
        print("워드프레스 포스팅 실패")

if __name__ == "__main__":
    main()
