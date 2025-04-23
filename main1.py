import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import time
import requests
import tempfile
import os

# --- Константы ---
TOKEN = os.getenv('TOKEN')  # Токен для бота
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')  # ID Google Таблицы
GOOGLE_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS_FILE')  # Содержимое JSON файла в виде строки
ADMIN_IDS = [6916553173]  # Список ID администраторов

bot = telebot.TeleBot(TOKEN)

# Сохраняем JSON в временный файл
with tempfile.NamedTemporaryFile(delete=False) as temp_file:
    temp_file.write(GOOGLE_CREDENTIALS_JSON.encode())  # Преобразуем строку в байты и записываем
    temp_file_path = temp_file.name

# Подключение к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(temp_file_path, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID)


# --- Получение данных из таблиц ---
sheet_imgs = sheet.worksheet("РасписаниеФото")
img_records = sheet_imgs.get_all_records()
images_data = {r['Название']: r['ПутьКФайлу'] for r in img_records}

sheet_bells = sheet.worksheet("РасписаниеЗвонков")
bell_records = sheet_bells.get_all_records()
bells_data = {r['Название']: r['Текст'] for r in bell_records}

sheet_users = sheet.worksheet("Пользователи")
sheet_news = sheet.worksheet("Новости")

sheet_contacts = sheet.worksheet("Контакты")
CONTACTS = "\n".join([row[0] for row in sheet_contacts.get_all_values()])

# --- Вспомогательные функции ---

def register_user(user_id):
    existing = [row[0] for row in sheet_users.get_all_values()]
    if str(user_id) not in existing:
        sheet_users.append_row([str(user_id)])

def main_menu(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🗓 Расписание"), KeyboardButton("🔔 Звонки"))
    markup.add(KeyboardButton("📞 Контакты"))
    # Кнопка для админов
    if message.chat.id in ADMIN_IDS:
        markup.add(KeyboardButton("⚙️ Админ-панель"))
    bot.send_message(message.chat.id, "Добро пожаловать в школьный бот!\n\n🔎Здесь вы можете просматривать расписание уроков, звонков, а также воспользоваться контактами с школой.\n\n➡️Выберите действие:", reply_markup=markup)

def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file.write(response.content)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")
        return None

# --- Обработчики команд ---

@bot.message_handler(commands=['start'])
def handle_start(message):
    register_user(message.chat.id)
    main_menu(message)

@bot.message_handler(func=lambda message: message.text == "📕 1 смена")
def send_first_shift_schedule(message):
    # Используем локальный путь для изображения 1 смены
    try:
        with open('snim2.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="➡️ Расписание для 1 смены")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Не удалось загрузить расписание для 1 смены: {e}")

@bot.message_handler(func=lambda message: message.text == "📘 2 смена")
def send_second_shift_schedule(message):
    # Используем локальный путь для изображения 2 смены
    try:
        with open('snim2.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="➡️ Расписание для 2 смены")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Не удалось загрузить расписание для 2 смены: {e}")

# @bot.message_handler(func=lambda m: m.text in images_data)
# def handle_photo_schedule(message):
#     url_or_path = images_data[message.text]
#     if url_or_path.startswith("http"):
#         local_path = download_image(url_or_path)
#     else:
#         local_path = url_or_path
#     try:
#         with open(local_path, 'rb') as f:
#             bot.send_photo(message.chat.id, f, caption=f"➡️ Расписание: {message.text}")
#     except Exception as e:
#         bot.send_message(message.chat.id, f"❌ Не удалось загрузить изображение: {e}")
    

@bot.message_handler(func=lambda message: message.text == "🔔 Звонки")
def choose_day(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📅 Пн/Чт"), KeyboardButton("📅 Сб"))
    markup.add(KeyboardButton("📅 Остальные дни"))
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "Выберите день недели:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in bells_data)
def handle_send_bells(message):
    text = bells_data[message.text]
    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    

@bot.message_handler(func=lambda m: m.text == "⬅️ Назад")
def handle_back(message):
    main_menu(message)

@bot.message_handler(func=lambda m: m.text == "🗓 Расписание")
def handle_choose_schedule(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for name in images_data:
        markup.add(KeyboardButton(name))
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "Выберите нужное расписание:", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "📞 Контакты")
def handle_contacts(message):
    bot.send_message(message.chat.id, CONTACTS)

# --- Админ-панель и новости ---

def admin_panel(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📝 Создать новость"))
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "⚙️ Админ-панель:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "⚙️ Админ-панель")
def handle_admin(message):
    if message.chat.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "⚠️ Нет доступа")
        return
    admin_panel(message)

@bot.message_handler(func=lambda m: m.text == "📝 Создать новость")
def handle_create_news(message):
    if message.chat.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "⚠️ Нет прав")
        return
    bot.send_message(message.chat.id, "➡️ Введите текст новости:")
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("❌ Отменить"))
    bot.register_next_step_handler(message, save_news_text)

def save_news_text(message):
    if message.text == "❌ Отменить":
        admin_panel(message)
        return
    news_text = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Пропустить"), KeyboardButton("❌ Отменить"))
    bot.send_message(message.chat.id, "➡️ Отправьте фото или Пропустить", reply_markup=markup)
    bot.register_next_step_handler(message, save_news_image, news_text)

def save_news_image(message, news_text):
    if message.text == "❌ Отменить":
        admin_panel(message)
        return
    if message.text == "Пропустить":
        bot.send_message(message.chat.id, "➡️ Пропуск фото. Отправьте файл или Пропустить.")
        bot.register_next_step_handler(message, save_news_file, news_text, None)
        return
    if message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        data = bot.download_file(file_info.file_path)
        image_path = f"news_img_{int(time.time())}.jpg"
        with open(image_path, 'wb') as f:
            f.write(data)
        bot.send_message(message.chat.id, "➡️ Фото сохранено. Отправьте файл или Пропустить.")
        bot.register_next_step_handler(message, save_news_file, news_text, image_path)
    else:
        bot.send_message(message.chat.id, "❌ Не фото. Отправьте файл или Пропустить.")
        bot.register_next_step_handler(message, save_news_file, news_text, None)

def save_news_file(message, news_text, image_path=None):
    if message.text == "❌ Отменить":
        admin_panel(message)
        return
    file_path = None
    if message.text != "Пропустить" and message.document:
        file_info = bot.get_file(message.document.file_id)
        data = bot.download_file(file_info.file_path)
        file_path = f"news_file_{int(time.time())}.pdf"
        with open(file_path, 'wb') as f:
            f.write(data)

    sheet_news.append_row([time.strftime('%Y-%m-%d %H:%M:%S'), news_text, image_path or "", file_path or ""])

    user_ids = [r[0] for r in sheet_users.get_all_values()]
    for uid in user_ids:
        try:
            if image_path:
                with open(image_path, 'rb') as f:
                    bot.send_photo(uid, f, caption=news_text)
                time.sleep(1)
            if file_path:
                with open(file_path, 'rb') as f:
                    bot.send_document(uid, f, caption="📎 Файл")
                time.sleep(1)
            if not image_path and not file_path:
                bot.send_message(uid, news_text)
        except Exception as e:
            print(f"Ошибка отправки {uid}: {e}")
    bot.send_message(message.chat.id, "✅ Новость сохранена и разослана.")
    admin_panel(message)

# --- Запуск бота ---
if __name__ == '__main__':
    bot.polling(none_stop=True)
