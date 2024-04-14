import base64

# 이미지 파일 경로
image_path = input(str("이미지 경로 입력"))
access_token = input(str("엑세스 토큰 입력"))
coordinates = input(str("좌표 입력"))

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
        center: [127.0471, 37.6688], // 지도의 초기 중심점 [경도, 위도]
        zoom: 10 // 지도의 초기 줌 레벨
    }});
    
    map.on('load', function() {{
    map.loadImage('data:image/jpg;base64,{encoded_string}', function(error, image) {{
    if (error) throw error;
    map.addImage('pattern', image);
    map.addSource('multipolygon', {{
        'type': 'geojson',
        'data': {{
            'type': 'Feature',
            'geometry': {{
                'type': 'MultiPolygon',
                'coordinates': {coordinates} // 각 폴리곤 좌표 종료
            }}
        }}
    }});
    map.addLayer({{
        'id': 'pattern-layer',
        'type': 'fill',
        'source': 'multipolygon',
        'paint': {{
            'fill-pattern': 'pattern'
            }}
        }});
    }});
}});
</script>
</body>
</html>
"""


# HTML 파일로 저장하는 코드
html_filename = "mapbox_image_create_example.html"

with open(html_filename, 'w', encoding='UTF-8') as file:
    file.write(html_code)

html_filename