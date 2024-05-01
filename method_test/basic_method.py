import os, logging, traceback, json, requests, time, re
from datetime import date 
from requests import get
from fake_useragent import UserAgent
from urllib.request import urlopen
import platform

if platform.uname()[0] == "Windows":
    import pywinauto
    from pywinauto.application import Application

    def edit_encoding(filepath):
        ''' edit_encoding 함수는 pywinauto를 사용하여 메모장을 GUI 자동화 하도록 동작
            CSV 파일의 인코딩 형식을 자동으로 UTF-8(BOM)으로 수정하여, 큰 CSV 파일이 읽히지 않는 현상을 방지하기 위한 기능

            filepath : 변경할 CSV파일 전체 경로
        '''
        if "\\" in filepath:                                            # 파일 경로에 백슬래시가 있을 경우
            file_name = filepath.split("\\")[-1]                        # 파일명 선언
        elif "/" in filepath:                                           # 파일 경로에 슬래시가 있을경우
            filepath = filepath.replace("/", "\\")                      # 슬래시를 백슬래시로 변경
            file_name = filepath.split("\\")[-1]                        # 파일명 선언

        new_notepad_title = "제목 없음 - 메모장"                         # 메모장 기본 창 이름 선언
        open_window = "열기"                                            # 메모장 열기 창 이름 선언
        saveAs_window = "다른 이름으로 저장"                             # 메모장 다른 이름으로 저장 창 이름 선언
        confirmSaveAs_window = "다른 이름으로 저장 확인"                  # 메모장 다른 이름으로 저장 창 이름 선언
        app = pywinauto.application.Application()                       # 열려진 메모장 다이얼로그 창에 컨넥트 함
        app = Application().start("notepad.exe")                        # 열린 창이 없을때는 Run a target application
        app[new_notepad_title].menu_select("파일(F)-->열기(O)")          # 메뉴의 파일-열기 선택
        app[open_window].Edit.type_keys(filepath)                       # 파일 경로 입력
        app[open_window]["열기(O)"].click()                              # 열기 클릭
        app[file_name].menu_select("파일(F)-->다른 이름으로 저장(A)")     # 메뉴의 파일-다른 이름으로 저장 선택
        app[saveAs_window].Edit.type_keys(filepath)                     # 파일 경로 입력
        app[saveAs_window].ComboBox2.select("모든 파일 (*.*)")           # 파일형식 모든파일로 선택
        app[saveAs_window].ComboBox3.select("UTF-8(BOM)")               # 인코딩 형식 UTF-8(BOM) 선택
        app[saveAs_window]["저장(S)"].click()                            # 저장 클릭
        app[confirmSaveAs_window]["예(Y)"].click()                      # 원본 파일 덮어쓰기
        app[file_name].close()                                          # 메모장 닫기

def file_list(path, format):                                                        # 경로 값을 입력으로 받아 format 파일 리스트를 반환
    ''' file_list 함수는 경로 내 원하는 포멧의 파일리스트를 반환

        path : 리스트를 가져올 폴더 경로, format : 조회할 파일 확장자
    '''
    file_list = os.listdir(path)                                                    # 경로 내 파일리스트 선언
    format_files = [file for file in file_list if file.endswith(f".{format}")]      # 파일리스트 중 선택한 확장자 필터
    return format_files

def clean_text(inputString):
    ''' clean_text 함수는 re.compile 메소드를 사용하여 특수문자를 제거
    '''
    pattern_punctuation = re.compile(r'[=+,#/\?:^.@*\"※~ㆍ』‘|\(\)\[\]`\'…》\”\“\’·<>]')    # regex의 compile을 사용하여 특수문자 선언
    output_string = pattern_punctuation.sub('', inputString)                                 # 입력 문자열에서 특수문자 제거
    return output_string

def load_checkpoint(index_path):                                                                        # 저장된 좌표 리스트 탐색 수를 불러오는 함수
    ''' load_checkpoint 함수는 pickle 함수 사용해 리스트를 쓰고 저장, 
        오류 및 수동 종료 등의 경우에 마지막 실행 횟 수를 저장하고 불러오기.
        입력한 경로에 저장된 정수형 인덱스를 반환
        
        index_path : 인덱스가 저장된 경로 값 문자열 변수, 파일이 없는 경우 새로 생성(초기 실행)
    '''
    try:                                                                                                # 
        with open(index_path, 'r', encoding="utf-8") as file:
            index = file.read()
    except:                                                                                             # 초기 실행일 경우 저장 폴더 및 파일 생성
        os.makedirs(index_path.split("/")[-1], exist_ok=True)
        with open(index_path, 'w', encoding="utf-8") as file:
            data = str(0)
            index = file.write(data)
    return int(index)

def geo_mkdir(basic_path, set_addr, target_dir):                                                         # 데이터 저장 디렉토리 생성 함수
    ''' geo_mkdir 함수는 os 라이브러리의 makedirs 메소드를 사용
        "행정시 행정구 행정동" 형식의 주소 정보를 기반으로 폴더를 생성하고 생성된 경로를 반환한다.
        
        basic_path : 기본경로, set_addr : 주소정보 문자열(시 구 동 형식), target_dir : 시/구/동 폴더 하위에 생성할 폴더
    '''
    dir_path = f"{basic_path}/{set_addr.split(' ')[0].strip()}/{set_addr.split(' ')[1].strip()}/{set_addr.split(' ')[2].strip()}/{target_dir}"
    os.makedirs(dir_path, exist_ok=True) 
    return dir_path

def get_datetime(type=None):
    ''' date.datetime 모듈을 사용하여 날짜 값을 원하는 날짜형식의 문자열로 반환

        type = None : YYmmDD 형식의 날짜 문자열을 반환, type = 1 : YYYY-mm-DD 형식의 날짜 문자열을 반환
    '''
    if type == None:
        today = date.today()
        date_form = today.isoformat()
        datetime = date_form[2:].replace("-", "")
    elif type == 1:
        today = date.today()
        datetime = today.isoformat()
    return datetime

def logger_get(log_path, target, datetime=get_datetime()):                                              # 로그 생성 메소드
    ''' logger_get 함수는 logging 모듈을 사용하여 로그를 생성.
        설정된 포멧으로 로그를 생성할 수 있도록 편의성 개선한 함수
        같은 입력 값의 로그를 생성할 경우 인덱스 기반으로 새로운 로그 파일을 만들어서 덮어쓰지 않도록 설계\n
        반환 되는 값은 logger, stream_handler, file_handler

        log_path : 로그를 저장할 경로, target : 로그 파일 구분을 위해 파일명에 들어갈 문자열, datetime : 로그 생성일자를 파일명에 넣기 위한 날짜 문자열
    '''
    try:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)                                                                   # 로그의 출력 기준 설정
        logger.setLevel(logging.WARNING)
        logger.setLevel(logging.ERROR)
        logger.setLevel(logging.DEBUG)
        logger.setLevel(logging.NOTSET)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')           # log 출력 형식
        stream_handler = logging.StreamHandler()                                                        # log 출력
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        os.makedirs(log_path, exist_ok=True)

        file_idx = 0
        log_files = os.listdir(log_path)
        while True:
            file_idx += 1
            log_filename = f'{datetime}_{target}_{str(file_idx).zfill(2)}.txt'
            if log_filename not in log_files:
                break
            
        file_handler = logging.FileHandler(f"{log_path}/{log_filename}", encoding="utf-8")              # log를 파일에 출력
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    except KeyboardInterrupt:
        print("KeyboardInterrupt로 인하여 로그 종료")
        logger.removeHandler(stream_handler)
        logger.removeHandler(file_handler)
    
    except:
        err = traceback.format_exc()
        print(f"오류로 인하여 로그 종료: {err}")
        logger.removeHandler(stream_handler)
        logger.removeHandler(file_handler)
        
    return logger, stream_handler, file_handler

def get_size(path):
    ''' get_size 함수는 os.path.getsize를 사용하는 모듈
        한 줄로 파일 사이즈를 불러 올 수 있지만, bytes 단위의 크기를 구분이 쉽도록 KB, MB, GB 단위로 자동으로 변환하여 크기 값을 반환

        path : 파일 사이즈를 읽어올 파일 위치 경로 값
    '''
    size = os.path.getsize(path)
    if size < 1024:
        return f"{size} bytes"
    elif size < 1024*1024:
        return f"{round(size/1024, 2)} KB"
    elif size < 1024*1024*1024:
        return f"{round(size/(1024*1024), 2)} MB"
    elif size < 1024*1024*1024*1024:
        return f"{round(size/(1024*1024*1024), 2)} GB"

def img_down(url, file_name):
    ''' img_down 함수는 requests.get을 사용하는 모듈
        URL의 requests의 response를 contents로 받아 파일로 쓰는 모듈. 이미지를 다운로드할 때 사용한다.

        url : 이미지를 다운로드 할 이미지 URL, file_name : 저장 할 파일명 
    '''
    with open(file_name, "wb") as file:                                                                 # open in binary mode
            response = get(url)                                                                         # get request
            file.write(response.content)                                                                # write to file

def get_url(url):
    ''' get_url 함수는 requests.get을 사용하는 모듈
        URL의 requests의 response를 json형식의 텍스트로 반환받기 위한 함수

        url : response를 읽고자 하는 URL
    '''
    return requests.get(url).json()

def get_urlopen(url):
    ''' get_urlopen 함수는 urlopen를 사용하며, 인코딩 오류를 해결하기 위해 get_url 함수를 대체하기 위함
        
        url : response를 읽고자 하는 URL
    '''
    page = urlopen(url)
    data = page.read().decode('utf-8')
    return json.loads(data)

def csvFile_download(filename, data_id):
    ''' csvFile_download 함수는 requests.get을 사용하며
        서울시 공공데이터의 CSV 파일을 다운로드 받기 위한 메소드
        
        filename : 다운로드 받을 경로 및 파일명, data_id : 게시물 id 값
    '''
    response = get(f'http://datafile.seoul.go.kr/bigfile/iot/sheet/csv/download.do?onepagerow=1000&srvType=S&infId={data_id}&serviceKind=1&pageNo=1&ssUserId=SAMPLE_VIEW&strWhere=&strOrderby=&')
    print(f'http://datafile.seoul.go.kr/bigfile/iot/sheet/csv/download.do?onepagerow=1000&srvType=S&infId={data_id}&serviceKind=1&pageNo=1&ssUserId=SAMPLE_VIEW&strWhere=&strOrderby=&')
    with open(filename, "wb") as file:
        file.write(response.content)

def csvFile_download2(filename, data_id, max_retries=5):
    ''' get_url 함수는 requests.get을 사용하는 모듈
        URL의 requests의 response를 json형식의 텍스트로 반환받기 위한 함수

        url : response를 읽고자 하는 URL
    '''
    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.0.0',
    }
    
    retries = 0  # 재시도 횟수 초기화
    while retries <= max_retries:
        try:
            response = get(f'http://datafile.seoul.go.kr/bigfile/iot/sheet/csv/download.do?onepagerow=1000&srvType=S&infId={data_id}&serviceKind=1&pageNo=1&ssUserId=SAMPLE_VIEW&strWhere=&strOrderby=&', headers=headers)
            response.raise_for_status()  # 200 OK 코드가 아니면 예외 발생
            with open(filename, "wb") as file:
                file.write(response.content)
            break
        except requests.RequestException:
            retries += 1  # 재시도 횟수 증가
            time.sleep(1)  # 1초 대기 후 재시도
            
    return None  # 최대 재시도 횟수를 초과한 경우 None 반환

def cal_pg(cnt, start_idx, start_time, list_length):
    ''' cal_pg 함수는 실행 경과를 확인하기 위한 함수
        전체 실행횟수는 리스트 형태 데이터의 길이를 측정하여 계산하고, 현재 실행횟수는 저장된 시작 인덱스와 현재 반복횟수를 더하여 계산한다. 
        시작 실행시간 또한 불러와서 현재 실행시간도 계산
        전체 진행률, 현재 실행 진행률, 실행시간, 실행시간 단위를 반환한다. 

        cnt : 현재 반복 횟수, start_idx : 저장된 시작 인덱스, start_time : time.time()으로 시작 시 측정한 시간, list_length : 전체 실행할 리스트 길이
    '''
    total_per = round((start_idx + cnt) / list_length, 2) * 100
    current_per = round(cnt / (list_length - start_idx), 4) * 100
    current_time = time.time()
    cal_time = current_time - start_time
    if cal_time < 60:
        run_time = cal_time
        unit = "sec"
    elif cal_time >= 60 and cal_time < 3600:
        run_time = round((cal_time)/60, 2)
        unit = "min"
    elif cal_time >= 3600:
        run_time = round((cal_time)/3600, 2)
        unit = "hour"
    return total_per, current_per, run_time, unit

def filter_json(input_json, option):
    ''' filter_json 함수는 geojson 파일을 파싱하기 위한 함수

        input_json : 파싱할 geojson 파일, option : 행정동 선택
    '''
    
    output_dict = [x for x in input_json["features"] if x["properties"]
                ["sido"] == "11" and f"{option[:-1]}" in x["properties"]["temp"]]
    output_json = json.dumps(output_dict)
    return output_json