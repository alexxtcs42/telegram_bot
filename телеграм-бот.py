import logging
import sqlite3
from random import randint
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)

TOKEN = '5128094848:AAGpLWB48dlgTlHz4uc-4OP-TASxsVvFT24'


reply_keyboard = [['/start', '/stop', '/help']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)


def ending(n):
    s = str(n)
    if len(s) > 1 and s[-2] == '1':
        return ''
    elif s[-1] == '1':
        return 'а'
    elif s[-1] in ['2', '3', '4']:
        return 'ы'
    return ''


def start(update, context):
    update.message.reply_text("Привет! Я генератор старых фильмов. Укажите жанр фильма, который хотите посмотреть",
                              reply_markup=markup)
    return 1


def stop(update, context):
    update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


def heeelp(update, context):
    update.message.reply_text("Я генератор старых фильмов. "
                              "Если вы не знаете, что посмотреть, ответьте на мои вопросы, и я вам помогу!\n "
                              "\nСписок моих команд доступен в разделе 'Меню'.\n "
                              "\nСписок доступных жанров: комедия, драма, мелодрама, детектив, документальный, ужасы, "
                              "музыка, фантастика, анимация, биография, боевик, приключения, война, семейный, триллер, "
                              "фэнтези, вестерн, мистика, короткометражный, мюзикл, исторический, нуар.\n "
                              "\nВ нашей базе данных хранятся фильмы, выпущенные в прокат с 1908 по 2012 год")


def first_response(update, context):
    context.user_data['genre'] = update.message.text
    update.message.reply_text(f"Какого года должен быть этот фильм?")
    return 2


def second_response(update, context):
    context.user_data['year'] = update.message.text
    update.message.reply_text(f"Сколько у вас времени (в минутах) на просмотр?")
    return 3


def third_response(update, context):
    context.user_data['duration'] = update.message.text
    con = sqlite3.connect("films_db.sqlite")
    cur = con.cursor()
    try:
        result = cur.execute("""SELECT * FROM films WHERE genre IN (SELECT id FROM genres WHERE title = ?) \
        and year = ? and duration <= ?""", (context.user_data['genre'], context.user_data['year'],
                                            context.user_data['duration'])).fetchall()
        film = result[randint(0, len(result) - 1)]
        update.message.reply_text(f"Фильм '{film[1]}'. \nГод выпуска: {film[2]}. \nЖанр: {context.user_data['genre']}. "
                                  f"\nПродолжительность: {film[4]} минут{ending(film[4])}. \nСсылка: "
                                  f"https://yandex.ru/video/preview/?filmId=17904833407299321438&"
                                  f"reqid=1650829464246567-2721275713056310132-vla1-5175-vla-l7-balancer-8080-BAL-6452&"
                                  f"suggest_reqid=846127536160897776194650929888710&"
                                  f"text={'+'.join(film[1].split())}+фильм+{film[2]}")
    except Exception:
        update.message.reply_text('Извините, фильма по вашему запросу не найдено в нашей базе данных')
    con.close()
    context.user_data.clear()
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(entry_points=[CommandHandler('start', start)],
                                       states={1: [MessageHandler(Filters.text & ~Filters.command,
                                                                  first_response, pass_user_data=True)],
                                               2: [MessageHandler(Filters.text & ~Filters.command,
                                                                  second_response, pass_user_data=True)],
                                               3: [MessageHandler(Filters.text & ~Filters.command,
                                                                  third_response, pass_user_data=True)]},
                                       fallbacks=[CommandHandler('stop', stop)])

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("help", heeelp))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()

