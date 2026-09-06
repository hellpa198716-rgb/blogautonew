import os
import feedparser
import requests
from ai_client import generate_article_data
from image_service import get_unsplash_image, upload_image_to_wordpress
from wordpress import post_to_wordpress

# 기사 수집 중복 방지 파일
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
    # 구글 뉴스 RSS (한국 트렌드)
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

    # 1. Gemini AI를 통한 아티클 데이터 생성 (제목, 본문, category_id, search_keyword)
    article_data = generate_article_data(target_entry.title, target_entry.get("summary", ""))
    if not article_data:
        print("AI 아티클 생성 실패로 프로세스를 종료합니다.")
        return

    # 2. Unsplash 이미지 가져오기 및 워드프레스 미디어 업로드
    media_id = None
    search_keyword = article_data.get("search_keyword", "news")
    image_url = get_unsplash_image(search_keyword)

    if image_url:
        # os.getenv 안의 이름이 Secret 이름과 완벽히 일치해야 합니다.
        wp_url = os.getenv("WP_URL")
        wp_user = os.getenv("WP_USER")
        wp_password = os.getenv("WP_APP_PASSWORD")
        alt_text = article_data.get("title", "Featured Image")
        
        media_id = upload_image_to_wordpress(image_url, wp_url, wp_user, wp_app_pass, alt_text=alt_text)

    # 3. 워드프레스에 게시글 최종 전송
    success = post_to_wordpress(article_data, media_id=media_id)

    if success:
        save_posted_url(target_entry.link)
        print("성공적으로 새 아티클이 발행되고 중복 URL 목록에 등록되었습니다.")
    else:
        print("워드프레스 포스팅 실패")

if __name__ == "__main__":
    main()
