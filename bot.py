import telebot
from telebot import types
import time
from config import BOT_TOKEN
from parsers.ozon import OzonParser 

bot = telebot.TeleBot(BOT_TOKEN)
ozon_parser = OzonParser()

user_states = {}

class UserState:
    def __init__(self):
        self.waiting_for_query = False
        self.waiting_for_target_price = False
        self.selected_marketplace = None
        self.current_query = None
        self.selected_product = None
        self.search = False
        


def get_user_state(user_id):
    if user_id not in user_states:
        user_states[user_id] = UserState()
    return user_states[user_id]



@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    welcome_text = """
🤖 <b>Добро пожаловать в Price Tracker Bot!</b>

Я помогу вам отслеживать цены на товары и уведомлю, когда цена упадет до нужного уровня!

<b>Доступные команды:</b>
/track - Начать отслеживание цены
/my_tracks - Мои отслеживаемые товары
/search - Быстрый поиск без отслеживания
/help - Показать эту справку

<b>Как отслеживать цены:</b>
1. Используйте /track
2. Выберите маркетплейс
3. Введите название товара
4. Укажите целевую цену
5. Получайте уведомления!

🕐 <i>Проверка цен происходит каждые 30 минут</i>
    """
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML')



# функция для начала процесса отслеживания
@bot.message_handler(commands=['track'])
def start_tracking(message):
    # создаём клавиатуру
    markup = types.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)
    btn_wb = types.KeyboardButton('🟣 Wildberries')
    btn_ozon = types.KeyboardButton('🔵 Ozon')
    btn_cancel = types.KeyboardButton('❌ Отмена')
    markup.add(btn_wb,btn_ozon,btn_cancel)

    bot.send_message(
        message.chat.id,
        '🎯 <b>Отслеживание цены </b> \n Выберите маркетплейс:',
        reply_markup=markup,
        parse_mode='HTML'
    )
    state = get_user_state(message.chat.id)
    state.waiting_for_query = True
    state.waiting_for_target_price = False

# функция отслеживания комманды search
@bot.message_handler(commands=['search'])
def search_handler(message):
    state = get_user_state(message.chat.id)
    state.search = True
    bot.send_message(message.chat.id,'Введите товар для поиска')
    
    
# фунцкия Отслеживание текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    text = message.text.strip()
    state = get_user_state(user_id)

    # Быстрый поиск
    if state.search == True:
        state.search = False
        target = message.text
        if len(target) >= 3:
            bot.send_message(message.chat.id,'Идёт поиск пожалуйста подождтите🔍')
            data = ozon_parser.get_info(target=target)


            if data is not None:
                counter = 0
                for idx, row in data.head().iterrows():
                    title_short = row['title'][:70] + "..." if len(row['title']) > 70 else row['title']
                    title_short +=("\nЦена" + str(row['price']))
                    bot.send_photo(message.chat.id, row['image_url'], caption=title_short)
                    counter =+ 1
                    if counter == 5:
                        break
            else:
                bot.send_message(message.chat.id, "Ошибка при  поиске товара")

        
        
    # обработка отмены
    if text == '❌ Отмена':
        bot.send_message(user_id, '❌ Действие отменено.', reply_markup=types.ReplyKeyboardRemove())
        return
    
    
    # Этап 1: Выбор маркетплейса
    if state.waiting_for_query and not state.selected_marketplace:
        if text == '🟣 Wildberries':
            state.selected_marketplace = 'wildberries'
            marketplace_name = 'Wildberries'
            
        elif text == '🔵 Ozon':
            state.selected_marketplace = 'ozon'
            marketplace_name = 'Ozon'
            
        else:
            bot.send_message(user_id,'❌ Пожалуйста, выберите маркетплейс из кнопок.')


    # Этап 2: Ввод запроса для поиска












bot.infinity_polling()