# main.py
import os
import random
from google_research import fetch_latest_news
from ai_client import generate_article_content
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
    print("최신 트렌드/뉴스 수집 중...")
    news_list = fetch_latest_news()
    if not news_list:
        print("수집된 뉴스가 없습니다.")
        return

    posted_urls = load_history()
    
    # 아직 발행하지 않은 신규 뉴스 필터링
    fresh_news = [n for n in news_list if n["link"] not in posted_urls]
    
    if not fresh_news:
        print("모든 뉴스가 이미 처리되었습니다.")
        return

    # 하루 1~2개 제한을 위해 무작위로 1개만 선택하여 정밀 가공
    selected_news = random.choice(fresh_news)
    
    print(f"선택된 타겟 뉴스: {selected_news['title']}")
    
    # AI를 통한 고품질 심층 아티클 생성 (환각 방지 프롬프트 적용)
    content = generate_article_content(selected_news["title"], selected_news["summary"])
    
    if content:
        success = publish_to_wordpress(selected_news["title"], content)
        if success:
            save_history(selected_news["link"])
            print("프로세스가 안전하게 완료되었습니다.")

if __name__ == "__main__":
    main()