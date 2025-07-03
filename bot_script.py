import os
import requests
from telegram import Bot
from datetime import datetime

BOT_TOKEN = os.environ['BOT_TOKEN']
CHANNEL_ID = os.environ['CHANNEL_ID']
HF_API_TOKEN = os.environ['HF_API_TOKEN']

def generate_horoscope():
    prompt = (
        "Напиши мистический гороскоп на сегодня для 12 знаков зодиака. "
        "Каждый знак — отдельный абзац. Стиль: эзотерика, любовь, успех. "
        "Текст должен быть универсальным и немного загадочным."
    )
    
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}"
    }

    json_data = {
        "inputs": prompt,
        "parameters": {"temperature": 0.8, "max_new_tokens": 500}
    }

    response = requests.post(
        "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct",
        headers=headers,
        json=json_data
    )

    result = response.json()
    return result[0]["generated_text"] if isinstance(result, list) else result.get("generated_text", "Ошибка генерации")

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