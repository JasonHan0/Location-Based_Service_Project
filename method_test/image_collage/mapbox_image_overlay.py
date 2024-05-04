import base64

# 이미지 파일 경로
image_path = input(str("이미지 경로 입력"))
access_token = input(str("엑세스 토큰 입력"))

# 이미지를 Base64로 인코딩
with open(image_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()


html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Mapbox 이미지 오버레이 예제</title>
    <meta name="viewport" content="initial-scale=1,maximum-scale=1,user-scalable=no">
    <link href="https://api.mapbox.com/mapbox-gl-js/v2.3.1/mapbox-gl.css" rel="stylesheet">
    <script src="https://api.mapbox.com/mapbox-gl-js/v2.3.1/mapbox-gl.js"></script>
    <style>
        body {{ margin: 0; padding: 0; }}
        #map {{ position: absolute; top: 0; bottom: 0; width: 100%; }}
    </style>
</head>
<body>
<div id="map"></div>
<script>
    mapboxgl.accessToken = {access_token}; // Mapbox 액세스 토큰 설정
    var map = new mapboxgl.Map({{
        container: 'map', // 지도를 표시할 요소의 ID
        style: 'mapbox://styles/mapbox/streets-v11', // 지도 스타일
        center: [128.5918, 35.8888], // 지도의 초기 중심점 [경도, 위도]
        zoom: 10 // 지도의 초기 줌 레벨
    }});

    map.on('load', function() {{
        // 지도가 로드된 후 이미지 소스와 레이어를 추가
        map.addSource('yourImage', {{
            type: 'image',
            url: 'data:image/jpg;base64,{encoded_string}',
            coordinates: [
                [128.5918, 37.8888], // 좌상단 좌표
                [130.5918, 37.8888], // 우상단 좌표
                [130.5918, 35.8888], // 우하단 좌표
                [128.5918, 35.8888]  // 좌하단 좌표
            ]
        }});

        map.addLayer({{
            id: 'yourImageOverlay',
            source: 'yourImage',
            type: 'raster',
            paint: {{
                'raster-opacity': 0.85 // 이미지의 투명도 설정
            }}
        }});
    }});
</script>
</body>
</html>
"""

# HTML 파일로 저장하는 코드
html_filename = "mapbox_image_overlay_example.html"

with open(html_filename, 'w', encoding='UTF-8') as file:
    file.write(html_code)