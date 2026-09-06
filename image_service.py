import os
import random
import requests

def get_unsplash_image(keyword):
    """Unsplash API를 활용해 키워드 기반 무료 이미지 URL을 가져옵니다."""
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    
    # API 키가 없거나 비어있는 경우 Picsum 랜덤 이미지 사용 (중복 방지)
    random_seed = random.randint(1, 10000)
    fallback_url = f"https://picsum.photos/800/600?random={random_seed}"
    
    if not access_key:
        return fallback_url
    
    url = f"https://api.unsplash.com/photos/random?query={keyword}&orientation=landscape"
    headers = {"Authorization": f"Client-ID {access_key}"}
    
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json()["urls"]["regular"]
    except Exception as e:
        print(f"Unsplash 이미지 수집 중 오류 발생: {e}")
        
    return fallback_url
