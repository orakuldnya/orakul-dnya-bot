import os
import requests
import google.generativeai as genai
import google.api_core.exceptions
import html # Импортируем модуль html для экранирования


# --- 1. Настройка API-ключей и идентификаторов ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Инициализация модели Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Модель Gemini успешно инициализирована: gemini-1.5-flash")
except Exception as e:
    print(f"Ошибка инициализации Gemini API: {e}")
    if BOT_TOKEN and CHANNEL_ID:
        try:
            telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": f"❌ Бот: Ошибка инициализации Gemini API: {e}"})
        except:
            pass
    exit(1)

# --- 2. Список знаков зодиака и их смайлики ---
zodiac_signs_with_emojis = {
    "Овен": "♈",
    "Телец": "♉",
    "Близнецы": "♊",
    "Рак": "♋",
    "Лев": "♌",
    "Дева": "♍",
    "Весы": "♎",
    "Скорпион": "♏",
    "Стрелец": "♐",
    "Козерог": "♑",
    "Водолей": "♒",
    "Рыбы": "♓"
}

# --- 3. Генерация гороскопов и сборка в одно сообщение ---
print("Начинаем генерацию гороскопов для всех знаков зодиака...")

all_horoscopes_text = "" # Переменная для сбора всех гороскопов
error_messages_list = [] # Список для сбора ошибок, если они произойдут

# Общий заголовок для сообщения (используем HTML для жирного шрифта)
all_horoscopes_text += "✨ <b>Ежедневный гороскоп для всех знаков зодиака:</b> ✨\n\n"
all_horoscopes_text += "Надеемся, день принесет вам удачу!\n\n"

for sign, emoji in zodiac_signs_with_emojis.items():
    # Подготовка промпта для конкретного знака
    horoscope_prompt = f"""
    Ты - мудрый астролог, который составляет ежедневный гороскоп.
    Напиши сегодняшний гороскоп для знака зодиака "{sign}".
    Он должен быть:
    - Воодушевляющим и позитивным.
    - Содержать один-два полезных совета на день.
    - Не слишком длинным, 3-4 предложений.
    - Начинаться сразу с текста гороскопа (без заголовка типа "Гороскоп для ...").
    - Пиши на русском языке.
    """

    try:
        print(f"Попытка генерации гороскопа для {sign}...")
        gemini_response = model.generate_content(horoscope_prompt)
        generated_horoscope = gemini_response.text

        # Удаляем лишние звездочки или другие символы, которые Gemini может добавить в начало/конец
        # Это не экранирование, а очистка артефактов генерации
        generated_horoscope = generated_horoscope.strip('*').strip()

        # Экранируем специальные HTML-символы в сгенерированном гороскопе
        # Это КЛЮЧЕВОЕ ИЗМЕНЕНИЕ для 400 Bad Request
        escaped_generated_horoscope = html.escape(generated_horoscope)

        print(f"Гороскоп для {sign} успешно сгенерирован Gemini.")

        # Добавляем гороскоп к общей строке
        # Используем HTML для форматирования в Telegram
        all_horoscopes_text += (
            f"{emoji} Гороскоп для <b>{sign}</b>:\n"
            f"{escaped_generated_horoscope}\n\n" # Используем экранированный текст здесь
        )

    except google.api_core.exceptions.GoogleAPICallError as e:
        print(f"Ошибка Google API для {sign}: {e}")
        # Ошибки тоже экранируем на всякий случай
        error_messages_list.append(f"❌ Ошибка Google API для <b>{sign}</b>: {html.escape(str(e))}")

    except requests.exceptions.RequestException as req_err:
        print(f"Ошибка HTTP/Connection для {sign}: {req_err}")
        error_messages_list.append(f"❌ Ошибка сети/запроса для <b>{sign}</b>: {html.escape(str(req_err))}")

    except Exception as e:
        print(f"Непредвиденная ошибка для {sign}: {e}")
        error_messages_list.append(f"❌ Непредвиденная ошибка для <b>{sign}</b>: {html.escape(str(e))}")

print("\nГенерация гороскопов для всех знаков завершена. Отправляем в Telegram...")

# --- 4. Отправка ЕДИНОГО сообщения в Telegram ---
try:
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    final_message_to_send = all_horoscopes_text

    # Если были ошибки при генерации, добавим их в конец сообщения
    if error_messages_list:
        final_message_to_send += "\n\n---\n"
        final_message_to_send += "При генерации некоторых гороскопов произошли ошибки:\n"
        final_message_to_send += "\n".join(error_messages_list)

    # ... предыдущий код ...

        # ... предыдущий код ...

    final_message_to_send = all_horoscopes_text

    # Если были ошибки при генерации, добавим их в конец сообщения
    if error_messages_list:
        final_message_to_send += "\n\n---\n"
        final_message_to_send += "При генерации некоторых гороскопов произошли ошибки:\n"
        final_message_to_send += "\n".join(error_messages_list)

    # *** ДОБАВЬТЕ ЭТУ СТРОКУ ***
    print(f"Длина сообщения, отправляемого в Telegram: {len(final_message_to_send)} символов.")
    # **************************

    telegram_payload = {
        "chat_id": CHANNEL_ID,
        "text": final_message_to_send,
        "parse_mode": "HTML"
    }
    # ... остальной код ...


    # Если были ошибки при генерации, добавим их в конец сообщения
    if error_messages_list:
        final_message_to_send += "\n\n---\n"
        final_message_to_send += "При генерации некоторых гороскопов произошли ошибки:\n"
        final_message_to_send += "\n".join(error_messages_list)

    # *** ДОБАВЬТЕ ЭТУ СТРОКУ ***
    print(f"Длина сообщения, отправляемого в Telegram: {len(final_message_to_send)} символов.")
    # **************************

    telegram_payload = {
        "chat_id": CHANNEL_ID,
        "text": final_message_to_send,
        "parse_mode": "HTML"
    }

    telegram_response = requests.post(telegram_url, json=telegram_payload)
    # ... остальной код ...


    telegram_payload = {
        "chat_id": CHANNEL_ID,
        "text": final_message_to_send,
        "parse_mode": "HTML" # Продолжаем использовать HTML
    }

    telegram_response = requests.post(telegram_url, json=telegram_payload)
    telegram_response.raise_for_status() # Проверит ошибки HTTP

    print("Единое сообщение с гороскопами успешно отправлено в Telegram!")

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP ошибка при финальной отправке в Telegram: {http_err}")
    error_message_tg = f"❌ HTTP ошибка финальной отправки в Telegram: {html.escape(str(http_err))}"
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg, "parse_mode": "HTML"})
    except Exception as tg_err:
        print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")

except requests.exceptions.RequestException as req_err:
    print(f"Неизвестная ошибка при финальной отправке (Telegram): {req_err}")
    error_message_tg = f"❌ Неизвестная ошибка финальной отправки Telegram: {html.escape(str(req_err))}"
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg, "parse_mode": "HTML"})
    except Exception as tg_err:
        print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")

except Exception as e:
    print(f"Непредвиденная ошибка при финальной отправке: {e}")
    error_message_tg = f"❌ Непредвиденная ошибка скрипта при финальной отправке: {html.escape(str(e))}"
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg, "parse_mode": "HTML"})
    except Exception as tg_err:
        print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")

print("\nСкрипт завершил работу.")