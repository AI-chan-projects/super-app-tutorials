import paramiko
import logging
from getpass import getpass

# 로깅 설정
logging.basicConfig(level=logging.INFO)  # 로그 레벨을 INFO로 설정
logger = logging.getLogger(__name__)

def info_setting(explanations):
    constants = input(explanations)
    logger.info(f"Input received for {explanations.strip(':')}: {constants}")
    return constants

hostname = str(info_setting("hostname: "))
port = int(info_setting("port number: "))
username = str(info_setting("user name: "))
password = getpass("password: ")

# SSH 클라이언트 생성
client = paramiko.SSHClient()

# 기본 설정: 호스트 키 자동 승인
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# 원격 서버에 연결
client.connect(hostname, port=port, username=username, password=password)

# 원격 명령 실행
stdin, stdout, stderr = client.exec_command('ls')

# 명령 출력 읽기
print(stdout.read().decode())

# 연결 종료
client.close()