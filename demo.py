import json
import os
import tqdm
import requests
import re
from urllib.parse import urlparse

def get_herovoice_json(save_path):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33"}

    # 第一个请求头,需要得到[英雄的编号列表]和[英雄的名字列表]:
    herolist_json_url = 'https://pvp.qq.com/web201605/js/herolist.json'
    response1 = requests.get(url=herolist_json_url, headers=headers).text
    print(response1)
    hero_id_list = re.findall('"ename": (.+?),', response1, re.S)  # 得到英雄的编号列表(乱序的
    hero_name_list = re.findall('"cname": "(.+?)"', response1, re.S)  # 得到英雄的名字列表(乱序的
    id_name_dict = {hero_id_list[i]: hero_name_list[i] for i in range(len(hero_name_list))}
    voice_url = ["https://pvp.qq.com/zlkdatasys/yuzhouzhan/herovoice/{}.json".format(hero_id) for hero_id in hero_id_list]

    os.makedirs(save_path, exist_ok=True)
    for url in tqdm.tqdm(voice_url):
        try:
            res = requests.get(url, headers).content
            hero_id = url.split('/')[-1].split('.')[0]
            hero_name = id_name_dict[hero_id]
            save_name = hero_id + '_' +hero_name
            print(save_name)
            with open(os.path.join(save_path, save_name + '.json'), 'wb') as f:
                f.write(res)
        except OSError:
            continue

def parse_each_hero_json(json_path, save_root):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33"}
    with open(json_path, 'r', encoding='utf-8') as f:
        res = json.load(f)
    res = res["dqpfyy_5403"]
    hero_name = json_path.split('_')[-1].split('.')[0]
    print("############## hero name:", hero_name)

    def process_each_pifu(each_pifu, content):
        save_path = os.path.join(save_root, hero_name, each_pifu)
        os.makedirs(save_path, exist_ok=True)
        total_voices = content["yylbzt_9132"]
        for each_voice in tqdm.tqdm(total_voices):
            url = "https:" + each_voice['yywjzt_5304']
            label = str(each_voice['yywbzt_1517'][:-1])
            pattern = r'[^\w\s，]'

            new_label = re.sub(pattern, '', label)
            new_label = re.sub(r'\s+', ' ', new_label)
            audio_type = url.split('.')[-1]
            try:
                result = urlparse(url) # 判断url是否合法
                is_url = all([result.scheme, result.netloc])
                if is_url:
                    response = requests.get(url, headers)
                    if response.status_code == 200:
                        with open(os.path.join(save_path, new_label + '.' + audio_type), 'wb') as f:
                            f.write(response.content)

            except ConnectionError:
                continue


    if isinstance(res, dict): # 只有一个皮肤的语音
        pifu_name = res["pfmczt_7754"]
        print("########## 皮肤：", pifu_name)
        process_each_pifu(pifu_name, res)

    elif isinstance(res, list): # 多个皮肤的语音
        for i in range(len(res)):
            pifu_name = res[i]["pfmczt_7754"]
            print("########## 皮肤：", pifu_name)
            process_each_pifu(pifu_name, res[i])


if __name__ == '__main__':
    save_root = './raw_voices'
    voice_json_path = './voice_json'
    get_herovoice_json(voice_json_path)
    for name in os.listdir(voice_json_path):
        json_path = os.path.join(voice_json_path, name)
        parse_each_hero_json(json_path, save_root)
