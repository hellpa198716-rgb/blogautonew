import os
import requests

def get_unsplash_image(keyword):
    """Unsplash API를 활용해 키워드 기반 무료 이미지 URL을 가져옵니다."""
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not access_key:
        # API 키가 없을 때 대체할 이미지 주소
        return f"https://source.unsplash.com/800x600/?{keyword}"
    
    url = f"https://api.unsplash.com/photos/random?query={keyword}&orientation=landscape"
    headers = {"Authorization": f"Client-ID {access_key}"}
    
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json()["urls"]["regular"]
    except Exception as e:
        print(f"Unsplash 이미지 수집 중 오류 발생: {e}")
        
    return f"https://source.unsplash.com/800x600/?{keyword}"

def upload_image_to_wordpress(image_url, focus_keyword, wp_url, wp_user, wp_password):
    """이미지를 다운로드하여 워드프레스 미디어 라이브러리에 업로드합니다."""
    if not wp_url or not wp_user or not wp_password:
        print("워드프레스 접속 정보가 부족하여 이미지 업로드를 스킵합니다.")
        return None, None

    try:
        img_res = requests.get(image_url, timeout=10)
        if img_res.status_code != 200:
            print(f"이미지 다운로드 실패: Status Code {img_res.status_code}")
            return None, None
        
        # 파일명 및 헤더 설정
        clean_keyword = focus_keyword.replace(" ", "_")
        filename = f"{clean_keyword}.jpg"
        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "image/jpeg"
        }
        
        endpoint = f"{wp_url.rstrip('/')}/wp-json/wp/v2/media"
        res = requests.post(
            endpoint,
            headers=headers,
            data=img_res.content,
            auth=(wp_user, wp_password)
        )
        
        if res.status_code == 201:
            data = res.json()
            return data["id"], data["source_url"]
        else:
            print(f"워드프레스 미디어 업로드 실패: {res.status_code} - {res.text}")
            
    except Exception as e:
        print(f"워드프레스 이미지 업로드 중 오류 발생: {e}")
        
    return None, None
