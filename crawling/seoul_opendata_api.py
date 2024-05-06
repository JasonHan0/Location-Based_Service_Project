import requests, json
import basic_method as bm

setting = bm.read_json()
url = f"http://swopenAPI.seoul.go.kr/api/subway/{setting['subway_api_key']}/json/realtimeStationArrival/0/5/{setting['subway_station']}"
response = requests.get(url)
print(response.content.decode('utf-8'))