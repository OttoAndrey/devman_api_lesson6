import os
import random

import requests
from dotenv import load_dotenv


def main():
    load_dotenv()
    vk_token = os.getenv('VK_TOKEN')
    vk_group_id = os.getenv('VK_GROUP_ID')
    vk_upload_url = os.getenv('VK_UPLOAD_URL')

    last_comics_url = 'https://xkcd.com/info.0.json'
    last_comics_response = requests.get(last_comics_url)
    last_comics_response.raise_for_status()
    last_comics_data = last_comics_response.json()
    last_comics_num = last_comics_data['num']

    random_comics_num = random.randint(1, last_comics_num)

    comics_url = f'https://xkcd.com/{random_comics_num}/info.0.json'
    comics_response = requests.get(comics_url)
    comics_response.raise_for_status()
    comics_data = comics_response.json()

    img_url = comics_data['img']
    img_response = requests.get(img_url)
    img_response.raise_for_status()
    img = f'{comics_data["num"]}.png'

    with open(img, 'wb') as file:
        file.write(img_response.content)

    params = {'v': 5.21, 'access_token': vk_token, 'group_id': vk_group_id}

    with open(img, 'rb') as file:
        url = vk_upload_url
        files = {'photo': file}
        upload_response = requests.post(url, files=files, params=params)
        upload_response.raise_for_status()
        upload_data = upload_response.json()

    save_params = {'server': upload_data['server'],
                   'photo': upload_data['photo'],
                   'hash': upload_data['hash'],
                   }
    save_params.update(params)
    wall_save_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    save_response = requests.post(wall_save_url, params=save_params)
    save_response.raise_for_status()
    save_data = save_response.json()['response'][0]

    post_wall_params = {'attachments': [f'photo{save_data["owner_id"]}_{save_data["id"]}'],
                        'message': comics_data['alt'],
                        'from_group': 1,
                        'owner_id': -int(vk_group_id),
                        }
    post_wall_params.update(params)
    post_wall_url = 'https://api.vk.com/method/wall.post'
    post_wall_response = requests.post(post_wall_url, params=post_wall_params)
    post_wall_response.raise_for_status()

    os.remove(img)


if __name__ == '__main__':
    main()
