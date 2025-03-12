import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os
import time
import requests
import os
import tempfile

# Используем переменные из config.py
TOKEN = os.getenv('TOKEN')  # Токен для бота
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')  # ID Google Таблицы
GOOGLE_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS_FILE')  # Содержимое JSON файла в виде строки
ADMIN_IDS = os.getenv('ADMIN_IDS')  # Список ID администраторов

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

# Продолжайте писать код для бота

# Контакты школы 
CONTACTS = "📞 Приемная - +7(3952)46-29-30\n📞 Бухгалтерия - +7(3952)46-52-30\n✉️ Эл.почта - school4.irk@ru\n\n📱 ВК - https://vk.com/irk.school4\n🖥 Cайт - https://sh4-irkutsk-r138.gosweb.gosuslugi.ru/?cur_cc=2873&curPos=5"

# Функция для отображения основного меню
def main_menu(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🗓 Расписание"), KeyboardButton("🔔 Звонки"))
    markup.add(KeyboardButton("📞 Контакты"))
    # Кнопка для админов
    if message.chat.id in ADMIN_IDS:
        markup.add(KeyboardButton("⚙️ Админ-панель"))
   bot.send_message(message.chat.id, "Добро пожаловать в школьный бот!\n\n🔎Здесь вы можете просматривать расписание уроков, звонков, а также воспользоваться контактами с школой.\n\n➡️Выберите действие:", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    sheet_users = sheet.worksheet("Пользователи")
    
    # Проверяем, есть ли этот пользователь уже в таблице
    existing_users = [row[0] for row in sheet_users.get_all_values()]
    if str(user_id) not in existing_users:
        sheet_users.append_row([str(user_id)])

    main_menu(message) 

@bot.message_handler(func=lambda message: message.text == "🗓 Расписание")
def choose_shift(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📕 1 смена"), KeyboardButton("📘 2 смена"))
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "Выберите смену:", reply_markup=markup)

# Обработчик для кнопки "1 смена"
@bot.message_handler(func=lambda message: message.text == "📕 1 смена")
def send_first_shift_schedule(message):
    # Здесь указываем путь к фотографии для 1 смены
    with open('snim1.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption="➡️ Расписание для 1 смены")

# Обработчик для кнопки "2 смена"
@bot.message_handler(func=lambda message: message.text == "📘 2 смена")
def send_second_shift_schedule(message):
    # Здесь указываем путь к фотографии для 2 смены
    with open('snim2.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption="➡️ Расписание для 2 смены")

# Обработчик для кнопки "⬅️ Назад"
@bot.message_handler(func=lambda message: message.text == "⬅️ Назад")
def go_back(message):
    main_menu(message)

@bot.message_handler(func=lambda message: message.text == "🔔 Звонки")
def choose_day(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📅 Пн/Чт"), KeyboardButton("📅 Сб"))
    markup.add(KeyboardButton("📅 Остальные дни"))
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "Выберите день недели:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "⬅️ Назад")
def go_back(message):
    main_menu(message)

@bot.message_handler(func=lambda message: message.text == "📅 Пн/Чт")
def get_bells_pn(message):
    bells_text = """
    📚 **Расписание звонков** для Понедельника/Четверга:
    
    **1 смена:**
    0️⃣ Классный час: 08:00 - 08:30  
    1️⃣ Урок: 08:35 - 09:15  
    2️⃣ Урок: 09:25 - 10:05  
    3️⃣ Урок: 10:15 - 10:55  
    4️⃣ Урок: 11:05 - 11:45  
    5️⃣ Урок: 11:55 - 12:35  
    6️⃣ Урок: 12:45 - 13:25   
    
    **2 смена:**
    0️⃣ Классный час: 14:00 - 14:30  
    1️⃣ Урок: 14:40 - 15:20  
    2️⃣ Урок: 15:30 - 16:10  
    3️⃣ Урок: 16:20 - 17:00 
    4️⃣ Урок: 17:05 - 17:45  
    5️⃣ Урок: 17:50 - 18:30  
    6️⃣ Урок: 18:35 - 19:15   
    """
    bot.send_message(message.chat.id, bells_text, parse_mode="Markdown")
    # Добавляем кнопку назад
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "Вернуться в главное меню?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📅 Сб")
def get_bells_sb(message):
    bells_text = """
    📚 **Расписание звонков** для Субботы:
    
    **1 смена:**   
    1️⃣ Урок: 08:00 - 08:40  
    2️⃣ Урок: 08:45 - 09:25  
    3️⃣ Урок: 09:35 - 10:15  
    4️⃣ Урок: 10:25 - 11:05  
    5️⃣ Урок: 11:15 - 11:55  
    6️⃣ Урок: 12:05 - 12:45  
    7️⃣ Урок: 12:55 - 13:35
    """
    bot.send_message(message.chat.id, bells_text, parse_mode="Markdown")
    # Добавляем кнопку назад
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "Вернуться в главное меню?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📅 Остальные дни")
def get_bells_other(message):
    bells_text = """
    📚 **Расписание звонков** для остальных дней недели:
    
    **1 смена:**
    1️⃣ Урок: 08:00 - 08:40  
    2️⃣ Урок: 08:45 - 09:25  
    3️⃣ Урок: 09:35 - 10:15  
    4️⃣ Урок: 10:25 - 11:05  
    5️⃣ Урок: 11:15 - 11:55  
    6️⃣ Урок: 12:05 - 12:45  
    7️⃣ Урок: 12:50 - 13:30  
    
    **2 смена:**
    1️⃣ Урок: 14:00 - 14:40  
    2️⃣ Урок: 14:50 - 15:30  
    3️⃣ Урок: 15:40 - 16:20  
    4️⃣ Урок: 16:30 - 17:10  
    5️⃣ Урок: 17:15 - 17:55  
    6️⃣ Урок: 18:00 - 18:40  
    7️⃣ Урок: 18:45 - 19:25
    """
    bot.send_message(message.chat.id, bells_text, parse_mode="Markdown")
    # Добавляем кнопку назад
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "Вернуться в главное меню?", reply_markup=markup)

# Функция для отображения админ-панели
def admin_panel(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📝 Создать новость"))
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "⚙️Вы в админ-панели⚙️\nЧто хотите сделать?", reply_markup=markup)

# Функция для отправки новостей
def send_news(message):
    if message.chat.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "⚠️У вас нет прав для отправки новостей⚠️")
        return

    # Отправляем запрос на ввод текста новости
    bot.send_message(message.chat.id, "➡️Введите текст события:")
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("❌ Отменить"))
    bot.send_message(message.chat.id, "Вы можете отменить создание новости c помощью клавиатуры\n'❌ Отменить'", reply_markup=markup)
    bot.register_next_step_handler(message, save_news_text)

def save_news_text(message):
    if message.text == "❌ Отменить":
        admin_panel(message)  # Возвращаемся в админ-панель
        return

    news_text = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("❌ Отменить"), KeyboardButton("Пропустить"))  # Добавляем кнопку "Отменить" для следующего шага
    bot.send_message(message.chat.id, "➡️ Отправьте изображение", reply_markup=markup)
    bot.register_next_step_handler(message, save_news_image, news_text)

def save_news_image(message, news_text):
    if message.text == "❌ Отменить":
        admin_panel(message)  # Возвращаемся в админ-панель
        return

    if message.text == "Пропустить":
        bot.send_message(message.chat.id, "➡️ Изображение пропущено\nДобавьте файл\n\n🕛 Загрузка файла может занять время, подождите")
        bot.register_next_step_handler(message, save_news_file, news_text)
        return

    if message.photo:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_path = f"news_image_{int(time.time())}.jpg"

        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.send_message(message.chat.id, "➡️ Фото получено\nДобавьте файл\n\n🕛 Загрузка файла может занять время, подождите")
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("❌ Отменить"), KeyboardButton("Пропустить"))
        #   bot.send_message(message.chat.id, "Вы можете отменить создание новости c помощью клавиатуры\n'❌ Отменить'", reply_markup=markup)
        bot.register_next_step_handler(message, save_news_file, news_text, image_path)
    else:
        bot.send_message(message.chat.id, "❌Изображение не получено\nДобавьте файл\n\n🕛 Загрузка файла может занять время, подождите")
        bot.register_next_step_handler(message, save_news_file, news_text)

def save_news_file(message, news_text, image_path=None):
    if message.text == "❌ Отменить":
        admin_panel(message)  # Возвращаемся в админ-панель
        return

    if message.text == "Пропустить":
        save_news_to_sheet(message, news_text, image_path)
        return

    if message.document:
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)

        try:
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = f"news_file_{int(time.time())}.pdf"

            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.send_message(message.chat.id, "✅ Файл сохранен! Рассылаем всем пользователям...")
            save_news_to_sheet(message, news_text, image_path, file_path)

        except requests.exceptions.RequestException as e:
            bot.send_message(message.chat.id, f"❌ Ошибка при загрузке файла: {e}")
            bot.send_message(message.chat.id, "Попробуйте отправить файл еще раз.")
            bot.register_next_step_handler(message, save_news_file, news_text, image_path)
    else:
        save_news_to_sheet(message, news_text, image_path)

def save_news_to_sheet(message, news_text, image_path=None, file_path=None):
    # Сохранение новости в Google Таблицы
    news_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    sheet_news = sheet.worksheet("Новости")
    new_row = [news_date, news_text, image_path or "", file_path or ""]
    sheet_news.append_row(new_row)

    # Отправка новости всем пользователям
    sheet_users = sheet.worksheet("Пользователи")
    user_ids = [row[0] for row in sheet_users.get_all_values()]
    
    for user_id in user_ids:
        try:
            if image_path:
                with open(image_path, 'rb') as img:
                    bot.send_photo(user_id, img, caption=news_text)
                time.sleep(1)  # Задержка, чтобы сообщения не слипались

            if file_path:
                with open(file_path, 'rb') as doc:
                    bot.send_document(user_id, doc, caption="📎 Прикрепленный файл")
                time.sleep(1)

            if not image_path and not file_path:
                bot.send_message(user_id, news_text)

        except Exception as e:
            print(f"❌ Ошибка при отправке пользователю {user_id}: {e}")

    bot.send_message(message.chat.id, "✅ Новость сохранена и отправлена всем пользователям.")

    # Возвращаем в админ-панель
    admin_panel(message)


# Обработчики команд
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    sheet_users = sheet.worksheet("Пользователи")
    
    # Проверяем, есть ли этот пользователь уже в таблице
    existing_users = [row[0] for row in sheet_users.get_all_values()]
    if str(user_id) not in existing_users:
        sheet_users.append_row([str(user_id)])

    main_menu(message)

@bot.message_handler(func=lambda message: message.text == "⚙️ Админ-панель")
def open_admin_panel(message):
    if message.chat.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "⚠️У вас нет доступа к админ-панели⚠️")
        return
    admin_panel(message)

@bot.message_handler(func=lambda message: message.text == "📝 Создать новость")
def create_news(message):
    send_news(message)

@bot.message_handler(func=lambda message: message.text == "⬅️ Назад")
def go_back(message):
    main_menu(message)

# Команды для пользователей
@bot.message_handler(func=lambda message: message.text == "📞 Контакты")
def get_contacts(message):
    bot.send_message(message.chat.id, f"Контакты школы:\n{CONTACTS}")

bot.polling(none_stop=True)
