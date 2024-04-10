from PIL import Image
import os
import concurrent.futures
import math

def calculate_collage_resolution(num_images, thumb_width=400, thumb_height=300):
    """
    이미지 개수에 따라 콜라주의 해상도 비율을 계산
    
    :param num_images: 콜라주에 포함될 이미지의 총 개수
    :param thumb_width: 이미지의 너비
    :param thumb_height: 이미지의 높이
    :return: (width, height) 형태의 튜플로 콜라주의 권장 해상도 비율
    """
    rows = int(math.sqrt(num_images))
    cols = rows

    if rows * cols < num_images:
        cols += 1
    if rows * cols < num_images:
        rows += 1

    width = cols * thumb_width
    height = rows * thumb_height

    return width, height

def process_image(image_path, thumb_width, thumb_height):
    """이미지를 리사이즈하고, 해당 이미지 객체를 반환
    
    :param image_path: 리사이즈할 이미지 파일 경로
    :param thumb_width: 리사이즈할 이미지의 너비
    :param thumb_height: 리사이즈할 이미지의 높이
    """
    img = Image.open(image_path)
    img = img.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
    return img

def create_collage(image_paths, output_path, thumb_width=400, thumb_height=300):
    """ 동적으로 콜라주의 해상도 계산
    
    :param image_paths: 콜라주에 포함될 이미지 파일 경로 리스트
    :param output_path: 콜라주 이미지 파일을 저장할 경로
    :param thumb_width: 이미지의 너비
    :param thumb_height: 이미지의 높이
    
    """
    num_images = len(image_paths)
    width, height = calculate_collage_resolution(num_images)
    
    collage = Image.new('RGB', (width, height), 'white')

    x = y = 0
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_image = [executor.submit(process_image, path, thumb_width, thumb_height) for path in image_paths]
        for future in concurrent.futures.as_completed(future_to_image):
            img = future.result()
            collage.paste(img, (x, y))
            x += thumb_width
            if x >= width:
                x = 0
                y += thumb_height
    
    collage.save(output_path)

# 이미지 파일 경로 리스트 생성 및 콜라주 생성
dir_path = input("이미지 파일이 있는 디렉토리 경로 입력: ")
image_paths = [os.path.join(dir_path, file) for file in os.listdir(dir_path) if file.endswith(('jpg', 'jpeg', 'png'))]
create_collage(image_paths, 'collage_image.jpg')
