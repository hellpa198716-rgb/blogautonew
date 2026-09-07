import os
import random
import feedparser
from ai_client import generate_article_data
from image_service import get_multiple_unsplash_images, upload_image_to_wordpress
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
    rss_urls = [
        "https://news.google.com/rss/search?q=%EC%8B%A0%EC%B2%AD+%EB%B0%A9%EB%B2%95+%EC%9E%90%EA%B2%A9+%ED%99%98%EA%B8%89%EA%B8%88&hl=ko&gl=KR&ceid=KR:ko",
        "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko"
    ]
    
    entries = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        entries.extend(feed.entries)
        
    return entries

def insert_multiple_images(content, image_urls, alt_text):
    """
    본문 <h2> 소제목을 탐색하여 최대 2~3개의 소제목 위에 이미지를 자연스럽게 분배 배치
    """
    if not image_urls:
        return content

    parts = content.split("<h2>")
    if len(parts) <= 1:
        # <h2>가 없는 경우 상단에 1장만 배치
        inline_html = f'<div style="text-align: center; margin: 30px 0;"><img src="{image_urls[0]}" alt="{alt_text}" style="max-width: 100%; height: auto; border-radius: 10px;" /></div>\n'
        return inline_html + content

    new_content = parts[0]
    num_h2 = len(parts) - 1
    
    # <h2> 개수에 따라 최적의 이미지 배치 위치 선정 (최대 2~3장)
    if num_h2 <= 2:
        target_indices = [1]
    elif num_h2 == 3:
        target_indices = [1, 3]
    else:
        target_indices = [1, 3, 5] if len(image_urls) >= 3 else [1, 3]

    img_idx = 0
    for i in range(1, len(parts)):
        if i in target_indices and img_idx < len(image_urls):
            img_html = f'''
            <div style="text-align: center; margin: 35px 0 20px 0;">
                <img src="{image_urls[img_idx]}" alt="{alt_text} - {img_idx+1}" style="max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.12);" />
            </div>
            '''
            new_content += img_html + "<h2>" + parts[i]
            img_idx += 1
        else:
            new_content += "<h2>" + parts[i]

    return new_content

def main():
    # [하루 1~3회 무작위 발행 제어] 약 33% 확률로 무작위 휴식
    if random.random() < 0.33:
        print("자연스러운 발행 패턴 유지를 위해 이번 스케줄은 실행하지 않고 건너뜁니다.")
        return

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

    # 2. 이미지 2~3장 다중 수집 및 소제목 본문 배치
    media_id = None
    search_keyword = article_data.get("search_keyword", "finance")
    alt_text = article_data.get("focus_keyword", article_data.get("title", "Guide Image"))
    
    image_urls = get_multiple_unsplash_images(search_keyword, count=3)

    if image_urls and wp_url:
        # 첫 번째 이미지는 대표 썸네일로 업로드
        media_id = upload_image_to_wordpress(image_urls[0], wp_url, wp_user, wp_password, alt_text=alt_text)
        # 본문 <h2> 사이사이에 최대 2~3장 균등 삽입
        article_data["content"] = insert_multiple_images(article_data["content"], image_urls, alt_text)

    # 3. 워드프레스 포스팅 (wordpress.py)
    success = post_to_wordpress(article_data, media_id=media_id)

    if success:
        save_posted_url(target_entry.link)
        print("성공적으로 새 가이드 글이 발행되고 기록되었습니다.")
    else:
        print("워드프레스 포스팅 실패")

if __name__ == "__main__":
    main()
