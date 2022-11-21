from fastapi.responses import HTMLResponse


class RegistrationService:
    async def get_template(self) -> HTMLResponse:
        """Проверка, что бот запустился и работает корректно."""
        with open("src/html/registration.html", "r", encoding="utf-8") as html_file:
            html_string = html_file.read()
        return HTMLResponse(html_string)
