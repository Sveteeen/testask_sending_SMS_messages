from typing import Dict
import json


class HTTPResponse:
    def __init__(self, status_code: int, headers: Dict[str, str], body: dict):
        self.status_code = status_code
        self.headers = headers
        self.body = body

    def to_bytes(self) -> bytes:
        """
        Преобразует объект HTTPResponse в последовательность байт.
        """
        headers_str = "\r\n".join(f"{k}: {v}" for k, v in self.headers.items())
        body_str = json.dumps(self.body)
        response = f"HTTP/1.1 {self.status_code}\r\n{headers_str}\r\n\r\n{body_str}"
        return response.encode("utf-8")

    @classmethod
    def from_bytes(cls, binary_data: bytes):
        """
        Создает объект HTTPResponse из последовательности байт.
        """
        # Декодируем байты в строку
        raw_response = binary_data.decode("utf-8")

        # Разделяем HTTP-ответ на строки
        lines = raw_response.split("\r\n")

        # Извлекаем статус-код из первой строки (например, "HTTP/1.1 200 OK")
        status_line = lines[0]
        status_code = int(status_line.split()[1])

        # Парсим заголовки
        headers = {}
        i = 1
        while lines[i]:  # Заголовки заканчиваются пустой строкой
            key, value = lines[i].split(": ", 1)
            headers[key] = value
            i += 1

        # Остаток данных — это тело ответа
        body_str = "\r\n".join(lines[i + 1:])
        body = json.loads(body_str) if body_str else {}

        # Создаем и возвращаем объект HTTPResponse
        return cls(status_code=status_code, headers=headers, body=body)