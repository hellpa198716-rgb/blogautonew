import os
import random
import time
from google_research import fetch_latest_news
from ai_client import generate_article_data
from image_service import get_unsplash_image, upload_image_to_wordpress
from wordpress import publish_to_wordpress

HISTORY_FILE = "posted_urls.txt"

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_history(link):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")

def main():
    # 스팸 알고리즘 회피를 위한 랜덤 실행 지연 (1분 ~ 15분 무작위 대기)
    random_delay = random.randint(60, 900)
    print(f"알고리즘 보호를 위해 {random_delay}초 후 포스팅 프로세스를 시작합니다...")
    time.sleep(random_delay)

    print("최신 이슈 수집 중...")
    news_list = fetch_latest_news()
    if not news_list:
        print("수집된 뉴스가 없습니다.")
        return

    posted_urls = load_history()
    fresh_news = [n for n in news_list if n["link"] not in posted_urls]
    
    if not fresh_news:
        print("신규 이슈가 없습니다.")
        return

    # 하루 1~2회 실행 스케줄에서 무작위 1개만 선별 발행
    selected_news = random.choice(fresh_news)
    print(f"타겟 뉴스: {selected_news['title']}")
    
    # 1. AI 기반 SEO 글 생성
    article_data = generate_article_data(selected_news["title"], selected_news["summary"])
    if not article_data:
        print("기사 생성 실패")
        return

    focus_keyword = article_data.get("focus_keyword", "뉴스")
    
    # 2. 이미지 처리 (썸네일 및 본문 이미지)
    wp_url = os.getenv("WP_URL")
    wp_user = os.getenv("WP_USER")
    wp_pass = os.getenv("WP_APP_PASSWORD")
    
    img_url = get_unsplash_image(focus_keyword)
    media_id, uploaded_url = upload_image_to_wordpress(img_url, focus_keyword, wp_url, wp_user, wp_pass)

    # 3. 워드프레스 발행
    success = publish_to_wordpress(article_data, featured_media_id=media_id, body_image_url=uploaded_url)
    if success:
        save_history(selected_news["link"])

if __name__ == "__main__":
    main()
