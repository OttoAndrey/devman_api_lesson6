import os
import random

import requests
from dotenv import load_dotenv


def get_upload_url(vk_token, vk_group_id):
    params = {'v': 5.21, 'access_token': vk_token, 'group_id': vk_group_id}
    upload_url = 'https://api.vk.com/method/photos.getWallUploadServer'
    server_response = requests.get(upload_url, params=params)
    server_response.raise_for_status()
    server_data = server_response.json()['response']

    return server_data['upload_url']


def get_last_comics_num():
    last_comics_url = 'https://xkcd.com/info.0.json'
    last_comics_response = requests.get(last_comics_url)
    last_comics_response.raise_for_status()
    last_comics_data = last_comics_response.json()

    return last_comics_data['num']


def get_random_comics(random_comics_num):
    comics_url = f'https://xkcd.com/{random_comics_num}/info.0.json'
    comics_response = requests.get(comics_url)
    comics_response.raise_for_status()
    comics_data = comics_response.json()

    return comics_data


def download_image(comics_data):
    img_url = comics_data['img']
    img_response = requests.get(img_url)
    img_response.raise_for_status()
    img = f'{comics_data["num"]}.png'

    with open(img, 'wb') as file:
        file.write(img_response.content)

    return img


def upload_image(vk_token, vk_group_id, vk_upload_url, img):
    params = {'v': 5.21, 'access_token': vk_token, 'group_id': vk_group_id}

    with open(img, 'rb') as file:
        url = vk_upload_url
        files = {'photo': file}
        upload_response = requests.post(url, files=files, params=params)
        upload_response.raise_for_status()
        upload_data = upload_response.json()

    return upload_data


def save_image(vk_token, vk_group_id, upload_data):
    save_params = {'server': upload_data['server'],
                   'photo': upload_data['photo'],
                   'hash': upload_data['hash'],
                   'v': 5.21,
                   'access_token': vk_token,
                   'group_id': vk_group_id
                   }
    wall_save_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    save_response = requests.post(wall_save_url, params=save_params)
    save_response.raise_for_status()
    save_data = save_response.json()['response'][0]

    return save_data


def post_image(vk_token, vk_group_id, comics_data, save_data):
    post_wall_params = {'attachments': [f'photo{save_data["owner_id"]}_{save_data["id"]}'],
                        'message': comics_data['alt'],
                        'from_group': 1,
                        'v': 5.21,
                        'access_token': vk_token,
                        'owner_id': -int(vk_group_id),
                        }
    post_wall_url = 'https://api.vk.com/method/wall.post'
    post_wall_response = requests.post(post_wall_url, params=post_wall_params)
    post_wall_response.raise_for_status()


def main():
    load_dotenv()
    vk_token = os.getenv('VK_TOKEN')
    vk_group_id = os.getenv('VK_GROUP_ID')

    vk_upload_url = get_upload_url(vk_token, vk_group_id)
    last_comics_num = get_last_comics_num()
    random_comics_num = random.randint(1, last_comics_num)
    comics_data = get_random_comics(random_comics_num)
    img = download_image(comics_data)
    upload_data = upload_image(vk_token, vk_group_id, vk_upload_url, img)
    save_data = save_image(vk_token, vk_group_id, upload_data)
    post_image(vk_token, vk_group_id, comics_data, save_data)
    os.remove(img)


if __name__ == '__main__':
    main()
