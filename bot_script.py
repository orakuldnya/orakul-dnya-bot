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

# Делим знаки зодиака на две группы по 6
signs_group_1 = list(zodiac_signs_with_emojis.items())[0:6]
signs_group_2 = list(zodiac_signs_with_emojis.items())[6:12]

# --- 3. Функция для генерации и сбора гороскопов ---
def generate_and_assemble_horoscopes(signs_group, group_number):
    print(f"\nНачинаем генерацию гороскопов для Группы {group_number} ({len(signs_group)} знаков)...")
    
    current_horoscopes_text = ""
    current_error_messages_list = []

    # Заголовок для текущей группы
    current_horoscopes_text += f"✨ <b>Ежедневный гороскоп (Часть {group_number}/2):</b> ✨\n\n"
    
    for sign, emoji in signs_group:
        horoscope_prompt = f"""
        Ты - мудрый астролог, который составляет ежедневный гороскоп.
        Напиши сегодняшний гороскоп для знака зодиака "{sign}".
        Он должен быть:
        - Воодушевляющим и позитивным.
        - Содержать один-два полезных совета на день.
        - Не слишком длинным, 2-3 предложения. # Сохраняем это для компактности
        - Начинаться сразу с текста гороскопа (без заголовка типа "Гороскоп для ...").
        - Пиши на русском языке.
        """

        try:
            print(f"Попытка генерации гороскопа для {sign}...")
            gemini_response = model.generate_content(horoscope_prompt)
            generated_horoscope = gemini_response.text
            generated_horoscope = generated_horoscope.strip('*').strip()
            
            escaped_generated_horoscope = html.escape(generated_horoscope)

            print(f"Гороскоп для {sign} успешно сгенерирован Gemini.")

            current_horoscopes_text += (
                f"{emoji} Гороскоп для <b>{sign}</b>:\n"
                f"{escaped_generated_horoscope}\n\n"
            )

        except google.api_core.exceptions.GoogleAPICallError as e:
            print(f"Ошибка Google API для {sign}: {e}")
            current_error_messages_list.append(f"❌ Ошибка Google API для <b>{sign}</b>: {html.escape(str(e))}")

        except requests.exceptions.RequestException as req_err:
            print(f"Ошибка HTTP/Connection для {sign}: {req_err}")
            current_error_messages_list.append(f"❌ Ошибка сети/запроса для <b>{sign}</b>: {html.escape(str(req_err))}")

        except Exception as e:
            print(f"Непредвиденная ошибка для {sign}: {e}")
            current_error_messages_list.append(f"❌ Непредвиденная ошибка для <b>{sign}</b>: {html.escape(str(e))}")
    
    return current_horoscopes_text, current_error_messages_list

# --- 4. Отправка сообщений в Telegram ---

telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Группа 1
assembled_horoscopes_1, errors_1 = generate_and_assemble_horoscopes(signs_group_1, 1)
final_message_to_send_1 = assembled_horoscopes_1
if errors_1:
    final_message_to_send_1 += "\n\n---\n"
    final_message_to_send_1 += "При генерации некоторых гороскопов этой части произошли ошибки:\n"
    final_message_to_send_1 += "\n".join(errors_1)

# Добавляем финальное сообщение в конце второй части
final_message_to_send_1 += "💫 Надеемся, день принесет вам удачу!\n" # Убираем '\n' в конце, чтобы не было лишнего пробела

print(f"Длина сообщения Части 1, отправляемого в Telegram: {len(final_message_to_send_1)} символов.")

try:
    telegram_payload_1 = {
        "chat_id": CHANNEL_ID,
        "text": final_message_to_send_1,
        "parse_mode": "HTML"
    }
    telegram_response_1 = requests.post(telegram_url, json=telegram_payload_1)
    telegram_response_1.raise_for_status()
    print("Сообщение Части 1 успешно отправлено в Telegram!")
except requests.exceptions.RequestException as e:
    print(f"Ошибка отправки Части 1 в Telegram: {e}")
    error_message_tg = f"❌ Ошибка отправки Части 1 гороскопа: {html.escape(str(e))}"
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg, "parse_mode": "HTML"})
    except: pass
except Exception as e:
    print(f"Непредвиденная ошибка при отправке Части 1: {e}")
    error_message_tg = f"❌ Непредвиденная ошибка при отправке Части 1: {html.escape(str(e))}"
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg, "parse_mode": "HTML"})
    except: pass


# Группа 2
assembled_horoscopes_2, errors_2 = generate_and_assemble_horoscopes(signs_group_2, 2)
final_message_to_send_2 = assembled_horoscopes_2
if errors_2:
    final_message_to_send_2 += "\n\n---\n"
    final_message_to_send_2 += "При генерации некоторых гороскопов этой части произошли ошибки:\n"
    final_message_to_send_2 += "\n".join(errors_2)

# Добавляем финальное сообщение в конце второй части
final_message_to_send_2 += "💫 Всего наилучшего!" # Можно изменить на другое завершение

print(f"Длина сообщения Части 2, отправляемого в Telegram: {len(final_message_to_send_2)} символов.")

try:
    telegram_payload_2 = {
        "chat_id": CHANNEL_ID,
        "text": final_message_to_send_2,
        "parse_mode": "HTML"
    }
    telegram_response_2 = requests.post(telegram_url, json=telegram_payload_2)
    telegram_response_2.raise_for_status()
    print("Сообщение Части 2 успешно отправлено в Telegram!")
except requests.exceptions.RequestException as e:
    print(f"Ошибка отправки Части 2 в Telegram: {e}")
    error_message_tg = f"❌ Ошибка отправки Части 2 гороскопа: {html.escape(str(e))}"
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg, "parse_mode": "HTML"})
    except: pass
except Exception as e:
    print(f"Непредвиденная ошибка при отправке Части 2: {e}")
    error_message_tg = f"❌ Непредвиденная ошибка при отправке Части 2: {html.escape(str(e))}"
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg, "parse_mode": "HTML"})
    except: pass

print("\nСкрипт завершил работу.")

