from pymongo import MongoClient
import json

with open('test_credential/mongo_info.json') as file:
    data = json.load(file)

HOST = data['server_ip']
# MongoDB 포트 번호
PORT = data['server_port']
# 사용자 이름
USERNAME = data['user_id']
# 비밀번호
PASSWORD = data['user_pw']
# 데이터베이스 이름
DATABASE = 'admin'

# MongoDB 연결 문자열
uri = f"mongodb://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

# MongoDB 클라이언트 생성
client = MongoClient(uri)

selected_db = 'place_info'
# 데이터베이스 선택
db = client[selected_db]

# 간단한 데이터 조회 예제
collection = db['shop']
for document in collection.find():
    print(document)

# 클라이언트 연결 종료
client.close()