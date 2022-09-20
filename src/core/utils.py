import json
import os
from pathlib import Path
from dotenv import load_dotenv

from src.core.settings import settings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def get_ngrok_ip():
    """Получение ip адреса ngrok."""
    resp = os.popen("curl  http://localhost:4040/api/tunnels").readlines()[0]
    js = json.loads(resp)
    return str(js.get('tunnels')[0].get('public_url'))


def find(file_name: str):
    """Поиск файла по имени, получение его абсолютного пути."""
    for root, dirs, files in os.walk(BASE_DIR):
        if file_name in files:
            return os.path.join(root, file_name)


def get_relative_path(file_name: str):
    """Поиск файла по имени, получение его относительного пути."""
    path = find(file_name)
    return os.path.relpath(path)


def get_project_folder_name():
    """Получение имени проектной папки"""
    return str(BASE_DIR).split('/')[-1]


def get_debug_url(file_name: str):
    """Путь для доступа из внешней среды к заданному файлу."""
    project_folder = get_project_folder_name()
    rel_path = os.path.join(get_ngrok_ip(), project_folder,
                            get_relative_path(file_name))
    return rel_path


def get_production_url(file_name: str):
    """Формирование url для заданного файла для доступа к нему на сервере."""
    return os.path.join(
        f"https://{settings.SERVER_URL}{BASE_DIR}"
        f"{get_relative_path(file_name)}")


def get_url(file_name: str):
    """Выбор url в зависимости от работы на локале или на проде."""
    d = {'true': True, 'false': False}
    if d.get(settings.DEBUG.lower()):
        return get_debug_url(file_name)
    return get_production_url(file_name)
