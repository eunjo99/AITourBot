import requests
import xmltodict

"""
'trrsrtNm' = 관광지명,
'trrsrtSe' = 관광지구분, 
'rdnmadr' = 소재지도로명주소, 
'lnmadr' = 소재지지번주소, 
'latitude' = 위도, 
'longitude' = 경도, 
'ar' = 면적, 
'cnvnncFclty' = 공공편익시설정보, 
'stayngInfo' = 숙박시설정보, 
'mvmAmsmtFclty' = 운동및오락시설정보, 
'recrtClturFclty' = 휴양및문화시설정보, 
'hospitalityFclty' = 접객시설정보, 
'sportFclty' = 지원시설정보, 
'appnDate' = 지정일자, 
'aceptncCo' = 수용인원수, 
'prkplceCo' = 주차가능수, 
'trrsrtIntrcn' = 관광지소개, 
'phoneNumber' = 관리기관전화번호, 
'institutionNm' = 관리기관명, 
'referenceDate' = 데이터기준일자, 
'instt_code' = 제공기관코드 
""" 

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

# 테스트
if __name__ == "__main__":
    print(f"전체 데이터 개수: {get_total_count()}")