# Импортируем необходимые библиотеки
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
import gss
import re
from settings import TG_TOKEN, TG_API_URL

# функция sms будет вызвана пользователем при отправке команды start,
# внутри функции будет описана логика при ее вызове
def greeting(bot, update): # передаем экземпляр бота с помощью которого общаемся и сообщение от платформы telegram
    keyboard = ReplyKeyboardMarkup([['Get started', 'Call a human, please']], resize_keyboard=True)
    bot.message.reply_text("Hey, {}! We're happy to see you.  \n"
                            "Let's find some growing real estate locations \n"
                            "We have 12,000 locations nationwide"
                           .format(bot.message.chat.first_name), 
                           reply_markup = keyboard)
    flag_get_greeting = 1
    return flag_get_greeting

# Функция обработки нажатия кнопки "Get started"
def get_started(bot, update):
    bot.message.reply_text("Enter a city and state to check (City, State) \n"
                            "i.e.: 'Austin, Texas' or 'Fresno, CA'")
    flag_get_started = 1
    return flag_get_started


# Функция обработки нажатия кнопки "Call a human, please"
def get_call_human(bot, update):
    bot.message.reply_text("Good. At least I've tried. \n"
                            "Chat with the Team: \n"
                            "@dspv1")
    flag_get_human = 1
    return flag_get_human

# Функция обработки ситуации, когда пользователь введет что-то другое
def get_other(bot, update):
    keyboard2 = ReplyKeyboardMarkup([['Get started']], resize_keyboard=True)
    bot.message.reply_text("Sorry, I'm newbie and don't understand what you're trying to do. \n"
                            "Wish to get started?",
                            reply_markup = keyboard2)
    flag_get_other = 1
    return flag_get_other

# Создаем функцию чтения данных из Google Spread Sheets файлов
def get_info_mlp(bot, update):
    print(bot.message.text)
    zipcode = bot.message.text
    df = gss.get_df()
    dt_tmp = df.copy()
    dt_tmp = dt_tmp[dt_tmp['Zipcode'] == zipcode].reset_index()
    location = dt_tmp['Location'][0]
    trend = dt_tmp['Trend'][0]
    trend10 = dt_tmp['10-months trend forecast'][0]
    last_year_change = dt_tmp['Last year change'][0]
    stable = dt_tmp['Stable'][0]
    advice = dt_tmp['Advice'][0]
    road_png = './data/charts/' + zipcode + '.png'
    print(road_png)
    # Непосредственно сам ответ
    bot.message.reply_text('Location is: {0} \nTrend is: {1} \n'
                            '10-month trend forecast is: {2} \n'
                            'Last year change is: {3} \n'
                            'Stable is: {4} \n'
                            'Advice is: {5}'
                            .format(location, trend, trend10, last_year_change, stable, advice))
    bot.message.reply_text('Listing prices forecast:')
    update.bot.send_photo(chat_id = bot.message.chat.id, 
                            photo = open(road_png, 'rb'))
    bot.message.reply_text('Your can reach Landly Team here: @dspv1')

# Объявляем функцию main, для соединение с платформой telegram
def main():
    # Тело функции, описываем функцию (что она будет делать)
    # Создадим переменную landly_bot, с помощью которой будем взаимодействовать с нашим ботом
    landly_bot = Updater(TG_TOKEN, TG_API_URL, use_context=True)
    flag_get_greeting = 0
    flag_get_started = 0
    flag_get_human = 0
    flag_get_other = 0
    # dispather принимает от Telegram входящее сообщение
    # add_handler передает его в обработчик CommandHandler
    # CommandHandler подписанный на реагирование определенный событий выполняет след.действия:
    # Когда нажмут команду start, он переходит к вызову функции sms()
    landly_bot.dispatcher.add_handler(CommandHandler('start', greeting)) 
    landly_bot.dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'hi', re.IGNORECASE)), greeting))
    landly_bot.dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'get started', re.IGNORECASE)), get_started))
    landly_bot.dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'call a human, please', re.IGNORECASE)), get_call_human))
    if (flag_get_greeting == 1 & flag_get_started == 0 & flag_get_human == 0):
        landly_bot.dispatcher.add_handler(MessageHandler(Filters.regex(r'[a-zA-Z]'), get_other))
    
    landly_bot.dispatcher.add_handler(MessageHandler(Filters.regex(r'\d{4,5}'), get_info_mlp, 
                                        message_updates=True))
    # Проверяем о наличии сообщений с платформы telegram
    landly_bot.start_polling()
    
    # Бот будет работать пока его не остановят
    landly_bot.idle()

main()