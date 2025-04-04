from typing import Dict
import json


class HTTPRequest:
    def __init__(self, method: str, path: str, headers: Dict[str, str], body: dict):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body

    def to_bytes(self) -> bytes:
        """
        Преобразует объект HTTP-запроса в последовательность байт.
        """
        headers_str = "\r\n".join(f"{k}: {v}" for k, v in self.headers.items())
        body_str = json.dumps(self.body)
        request = f"{self.method} {self.path} HTTP/1.1\r\n{headers_str}\r\n\r\n{body_str}"
        return request.encode("utf-8")

    @classmethod
    def from_bytes(cls, binary_data: bytes):
        """
        Создает объект HTTP-запроса из последовательности байт.
        """
        # Декодируем байты в строку
        raw_request = binary_data.decode("utf-8")

        # Разделяем запрос на строки
        lines = raw_request.split("\r\n")

        # Первая строка содержит метод и путь
        method, path, _ = lines[0].split(" ")

        # Следующие строки содержат заголовки
        headers = {}
        i = 1
        while lines[i]:  # Пока не встретим пустую строку (конец заголовков)
            key, value = lines[i].split(": ", 1)
            headers[key] = value
            i += 1

        # Остальная часть содержит тело запроса
        body = json.loads("\r\n".join(lines[i + 1:]))

        # Возвращаем новый объект HTTPRequest
        return cls(method, path, headers, body)