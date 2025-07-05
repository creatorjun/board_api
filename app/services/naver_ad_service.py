import time
import hmac
import hashlib
import base64
import httpx

from app.core.config import settings

BASE_URL = "https://api.searchad.naver.com"

def get_auth_headers(method, uri, customer_id):
    timestamp = str(int(time.time() * 1000))
    secret_key = settings.NAVER_AD_SECRET_KEY.encode('UTF-8')
    
    message = f"{timestamp}.{method}.{uri}".encode('UTF-8')
    
    signature = base64.b64encode(hmac.new(secret_key, message, hashlib.sha256).digest())

    return {
        'X-Timestamp': timestamp,
        'X-API-KEY': settings.NAVER_AD_API_KEY,
        'X-Customer': str(customer_id),
        'X-Signature': signature
    }

async def block_ip_address(customer_id: int, ip_address: str):
    uri = "/tool/ip-exclusions"
    method = "POST"
    
    headers = get_auth_headers(method, uri, customer_id)
    
    payload = {
        "filterIp": ip_address,
        "memo": "자동화 솔루션에 의해 차단됨"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BASE_URL}{uri}", headers=headers, json=payload)
            response.raise_for_status()
            
            print(f"성공: IP {ip_address}가 고객 ID {customer_id}의 차단 목록에 추가되었습니다.")

        except httpx.HTTPStatusError as e:
            print(f"네이버 광고 API 오류 발생: {e.response.status_code}, 응답: {e.response.text}")
            raise e
        except httpx.RequestError as e:
            print(f"네이버 광고 API 요청 중 예외 발생: {e}")
            raise e