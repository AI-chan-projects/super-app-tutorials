import paramiko
import logging
from getpass import getpass
import argparse  # argparse 모듈 추가

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

# 접속 직후 Welcome 메시지 출력
# 채널에서 데이터를 즉시 수신하고 출력
while not channel.recv_ready():
    pass  # 응답 대기
output = channel.recv(1024).decode()
print(output)

# 터미널 입력 및 출력 처리
while True:
    # 사용자가 입력한 명령을 채널에 보내기
    command = input("$ ")
    if command.lower() in ['exit', 'quit']:
        break
    channel.send(command + "\n")
    
    # 원격 서버에서 응답을 받기
    while not channel.recv_ready():
        pass  # 응답 대기
    output = channel.recv(1024).decode()
    
    # 원격 서버 응답 출력
    print(output)

# 채널 및 SSH 연결 종료
channel.close()
client.close()
print("터미널 세션이 종료되었습니다.")