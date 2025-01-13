import requests
import pandas as pd
import xmltodict
import numpy as np

# API 관련 정보
API_URL = 'http://api.data.go.kr/openapi/tn_pubr_public_trrsrt_api'
API_KEY = 'dCFfL1h1/vq0CZCZeUrfil0zO7OPzVQm+42mrbMGz+V1gsirHXJ89fqCU3RXAO4sc8SsK7LCrQpKI1cygL3fAw=='

def get_total_count():
    """
    API 호출을 통해 전체 데이터 개수를 반환.

    Returns:
        int: 전체 데이터 개수 (totalCount)
    """
    params = {'serviceKey': API_KEY, 'pageNo': '1', 'numOfRows': '1', 'type': 'xml'}
    response = requests.get(API_URL, params=params)
    
    if response.status_code != 200:
        raise Exception("API 호출 실패: 응답 코드 {}".format(response.status_code))
    
    dic = xmltodict.parse(response.content)
  
    total_count = int(dic['response']['body']['totalCount'])
    return total_count

def fetch_data_by_page(page, num_of_rows=300):
    """
    특정 페이지의 데이터를 가져옴.
    
    Args:
        page (int): 가져올 페이지 번호.
        num_of_rows (int): 한 번에 가져올 데이터 수.
    
    Returns:
        list: 해당 페이지의 데이터 목록.
    """
    params = {
        'serviceKey': API_KEY,
        'pageNo': str(page),
        'numOfRows': str(num_of_rows),
        'type': 'xml'
    }
    response = requests.get(API_URL, params=params)
    
    if response.status_code != 200:
        raise Exception("API 호출 실패: 응답 코드 {}".format(response.status_code))
    
    dic = xmltodict.parse(response.content)
    
    items = dic['response']['body']['items']['item']
    
    # 데이터가 한 개만 있을 경우에도 리스트로 처리
    if isinstance(items, list):
        return items
    else:
        return [items]

def save_to_csv(data, filename="tour_data.csv"):
    """
    데이터를 DataFrame으로 변환 후 CSV로 저장.
    """
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"데이터 저장 완료: {filename}")

def main():
    """
    전체 데이터를 가져와 CSV로 저장하는 메인 함수.
    """
    print("전체 데이터 개수 확인 중...")
    total_count = get_total_count()
    print(f"전체 데이터 개수: {total_count}")
    
    num_of_rows = 300  # 한 번에 가져올 데이터 수
    total_pages = int(np.ceil(total_count / num_of_rows))
    print(f"총 페이지 수: {total_pages}")
    
    all_data = []  # 전체 데이터를 저장할 리스트
    
    for page in range(1, total_pages + 1):
        print(f"{page}/{total_pages} 페이지 처리 중...")
        try:
            page_data = fetch_data_by_page(page, num_of_rows)
            all_data.extend(page_data)
        except Exception as e:
            print(f"페이지 {page} 처리 중 오류 발생: {e}")
    
    # CSV 저장
    save_to_csv(all_data)

if __name__ == "__main__":
    main()