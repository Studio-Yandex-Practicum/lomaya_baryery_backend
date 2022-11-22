from urllib.parse import urlparse

import aiohttp
from fastapi.responses import HTMLResponse

from src.core.settings import settings


class RegistrationService:
    async def get_template(self) -> HTMLResponse:
        """Возвращает HTML страницу для регистрации."""
        with open("src/html/registration.html", "r", encoding="utf-8") as html_file:
            html_string = html_file.read()
        return HTMLResponse(html_string)

    async def get_registration_ngrok_url(self) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(settings.NGROK_LOCAL_URL) as response:
                res_json = await response.json()
                public_url = res_json['tunnels'][0]['public_url']
                return urlparse(f"{public_url}/{settings.REGISTRATION_TEMPLATE_PREFIX}", "https").geturl()
