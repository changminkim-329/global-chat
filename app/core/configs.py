import os
from .consts import BASE_PATH
origins =[
    'http://127.0.0.1:3000',
    'http://localhost:3000',
    'http://localhost:8087',
    'http://127.0.0.1:8087',
    'http://localhost:80',
    'http://127.0.0.1:80',
]

pictures_path = os.path.join(BASE_PATH,'static/pictures')
if not os.path.isdir(pictures_path):
    os.mkdir(pictures_path)
