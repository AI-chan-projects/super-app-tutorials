import paramiko
import logging
from getpass import getpass
import argparse  # argparse 모듈 추가
from collections import deque
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO)  # 로그 레벨을 INFO로 설정
logger = logging.getLogger(__name__)

# argparse를 사용하여 명령줄 인자를 처리
parser = argparse.ArgumentParser(description="Remote SSH Access Script")
parser.add_argument("--hostname", type=str, required=True, help="Hostname of the remote server")
parser.add_argument("--port", type=int, default=22, help="Port number of the remote server")
parser.add_argument("--username", type=str, required=True, help="Username for remote server")
parser.add_argument("--pkey", type=str, help="Path to private key file for public key authentication")

args = parser.parse_args()  # 명령줄 인자 파싱

hostname = args.hostname
port = args.port
username = args.username
pkey_path = args.pkey  # 공개 키 경로를 가져옴

# SSH 클라이언트 생성
client = paramiko.SSHClient()

# 기본 설정: 호스트 키 자동 승인
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# 인증 방식 설정
if pkey_path:
    # 공개 키 인증 사용
    private_key = paramiko.RSAKey.from_private_key_file(pkey_path)
    client.connect(hostname, port=port, username=username, pkey=private_key)
else:
    # 공개 키 인증이 아닌 경우, 비밀번호를 getpass로 안전하게 입력받음
    password = getpass("password: ")
    client.connect(hostname, port=port, username=username, password=password)

# 원격 서버에 터미널 세션을 열기
channel = client.invoke_shell()

print("터미널 세션에 연결되었습니다. 명령을 입력하세요.")
output_queue = deque()  # 큐 방식으로 처리하기 위해 deque 생성

# 터미널 입력 및 출력 처리
while True:
    # 사용자가 입력한 명령을 채널에 보내기
    command = input()
    if command.lower() in ['exit', 'quit']:
        break
    channel.send(command + "\n")

    # 루프 내에서 대기 시간을 조절하여 폴링 주기를 설정
    time.sleep(0.05)  # 0.05초 대기
    
    # 원격 서버에서 응답을 받기
    while not channel.recv_ready():
        pass  # 응답 대기

    # 데이터를 수신하여 `output_queue`에 추가
    while channel.recv_ready():
        data = channel.recv(1024).decode()  # 수신한 데이터 디코딩
        output_queue.append(data)  # 데이터를 deque에 추가

    while output_queue:
        output = output_queue.popleft()  # 큐의 앞쪽에서 데이터를 꺼냄
        print(output, end='')

# 채널 및 SSH 연결 종료
channel.close()
client.close()
print("터미널 세션이 종료되었습니다.")