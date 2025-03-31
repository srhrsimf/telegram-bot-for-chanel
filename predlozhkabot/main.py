import telebot
from telebot import types
import time
from telebot.types import InputMediaPhoto
import sqlite3

bot_token = ваш токен бота
channel_id = id вашего чата для сортировки заявок
predlozhka_id = id вашго канала для "постинга" записей

bot = telebot.TeleBot(bot_token)

# Глобальные переменные для хранения данных
message_text = ''
message_document = None
message_photo = None
message_audio = None
message_video = None
message_voice = None
message_sticker = None
message_video_note = None
buf_mes = None
tag_1 = False
tag_2 = False
tag_3 = False
tag_1_cond = False
tag_2_cond = False
tag_3_cond = False
call_admin = False
last_message_time = {}
user_messages = {}
message_mapping = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Это предложка, скинь сюда свой мем или интересную историю")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton("Связть с админами")
    markup.add(btn1)

    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

    photo1 = 'D:\буфер\картиночки\аватарки\qwe.jpg'
    photo2 = 'D:\буфер\картиночки\аватарки\ewq.jpg'

    # Создаем список объектов InputMediaPhoto
    media = [
        InputMediaPhoto(photo1),
        InputMediaPhoto(photo2)
    ]

    # Отправляем медиа-группу
    bot.send_media_group(message.chat.id, media)

#@bot.message_handler(content_types=['photo'])
#def handle_photos(message):
    #photos = []
    #for photo in message.photo:
    #    file_id = photo.file_id
    #    photos.append(InputMediaPhoto((message.photo[-1].file_id)))
    #bot.send_media_group(predlozhka_id, photos)

# Отправка файлов из бота в канал
@bot.message_handler(content_types=['text','document', 'photo', 'audio', 'video', 'voice', 'sticker', 'video_note'])

def handle_files(message):
    global message_text, message_photo, message_audio, message_video, message_voice, message_sticker, message_video_note, \
        buf_mes, tag_1, tag_2, tag_3, call_admin

    if message.text == "Связть с админами":
        bot.send_message(message.chat.id, "Вы сейчас находитесь на горячей линии с админами:")
        call_admin = True

    if call_admin:
        if message.chat.type == 'private':
            current_time = time.time()
            user_id = message.from_user.id
            buf_mes = message.content_type

            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton(text="запостить", callback_data=f"post:{buf_mes}")
            button2 = types.InlineKeyboardButton(text="удалить", callback_data=f"delete:{message.from_user.id}")#{message.chat.id}_{message.message_id}
            button3 = types.InlineKeyboardButton(text="теги", callback_data=f"tags:{buf_mes}")
            markup.add(button, button2, button3)

            if user_id in last_message_time:
                if current_time - last_message_time[user_id] < 5:
                    bot.reply_to(message, "Пожалуйста, подождите 5 секунд перед отправкой следующего сообщения.")
                    return
            last_message_time[user_id] = current_time

            forwarded_message = bot.forward_message(predlozhka_id, message.chat.id, message.message_id)
            message_mapping[forwarded_message.message_id] = message.chat.id

            postscript = ''
            if message.content_type == 'text':
                message_text = message.text
            elif message.content_type == 'document':
                message_document = (message.document.file_id, message.caption if message.caption else postscript)
            elif message.content_type == 'photo':
                message_photo = (message.photo[-1].file_id, message.caption if message.caption else postscript)
            elif message.content_type == 'audio':
                message_audio = (message.audio.file_id, message.caption if message.caption else postscript)
            elif message.content_type == 'video':
                message_video = (message.video.file_id, message.caption if message.caption else postscript)
            elif message.content_type == 'voice':
                message_voice = (message.voice.file_id, message.caption if message.caption else postscript)
            elif message.content_type == 'sticker':
                message_sticker = message.sticker.file_id
            elif message.content_type == 'video_note':
                message_video_note = message.video_note.file_id
        else:
            if message.reply_to_message:
                user_chat_id = message_mapping.get(message.reply_to_message.message_id)
                if user_chat_id:
                    bot.send_message(user_chat_id, message.text)
    else:
        if message.chat.type == 'private':
            current_time = time.time()
            user_id = message.from_user.id
            buf_mes = message.content_type

            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton(text="запостить", callback_data=f"post:{buf_mes}")
            button2 = types.InlineKeyboardButton(text="удалить", callback_data=f"delete:{message.from_user.id}")#{message.chat.id}_{message.message_id}
            button3 = types.InlineKeyboardButton(text="теги", callback_data=f"tags:{buf_mes}")
            markup.add(button, button2, button3)

            if user_id in last_message_time:
                # Проверяем, прошло ли 20 секунд с момента последнего сообщения
                if current_time - last_message_time[user_id] < 20:
                    bot.reply_to(message, "Пожалуйста, подождите 20 секунд перед отправкой следующего сообщения.")
                    return

            bot.reply_to(message, "Ваше сообщение принято.")
            last_message_time[user_id] = current_time

            forwarded_message = bot.forward_message(predlozhka_id, message.chat.id, message.message_id)
            bot.send_message(predlozhka_id, "Действия", reply_markup=markup,
                             reply_to_message_id=forwarded_message.message_id)

            postscript = ''
            if message.content_type == 'text':
                message_text = message.text
                #bot.send_message(predlozhka_id, forwarded_message.text, reply_markup=markup)
            elif message.content_type == 'document':
                message_document = (message.document.file_id, message.caption if message.caption else postscript)
                #bot.send_document(chat_id=predlozhka_id, document=message_document[0], caption=message_document[1], reply_markup=markup)
            elif message.content_type == 'photo':
                message_photo = (message.photo[-1].file_id, message.caption if message.caption else postscript)
                #bot.send_photo(chat_id=predlozhka_id, photo=message_photo[0], caption=message_photo[1], reply_markup=markup)
            elif message.content_type == 'audio':
                message_audio = (message.audio.file_id, message.caption if message.caption else postscript)
                #bot.send_audio(chat_id=predlozhka_id, audio=message_audio[0], caption=message_audio[1], reply_markup=markup)
            elif message.content_type == 'video':
                message_video = (message.video.file_id, message.caption if message.caption else postscript)
                #bot.send_video(chat_id=predlozhka_id, video=message_video[0], caption=message_video[1], reply_markup=markup)
            elif message.content_type == 'voice':
                message_voice = (message.voice.file_id, message.caption if message.caption else postscript)
                #bot.send_voice(chat_id=predlozhka_id, voice=message_voice[0], caption=message_voice[1], reply_markup=markup)
            elif message.content_type == 'sticker':
                message_sticker = message.sticker.file_id
                #bot.send_sticker(chat_id=predlozhka_id, sticker=message_sticker, reply_markup=markup)
            elif message.content_type == 'video_note':
                message_video_note = message.video_note.file_id
                #bot.send_video_note(chat_id=predlozhka_id, video_note=message_video_note, reply_markup=markup)

# Обработчик callback-запросов
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    global message_text, message_document, message_photo, message_audio, message_video, message_voice, message_sticker, \
        message_video_note, buf_mes, tag_1, tag_2, tag_3, tag_1_cond, tag_2_cond, tag_3_cond
    tag_1_text = '#мемы '
    tag_2_text = '#жиза '
    tag_3_text = '#qwe '

    if call.data.startswith("post:"):
        content_type = call.data.split(":")[1]
        postscript = '\n'
        if tag_1 == True:
            if tag_1_cond == True:
                postscript += tag_1_text
        if tag_2 == True:
            if tag_2_cond == True:
                postscript += tag_2_text
        if tag_3 == True:
            if tag_3_cond == True:
                postscript += tag_3_text
        postscript += '\n\n@predl_bot'

        if content_type == 'text':
            bot.send_message(channel_id, message_text + postscript)
        elif content_type == 'document':
            bot.send_document(chat_id=channel_id, document=message_document[0], caption=message_document[1])
        elif content_type == 'photo':
            bot.send_photo(chat_id=channel_id, photo=message_photo[0], caption=message_photo[1] + postscript)
        elif content_type == 'audio':
            bot.send_audio(chat_id=channel_id, audio=message_audio[0], caption=message_audio[1] + postscript)
        elif content_type == 'video':
            bot.send_video(chat_id=channel_id, video=message_video[0], caption=message_video[1] + postscript)
        elif content_type == 'voice':
            bot.send_voice(chat_id=channel_id, voice=message_voice[0], caption=message_voice[1])
        elif content_type == 'sticker':
            bot.send_sticker(chat_id=channel_id, sticker=message_sticker)
        elif content_type == 'video_note':
            bot.send_video_note(chat_id=channel_id, video_note=message_video_note)

        new_markup = types.InlineKeyboardMarkup()
        new_button1 = types.InlineKeyboardButton("готово", callback_data='none')
        new_markup.add(new_button1)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=new_markup)

        tag_1_cond = False
        tag_2_cond = False
        tag_3_cond = False

    if call.data.startswith("delete:"):
        new_markup = types.InlineKeyboardMarkup()
        new_button1 = types.InlineKeyboardButton("удалено", callback_data='none')
        new_markup.add(new_button1)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=new_markup)

        user_id = int(call.data.split(':')[1])
        bot.send_message(user_id, "неприемлемый контент")

    if call.data.startswith("tags:"):
        new_markup = types.InlineKeyboardMarkup()
        new_button1 = types.InlineKeyboardButton("#мемы", callback_data='add_tag_mems:')
        new_button2 = types.InlineKeyboardButton("#жиза", callback_data='add_tag_zhiz:')
        new_button3 = types.InlineKeyboardButton("#фурри", callback_data='add_tag_fury:')
        new_button4 = types.InlineKeyboardButton("назад", callback_data='cancel:')

        new_markup.add(new_button1, new_button2, new_button3, new_button4)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=new_markup)

    if call.data.startswith('cancel:'):
        new_markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("запостить", callback_data=f"post:{buf_mes}")
        button2 = types.InlineKeyboardButton("удалить", callback_data=f"delete:{buf_mes}")
        button3 = types.InlineKeyboardButton("теги", callback_data=f"tags:{buf_mes}")

        new_markup.add(button1, button2, button3)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=new_markup)
    #сделать булевую переменную которая меняет кнопку "запостить" и которая будет условием для постинга документов
    #if content_type == 'text' and proccess != true:

    if call.data.startswith('add_tag_mems:'):
        tag_1 = True
        if tag_1_cond == False:
            bot.answer_callback_query(call.id, "тег мемы добавлен")
            tag_1_cond = True
        else:
            bot.answer_callback_query(call.id, "такой тег уже есть")
    if call.data.startswith('add_tag_zhiz:'):
        tag_2 = True
        if tag_2_cond == False:
            bot.answer_callback_query(call.id, "тег жиза добавлен")
            tag_2_cond = True
        else:
            bot.answer_callback_query(call.id, "такой тег уже есть")
    if call.data.startswith('add_tag_fury:'):
        tag_3 = True
        if tag_3_cond == False:
            bot.answer_callback_query(call.id, "тег qwe добавлен")
            tag_3_cond = True
        else:
            bot.answer_callback_query(call.id, "такой тег уже есть")

bot.polling(none_stop = True)