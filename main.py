import toml
import argparse
import socket
from http_request import HTTPRequest
from http_response import HTTPResponse
import base64
from logger import setup_logger, log_request, log_response


def load_config():
    with open("config.toml", "r") as f:
        config = toml.load(f)
    return config


def parse_args():
    parser = argparse.ArgumentParser(description="SMS Client")
    parser.add_argument("--sender", required=True, help="Sender phone number")
    parser.add_argument("--recipient", required=True, help="Recipient phone number")
    parser.add_argument("--message", required=True, help="SMS message text")
    return parser.parse_args()


def send_request(request: HTTPRequest, host: str, port: int) -> bytes:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
            sock.sendall(request.to_bytes())
            response = sock.recv(4096)
        return response
    except ConnectionRefusedError:
        print(f"Ошибка: Не удалось подключиться к серверу {host}:{port}.")
        exit(1)


def main():
    setup_logger()
    args = parse_args()
    config = load_config()

    # Логирование входных данных
    log_request(args)

    # Формируем HTTP-запрос
    credentials = base64.b64encode(
        f"{config['username']}:{config['password']}".encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {credentials}"
    }
    body = {"sender": args.sender, "recipient": args.recipient, "message": args.message}
    request = HTTPRequest("POST", "/send_sms", headers, body)

    # Отправляем запрос
    url = config["url"]
    if ":" in url:
        host, port = url.replace("http://", "").split(":")
        port = int(port)
    else:
        host = url.replace("http://", "")
        port = 80
    try:
        response_data = send_request(request, host, port)
    except Exception as e:
        print(f"Ошибка при отправке запроса: {e}")
        exit(1)

    # Парсим ответ
    try:
        response = HTTPResponse.from_bytes(response_data)
    except Exception as e:
        print(f"Ошибка при парсинге ответа: {e}")
        exit(1)

    # Логирование ответа
    log_response(response.status_code, response.body)

    # Выводим результат
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.body}")


if __name__ == "__main__":
    main()


#python main.py --sender "+1234567890" --recipient "+0987654321" --message "Hello, this is a test message!"