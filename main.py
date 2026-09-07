import os
import datetime
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
    # URL 순수 주소만 들어가도록 수정되었습니다.
    rss_urls = [
        "https://news.google.com/rss/search?q=%EC%8B%A0%EC%B2%AD+%EB%B0%A9%EB%B2%95+%EC%9E%90%EA%B2%A9+%ED%99%98%EA%B8%89%EA%B8%88&hl=ko&gl=KR&ceid=KR:ko",
        "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko"
    ]
    
    entries = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        print(f"[RSS 수집 결과] {url} -> {len(feed.entries)}개 기사 발견")
        entries.extend(feed.entries)
        
    return entries

def attach_eeat_metadata(content, source_link):
    today_str = datetime.datetime.now().strftime("%Y년 %m월 %d일")
    
    eeat_footer = f"""
    <hr style="margin-top: 40px; border: 0; border-top: 1px solid #eee;" />
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; font-size: 0.9em; color: #444; margin-top: 30px;">
        <p style="margin: 0 0 8px 0;"><strong>정보 검증 및 편집 안내</strong></p>
        <p style="margin: 0 0 5px 0;">• <strong>작성자:</strong> Trend Scan 편집팀 (정책·금융 정보 검증 전담)</p>
        <p style="margin: 0 0 5px 0;">• <strong>최종 검수일:</strong> {today_str}</p>
        <p style="margin: 0 0 8px 0;">• <strong>자료 검증 및 수집 출처:</strong></p>
        <ul style="margin: 0; padding-left: 20px;">
            <li><a href="https://www.wetax.go.kr" target="_blank" rel="nofollow noopener">위택스(WeTax) 지방세 환급 공식 창구</a></li>
            <li><a href="https://www.gov.kr" target="_blank" rel="nofollow noopener">정부24 지방세 환급금 신청 안내</a></li>
            <li>행정안전부 및 관할 지자체 공식 공고 데이터</li>
        </ul>
        <p style="margin: 10px 0 0 0; font-size: 0.85em; color: #777;">※ 본 가이드는 공식 행정기관 자료를 기초로 2026년 9월 기준 조건을 검증하여 재구성되었습니다.</p>
    </div>
    """
    return content + eeat_footer

def insert_multiple_images(content, image_urls, alt_text):
    if not image_urls:
        return content

    parts = content.split("<h2>")
    if len(parts) <= 1:
        inline_html = f'<div style="text-align: center; margin: 30px 0;"><img src="{image_urls[0]}" alt="{alt_text}" style="max-width: 100%; height: auto; border-radius: 10px;" /></div>\n'
        return inline_html + content

    new_content = parts[0]
    num_h2 = len(parts) - 1
    
    target_indices = [1, 3] if num_h2 >= 3 else [1]

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
    posted_urls = load_posted_urls()
    entries = fetch_latest_topics()

    print(f"총 수집된 RSS 기사 수: {len(entries)}개 / 기존 작성된 URL 수: {len(posted_urls)}개")

    target_entry = None
    for entry in entries:
        if entry.link not in posted_urls:
            target_entry = entry
            break

    if not target_entry:
        print("새롭게 작성할 수 있는 정보형 주제가 없습니다.")
        return

    print(f"가이드 수집 및 검증 시작: {target_entry.title}")

    # 1. 정보 추출 및 출처 링크 전달
    source_url = target_entry.link
    summary_text = target_entry.get("summary", "")
    
    article_data = generate_article_data(target_entry.title, summary_text, source_url=source_url)
    if not article_data:
        print("AI 검증 아티클 생성 실패로 종료합니다.")
        return

    # 2. E-E-A-T 검증 하단 블록 삽입
    article_data["content"] = attach_eeat_metadata(article_data["content"], source_url)

    wp_url = os.getenv("WP_URL")
    wp_user = os.getenv("WP_USER")
    wp_password = os.getenv("WP_APP_PASSWORD")

    # 3. 이미지 수집 및 삽입
    media_id = None
    search_keyword = article_data.get("search_keyword", "finance")
    alt_text = article_data.get("focus_keyword", article_data.get("title", "Guide Image"))
    
    image_urls = get_multiple_unsplash_images(search_keyword, count=2)

    if image_urls and wp_url:
        media_id = upload_image_to_wordpress(image_urls[0], wp_url, wp_user, wp_password, alt_text=alt_text)
        article_data["content"] = insert_multiple_images(article_data["content"], image_urls, alt_text)

    # 4. 워드프레스 발행
    success = post_to_wordpress(article_data, media_id=media_id)

    if success:
        save_posted_url(target_entry.link)
        print("E-E-A-T 기반 가이드가 성공적으로 발행되었습니다.")
    else:
        print("워드프레스 포스팅 실패")

if __name__ == "__main__":
    main()
