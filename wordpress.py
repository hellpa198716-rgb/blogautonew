# wordpress.py
import os
import requests
from requests.auth import HTTPBasicAuth

def publish_to_wordpress(title, content):
    wp_url = os.getenv("WP_URL").rstrip('/')
    wp_user = os.getenv("WP_USER")
    wp_password = os.getenv("WP_APP_PASSWORD")
    
    api_endpoint = f"{wp_url}/wp-json/wp/v2/posts"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "title": title,
        "content": content,
        "status": "publish" # 바로 발행 또는 "draft"로 테스트 가능
    }
    
    response = requests.post(
        api_endpoint,
        headers=headers,
        json=payload,
        auth=HTTPBasicAuth(wp_user, wp_password)
    )
    
    if response.status_code == 201:
        print(f"성공적으로 워드프레스에 발행되었습니다: {title}")
        return True
    else:
        print(f"발행 실패: {response.status_code} - {response.text}")
        return False