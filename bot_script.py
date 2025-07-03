import os
from telegram import Bot
from openai import OpenAI
from datetime import datetime

BOT_TOKEN = os.environ['BOT_TOKEN']
CHANNEL_ID = os.environ['CHANNEL_ID']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_horoscope():
    prompt = (
        "Напиши мистический гороскоп на сегодня для 12 знаков зодиака. "
        "Каждый знак — отдельный абзац. Стиль: эзотерика, любовь, успех. "
        "Текст должен быть универсальным и немного загадочным."
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=1,
        max_tokens=1000
    )
    return response.choices[0].message.content

def main():
    bot = Bot(token=BOT_TOKEN)
    horoscope_text = generate_horoscope()
    image_url = "https://images.unsplash.com/photo-1607746882042-944635dfe10e"

    try:
        bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=horoscope_text[:1024])
        print(f"{datetime.now()}: Гороскоп успешно отправлен.")
    except Exception as e:
        print("Ошибка при отправке гороскопа:", e)

if __name__ == "__main__":
    main()