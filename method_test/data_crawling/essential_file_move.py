# -*- coding: utf-8 -*- 

import os
import shutil

def move_filtered_files():
    """
    지정된 기본 경로에서 주어진 필터를 기반으로 파일을 'essential_csv'라는 하위 폴더로 이동합니다.

    매개변수:
    - base_path (str): 파일이 위치한 기본 경로입니다.
    - filter (list): 파일을 필터링하는 데 사용되는 문자열의 리스트입니다.

    반환값:
    - None
    """

    base_path = input("기본 경로를 입력하세요: ")
    filter = list(input("필터를 입력하세요: ").split(", "))

    # 주어진 필터를 기반으로 파일을 필터링합니다.
    filtered_files = [i for i in os.listdir(base_path) if any(n in i for n in filter)]
    print("대상파일 수:", len(filtered_files))

    # 'essential_csv'라는 하위 폴더가 없으면 생성합니다.
    os.makedirs(f"{base_path}/essential_csv", exist_ok=True)

    # 필터링된 파일을 'essential_csv'라는 하위 폴더로 이동합니다.
    for file in filtered_files:
        source_path = os.path.join(base_path, file)
        destination_path = os.path.join(base_path, "essential_csv", file)
        shutil.move(source_path, destination_path)

    # 이동된 CSV 파일의 수를 출력합니다.
    moved_files = len([i for i in os.listdir(f"{base_path}/essential_csv") if i.endswith(".csv")])
    print(f"필터링된 {moved_files} csv 파일이 성공적으로 이동되었습니다.")

move_filtered_files()