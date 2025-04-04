import pytest
import json
from main import send_request
from http_request import HTTPRequest
from http_response import HTTPResponse


#Проверка, что метод .to_bytes() правильно формирует HTTP-запрос
def test_http_request_to_bytes():
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic dXNlcjpwYXNzd29yZA=="
    }
    body = {
        "sender": "+1234567890",
        "recipient": "+0987654321",
        "message": "Hello, this is a test message!"
    }
    request = HTTPRequest("POST", "/send_sms", headers, body)
    raw_request = request.to_bytes().decode("utf-8")

    # Отладочный вывод
    print("Raw request:")
    print(raw_request)

    # Вычисляем ожидаемое значение Content-Length
    body_str = json.dumps(body, separators=(",", ":"))  # Убираем лишние пробелы
    expected_content_length = str(len(body_str.encode("utf-8")))

    # Проверяем Content-Length
    assert f"Content-Length: {expected_content_length}" in raw_request

    # Проверяем тело запроса
    assert '{"sender":"+1234567890","recipient":"+0987654321","message":"Hello, this is a test message!"}' in raw_request

#Проверка, что метод .from_bytes() правильно разбирает HTTP-запрос.
def test_http_request_from_bytes():
    binary_data = (
        b"POST /send_sms HTTP/1.1\r\n"
        b"Content-Type: application/json\r\n"
        b"Authorization: Basic dXNlcjpwYXNzd29yZA==\r\n"
        b"Content-Length: 85\r\n"
        b"\r\n"
        b'{"sender": "+1234567890", "recipient": "+0987654321", "message": "Hello, this is a test message!"}'
    )
    request = HTTPRequest.from_bytes(binary_data)

    # Проверяем, что объект создан корректно
    assert request.method == "POST"
    assert request.path == "/send_sms"
    assert request.headers == {
        "Content-Type": "application/json",
        "Authorization": "Basic dXNlcjpwYXNzd29yZA==",
        "Content-Length": "85"
    }
    assert request.body == {
        "sender": "+1234567890",
        "recipient": "+0987654321",
        "message": "Hello, this is a test message!"
    }


#Проверка, что метод .to_bytes() правильно формирует HTTP-ответ.
def test_http_response_to_bytes():
    headers = {
        "Content-Type": "application/json"
    }
    body = {
        "status": "success",
        "message_id": "123456"
    }
    response = HTTPResponse(200, headers, body)
    raw_response = response.to_bytes().decode("utf-8")

    # Проверяем, что ответ содержит все необходимые части
    assert "HTTP/1.1 200" in raw_response
    assert "Content-Type: application/json" in raw_response
    assert '{"status": "success", "message_id": "123456"}' in raw_response


#Проверка, что метод .from_bytes() правильно разбирает HTTP-ответ.
def test_http_response_from_bytes():
    binary_data = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: application/json\r\n"
        b"\r\n"
        b'{"status": "success", "message_id": "123456"}'
    )
    response = HTTPResponse.from_bytes(binary_data)

    # Проверяем, что объект создан корректно
    assert response.status_code == 200
    assert response.headers == {
        "Content-Type": "application/json"
    }
    assert response.body == {
        "status": "success",
        "message_id": "123456"
    }


@pytest.fixture
def mock_socket(monkeypatch):
    class MockSocket:
        def __init__(self, *args):
            pass

        def connect(self, *args):
            pass

        def sendall(self, data):
            self.sent_data = data

        def recv(self, size):
            return (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: application/json\r\n"
                b"\r\n"
                b'{"status": "success", "message_id": "123456"}'
            )

        def close(self):
            pass

        def __enter__(self):
            return self  # Возвращаем сам объект при входе в контекст

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()  # Закрываем сокет при выходе из контекста

    monkeypatch.setattr("socket.socket", MockSocket)


def test_send_request(mock_socket):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic dXNlcjpwYXNzd29yZA=="
    }
    body = {
        "sender": "+1234567890",
        "recipient": "+0987654321",
        "message": "Hello, this is a test message!"
    }
    request = HTTPRequest("POST", "/send_sms", headers, body)
    response = send_request(request, "localhost", 4010)

    # Проверяем, что ответ сервера соответствует ожиданиям
    assert b"HTTP/1.1 200 OK" in response
    assert b'{"status": "success", "message_id": "123456"}' in response

