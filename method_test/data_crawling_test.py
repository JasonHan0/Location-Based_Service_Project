# -*- coding: utf-8 -*- 
#==============================================================================================================
## 서울 열린 데이터 광장 데이터 검색 및 엑셀 파일 다운로드

#### API를 통해 데이터를 받을 수 있지만, 데이터 제공처마다 api key를 매번 발급받아 변수로 지정해야줘야 할 수 있어, 
#### 안정적인 데이터 수급을 위하여 웹크롤링을 통한 엑셀파일 다운로드 시도하는 메소드
#==============================================================================================================

import os, time, logging
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import basic_method as bm
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
import requests
from fake_useragent import UserAgent



def csvFile_reader(filename, data_id):
    ''' csvFile_download 함수는 requests.get을 사용하며
        서울시 공공데이터의 CSV 파일을 다운로드 받기 위한 메소드
        
        filename : 다운로드 받을 경로 및 파일명, data_id : 게시물 id 값
    '''
    with open(filename, "wb") as file:
        # ua = UserAgent(use_cache_server=True)
        ua = UserAgent()
        headers = {"User-Agent": ua.random}
        response = requests.get(f"https://data.seoul.go.kr/dataList/dataView.do?onepagerow=1000&srvType=S&infId={data_id}&serviceKind=1&pageNo=1&ssUserId=SAMPLE_VIEW&strWhere=&strOrderby=&filterCol=%ED%95%84%ED%84%B0%EC%84%A0%ED%83%9D&txtFilter=", headers=headers)
        print(response.text)
        print("="*100)
            

if __name__ == "__main__":
    open_search_terms1 = "인허가 정보"
    open_search_terms2 = ""
    base_path = "C:/Users/Jason/Downloads/output"
    open_csv_path = f"{base_path}/csv"
    log_path = f"{base_path}/log"
    start_url = "http://data.seoul.go.kr/dataList/datasetList.do"                                           # 서울 열린 데이터 광장 URL

    os.makedirs(open_csv_path, exist_ok=True)                                                                   # 데이터 저장경로 디렉토리 생성
    os.makedirs(log_path, exist_ok=True)                                                                    # 로그 저장경로 디렉토리 생성
    log_date = bm.get_datetime()                                                                            # 로그 파일명에 사용할 날짜 생성 메소드
    logging.basicConfig(level=logging.INFO)                                                                 # 로그 기본 레벨 설정
    logger, stream_handler, file_handler = bm.logger_get(log_path, open_search_terms1, log_date)                  # 로그 메소드 및 변수 선언
    start = time.time()                                                                                     # 실행 시작 시간 선언
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    driver_path = ChromeDriverManager(driver_version='124.0.6367.119').install()
    print(driver_path)
    driver = uc.Chrome(executable_path=driver_path, version_main=124, enable_cdp_events=True, options=options)
    
    driver.get(start_url)                                                                                   # 설정한 URL로 웹드라이버 실행
    driver.implicitly_wait(10)                                                                              # 실행 후 페이지 로딩까지 10초 이하 딜레이
    searchBox_element = driver.find_element(By.NAME, 'searchKeyword')                                       # 검색어 입력 창 element 선언
    searchBox_element.send_keys(open_search_terms1)                                                               # 검색어 입력 
    searchBox_element.find_element(By.XPATH, '/html/body/div[3]/section/form/div[1]/div/button').click()    # 검색 버튼 클릭

    current_pageNum = 1                                                                                     # 시작 페이지 인덱스 번호 선언
    html = driver.page_source                                                                               # 현재 페이지 파싱을 위한 페이지 소스 변수 선언
    soup = BeautifulSoup(html, 'html.parser')                                                               # bs4를 사용하여 html parser 사용하여 html 데이터 변수 선언
    items = soup.find_all('div', {'class': 'search-count-text'})[0].find('strong').text.replace(',', '')    # 검색 조회 개수 데이터있는 element 선언
    end_pageNum = round(int(items)/10)+1                                                                    # 마지막 페이지 숫자 인덱스 선언
    logger.info(f'{open_search_terms1} Search Results - Total Data Count : {items}, Total Pages: {end_pageNum}')
    btn_maxIndex = 14                                                                                       # next page 버튼 elements 최대 개수
    btn_nthIndex = 3                                                                                        # Pagination을 위한 next page 버튼 elements index 초기화
    while current_pageNum <= end_pageNum:                                                                   # 마지막 페이지와 같아질 때까지 pageNum 증가하며 반복하는 while문 시작
        logger.info(f"{'='*10} Current Page Number : {current_pageNum} {'='*10} ")
        html = driver.page_source                                                                           # 현재 페이지 파싱을 위한 페이지 소스 변수 선언
        soup = BeautifulSoup(html, 'html.parser')                                                           # bs4를 사용하여 html parser 사용하여 html 데이터 변수 선언
        target = soup.find_all('a', class_='goView')                                                        # 데이터 타이틀 파싱을 위한 class elements 변수 선언
        for tar in target:
            title = tar.text.replace(" ", "_").replace("\n","").replace("\n","")                            # 데이터 타이틀 문자열 선언
            filename = f'{open_csv_path}/{title}.csv'                                                       # 저장할 데이터(엑셀) 경로 및 파일명 선언
            data_id = tar['data-rel'].split('/')[0]                                                         # 데이터 다운로드를 위한 게시물 id 값 선언
            if open_search_terms1.replace(" ", "_") in title and open_search_terms2 in title:    
                # bm.csvFile_download(filename , data_id)                                                     # basic_method의 csvFile_download 메소드 사용하여 엑셀파일 다운로드
                csvFile_reader(filename, data_id)
                break
                logger.info(f"Data Successfully Download - FileName : {title}")
            else:                                                                                           # 타이틀에 검색어 미포함의 경우 건너뜀
                logger.info(f"Data Doesn't Contained Essential Words, Skip Download - FileName : {title}")
        if btn_nthIndex == 12:                                                                              # Pagination 마지막 버튼일 경우 다음버튼 페이지 누르기
            WebDriverWait(driver,2).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#datasetVO > div.wrap-a > div > section > div.list-statistics > div > div > button.paging-next'))).click()
            btn_nthIndex = 4                                                                                # 다시 첫번째 인덱스의 버튼 클릭을 위한 btn_nthIndex 초기화
        else:
            btn_nthIndex += 1                                                                               # Pagination 다음 숫자 버튼 누르도록 인덱스 증가
            try:
                WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,f'#datasetVO > div.wrap-a > div > section > div.list-statistics > div > div > button:nth-child({btn_nthIndex})'))).click()
            except:
                # print(driver.get_url())
                continue
        current_pageNum += 1                                                                                # next button 누른 뒤 페이지 숫자 증가

    end = time.time()                                                                                       # 종료 시간 선언
    running_time = round((end-start)/60, 2)                                                                 # 총 실행 시간 계산
    logger.info(f"[End Run] Running Time: During {running_time} Minutes Running")                           # 총 실행 시간 프린트  
    logger.removeHandler(file_handler)                                                                      # 로그 파일 핸들러 종료
    logger.removeHandler(stream_handler)                                                                    # 로그 스트림 핸들러 종료
    logging.shutdown()                                                                                      # 로깅 종료