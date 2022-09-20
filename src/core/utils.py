import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def ngrok_ip():
    resp = os.popen("curl  http://localhost:4040/api/tunnels").readlines()[0]
    js = json.loads(resp)
    return str(js.get('tunnels')[0].get('public_url'))


def find(name):
    for root, dirs, files in os.walk(BASE_DIR):
        if name in files:
            return os.path.join(root, name)


def get_relative_path(file_name):
    path = find(file_name)
    return os.path.relpath(path)


def get_project_folder_name():
    return str(BASE_DIR).split('/')[-1]


def get_debug_url(file_name):
    project_folder = get_project_folder_name()
    rel_path = os.path.join(ngrok_ip(), project_folder,
                            get_relative_path(file_name))
    return rel_path


def get_production_url(file_name):
    return os.path.join(
        f"https://{os.getenv('SERVER_URL')}{BASE_DIR}"
        f"{get_relative_path(file_name)}")


def get_url(file_name):
    d = {'true': True, 'false': False}
    if d.get(os.getenv('DEBUG').lower()):
        return get_debug_url(file_name)
    return get_production_url(file_name)
