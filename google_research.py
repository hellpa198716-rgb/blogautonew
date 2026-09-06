# google_research.py
import feedparser
import urllib.parse

def fetch_latest_news():
    """
    구글 뉴스 RSS를 활용해 최신 이슈를 안전하게 수집 (허위 사실 방지를 위한 실제 원문 확보)
    """
    # 예시: IT/경제/트렌드 관련 구글 뉴스 RSS (한국어)
    rss_url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(rss_url)
    articles = []
    
    for entry in feed.entries[:10]:
        title = entry.title
        link = entry.link
        summary = entry.get('summary', title)
        articles.append({
            "title": title,
            "link": link,
            "summary": summary
        })
        
    return articles