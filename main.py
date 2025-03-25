import telebot
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from datetime import datetime
import time
import os
#https://aimlapi.com/app/keys/
#Основная задача -> брать последние новости (не менее 70%) с сайта и перефразировать новость и публиковать в тг канал!!!
TOKENBOT = os.getenv("TOKENBOT")
CHANNEL_ID = os.getenv("CHANNEL_ID")
URL = "https://gamerant.com/gaming/"
bot = telebot.TeleBot(TOKENBOT)
isNeedToLaunch = True
query = "первый soup объект с текстом"
###
APIAI = os.getenv("APIAI")
BASEAI = os.getenv("BASEAI")
needToAi = "paraphrase it,add one semantic emoji"
doneApi = OpenAI(api_key=APIAI, base_url=BASEAI)
###

while True:
    if datetime.now().minute in [0, 15, 30, 45] and isNeedToLaunch:
        isNeedToLaunch = False
        response = requests.get(URL)
        if response.status_code != 200:
            print(f"Error -> {response.status_code}!!!")

        soup = BeautifulSoup(response.content, 'html.parser').find('p', class_='display-card-excerpt')
        if soup and soup.get_text() != query:
            query = soup.get_text()
            soupImg = BeautifulSoup(response.content, 'html.parser').find("img", {"width":"2200", "height":"1100"})
            if soupImg:
                img = soupImg["src"]
                imgGet = requests.get(img)
                with open("img.jpg", "wb") as file:
                    file.write(imgGet.content)
            else:
                print('SoupImg Error!!!')
        else:
            print('Soup Error!!!')
            continue

        finish = doneApi.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.2",
                messages=[
                    {"role": "system", "content": needToAi},
                    {"role": "user", "content": query},
                ],
                temperature=0.7,
                max_tokens=256,
        )
        result = finish.choices[0].message.content

        with open("img.jpg", "rb") as photo:
            bot.send_photo(CHANNEL_ID, photo, caption=result)
    elif datetime.now().minute in [1, 16, 31, 46]:
        print("Не время еще... НО ПОДКРУЧУ ISNEEDTOLAUNCH В TRUE ДЛЯ ПОСЛЕДУЮЩЕГО ЗАПУСКА")
        isNeedToLaunch = True
        time.sleep(1)
    else:
        print("Не время еще...")
        time.sleep(1)