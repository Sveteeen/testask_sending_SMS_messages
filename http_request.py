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
        headers = self.headers.copy()
        body_str = json.dumps(self.body, separators=(",", ":"))  # Убираем лишние пробелы
        headers["Content-Length"] = str(len(body_str.encode("utf-8")))  # Вычисляем длину тела
        headers_str = "\r\n".join(f"{k}: {v}" for k, v in headers.items())

        # Собираем полный HTTP-запрос
        request = f"{self.method} {self.path} HTTP/1.1\r\n{headers_str}\r\n\r\n{body_str}"

        return request.encode("utf-8")

    @classmethod
    def from_bytes(cls, binary_data: bytes) -> 'HTTPRequest':
        """
        Создает объект HTTP-запроса из последовательности байт.
        """
        raw_request = binary_data.decode("utf-8")
        lines = raw_request.split("\r\n")

        method, path, _ = lines[0].split(" ")
        headers = {}
        i = 1
        while lines[i]:  # Пока не встретим пустую строку (конец заголовков)
            key, value = lines[i].split(": ", 1)
            headers[key] = value
            i += 1

        body = json.loads("\r\n".join(lines[i + 1:]))

        return cls(method, path, headers, body)