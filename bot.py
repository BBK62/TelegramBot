# Импортируем необходимые библиотеки
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
import gss
from settings import TG_TOKEN, TG_API_URL

# функция sms будет вызвана пользователем при отправке команды start,
# внутри функции будет описана логика при ее вызове
def sms(bot, update): # передаем экземпляр бота с помощью которого общаемся и сообщение от платформы telegram
    bot.message.reply_text('Hey, {}! \n'
                            'Welcome to Landly Bot.\nWebsite: landly.ai\n'
                            'For more information, send me a message in the format of 4 or 5 digits (without letters)'
                           .format(bot.message.chat.first_name))

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
    # Создадим переменную landly_bot, с помощью которой будем взаимодействовать с нашим ботов
    landly_bot = Updater(TG_TOKEN, TG_API_URL, use_context=True)
    
    # dispather принимает от Telegram входящее сообщение
    # add_handler передает его в обработчик CommandHandler
    # CommandHandler подписанный на реагирование определенный событий выполняет след.действия:
    # Когда нажмут команду start, он переходит к вызову функции sms()
    landly_bot.dispatcher.add_handler(CommandHandler('start', sms)) 
    landly_bot.dispatcher.add_handler(MessageHandler(Filters.regex(r'[a-zA-Z]+'), sms))
    landly_bot.dispatcher.add_handler(MessageHandler(Filters.regex(r'\d{4,5}'), get_info_mlp, 
                                        message_updates=True))
    # Проверяем о наличии сообщений с платформы telegram
    landly_bot.start_polling()
    
    # Бот будет работать пока его не остановят
    landly_bot.idle()

main()