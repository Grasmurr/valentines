from aiogram import executor, types, Bot, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiosqlite
import requests

from config import Token


bot = Bot(token=Token)
dp = Dispatcher(bot=bot, storage=MemoryStorage())


class Form(StatesGroup):
    anonim = State()
    anonim_text = State()
    open = State()
    open_text = State()
    mailing = State()
    mailing_final = State()
    anonim_photo = State()
    open_photo = State()



valentinesusernmaes = {}
valentinesmessages = {}
valentinestatus = {}
format = {}
valentinesphotos = {}


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button0 = KeyboardButton("Проверить мои валентинки")
    button1 = KeyboardButton("Отправить валентинку")
    button2 = KeyboardButton("Открыточки от вашего студактива")

    markup.add(button0)
    markup.add(button1)
    markup.add(button2)

    async with aiosqlite.connect('database.db') as conn:
        cur = await conn.cursor()
        await cur.execute(
            '''CREATE TABLE IF NOT EXISTS accounts
            (username TEXT, id INT)''')
        await conn.commit()
        await cur.execute(f'SELECT * FROM accounts WHERE username = ?', (message.from_user.username.lower(),))
        rows = await cur.fetchall()
        rows = [list(i) for i in rows]
        if not rows:

            await cur.execute("""INSERT OR IGNORE INTO accounts (username, id) 
                            VALUES (?, ?)""", (message.from_user.username.lower(), message.from_user.id,))
            await conn.commit()


    await bot.send_photo(photo=open('photos/тг1.png', 'rb'), caption=f'Привет, {message.from_user.full_name}! '
                              f'Это бот-валентинка для студентов факультета права НИУ ВШЭ. '
                              f'Через него вы можете отправить валентинку открыто или анонимно.',
                         reply_markup=markup, chat_id=message.chat.id)

@dp.message_handler(commands=['mailing'])
async def mailingtousers(message: Message):
    if message.text == '/mailing':
        await bot.send_message(chat_id=message.chat.id,
                               text='Хорошо, пришлите сообщение, которое собираетесь разослать по пользователям:')
        await Form.mailing.set()


@dp.message_handler(content_types=['text'])
async def textmessages(message: Message):
    if message.text == 'Проверить мои валентинки':
        markup = InlineKeyboardMarkup()
        button1 = InlineKeyboardButton(text='Да, я готов(а)!', callback_data='showvalentines')
        button2 = InlineKeyboardButton(text='Постой, мне нужно время..', callback_data='Cancel')

        async with aiosqlite.connect('database.db') as conn:
            cur = await conn.cursor()
            await cur.execute(f'SELECT * FROM valentines WHERE towhom = ?', ('@' + message.from_user.username.lower(),))
            rows = await cur.fetchall()
            rows = [list(i) for i in rows]

            if len(rows) == 0:
                await bot.send_message(chat_id=message.chat.id, text='К сожалению, вам еще никто не прислал валентинок...')
            else:
                markup.add(button1)
                markup.add(button2)

                await bot.send_message(chat_id=message.chat.id, text=f'Ого! Вам прислали {len(rows)} валентинку(и)! Хотите прочитать?', reply_markup=markup)

    elif message.text == 'Отправить валентинку':

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = KeyboardButton('В виде фото')
        button2 = KeyboardButton('В виде текста')
        button3 = KeyboardButton('Отмена')

        markup.add(button1, button2)
        markup.add(button3)

        await bot.send_message(chat_id=message.chat.id, text='Хорошо, вы хотите отправить фото или текст?',
                               reply_markup=markup)

    elif message.text == 'Отмена':
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        button0 = KeyboardButton("Проверить мои валентинки")
        button1 = KeyboardButton("Отправить валентинку")
        button2 = KeyboardButton("Открыточки от вашего студактива")

        markup.add(button0)
        markup.add(button1)
        markup.add(button2)

        await bot.send_message(chat_id=message.chat.id, text='Главное меню', reply_markup=markup)

    elif message.text in ['В виде фото', 'В виде текста']:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        button0 = KeyboardButton("Проверить мои валентинки")
        button1 = KeyboardButton("Отправить валентинку")
        button2 = KeyboardButton("Открыточки от вашего студактива")

        markup.add(button0)
        markup.add(button1)
        markup.add(button2)


        if message.text == 'В виде фото':
            await bot.send_message(chat_id=message.chat.id, text='Хорошо! Вы выбрали формат фото!', reply_markup=markup)
            format[message.from_user.id] = 'photo'
        else:
            await bot.send_message(chat_id=message.chat.id, text='Хорошо! Вы выбрали формат текста!', reply_markup=markup)
            format[message.from_user.id] = 'text'
        print(format)
        markup = InlineKeyboardMarkup()
        button1 = InlineKeyboardButton(text='Отправить анонимную валентинку', callback_data='anonimformat')
        button2 = InlineKeyboardButton(text='Отправить открытую валентинку', callback_data='openformat')

        markup.add(button1)
        markup.add(button2)

        await bot.send_photo(photo=open('photos/4123763.png', 'rb'),
                             caption='Теперь, пожалуйста, выберите, в каком формате вы хотите отправить валентинку'
                                    ' (Анонимная - получатель не увидит ваш username около пожелания)',
                               chat_id=message.chat.id, reply_markup=markup)

    elif message.text == 'Открыточки от вашего студактива':
        # photo_path_1 = 'photos/2023-02-13 7.11.42 AM.jpg'
        # photo_path_2 = 'photos/2023-02-13 7.11.39 AM.jpg'
        # photo_path_3 = 'photos/2023-02-13 7.11.34 AM.jpg'
        # message_1 = await bot.send_photo(chat_id=message.chat.id, photo=open(photo_path_1, 'rb'))
        # file_id_1 = message_1.photo[-1].file_id
        # message_2 = await bot.send_photo(chat_id=message.chat.id, photo=open(photo_path_2, 'rb'))
        # file_id_2 = message_2.photo[-1].file_id
        # message_3 = await bot.send_photo(chat_id=message.chat.id, photo=open(photo_path_3, 'rb'))
        # file_id_3 = message_3.photo[-1].file_id
        #
        # print(file_id_1, file_id_2, file_id_3)

        media_group = [
            types.InputMedia(media='AgACAgIAAxkDAAIDE2PpvUxqjF1TdWTbzLgWhcae5pg3AAJxwTEbTDZRSy_mifNB76kRAQADAgADeQADLgQ'),
            types.InputMedia(media='AgACAgIAAxkDAAIDFGPpvU1jcgYUQrRS_4F7_y0wAUEoAAJywTEbTDZRS-KDD-QGcPoxAQADAgADeQADLgQ'),
            types.InputMedia(media='AgACAgIAAxkDAAIDIWPpvdyRe84VQv3ZFdUhvR6Kwra3AAJzwTEbTDZRS4UEqAKR7CF5AQADAgADeQADLgQ'),
            types.InputMedia(media='AgACAgIAAxkDAAIDImPpvd1g3qfstXeysQgQXqtU_N34AAJ0wTEbTDZRS5227VqVT-7GAQADAgADeQADLgQ'),
            types.InputMedia(media='AgACAgIAAxkDAAIDI2Ppvd4E11Z06185I0Q5zLyORBuVAAJ1wTEbTDZRS6b_NBlJrHy2AQADAgADeQADLgQ'),
                       ]
        await bot.send_message(chat_id=message.chat.id,
                               text='Мы подготовили для вас несколько открыточек, '
                                    'которые вы можете прислать вместо или вместе с пожеланием:')
        await bot.send_media_group(chat_id=message.chat.id, media=media_group)


@dp.callback_query_handler(lambda c: True)
async def inline_buttons(call: types.CallbackQuery):
    req = call.data

    if req == 'anonimformat':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await bot.send_message(text='Хорошо, вы выбрали анонимный формат. '
                                    'Теперь, пожалуйста, введите @username пользователя, '
                                    'которому собираетесь отправлять валентинку. В формате @username.',
                               chat_id=call.message.chat.id)
        await Form.anonim.set()

    elif req == 'openformat':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.from_user.username:
            await bot.send_message(text='Хорошо, вы выбрали открытый формат. '
                                        'Теперь, пожалуйста, введите @username пользователя, '
                                        'которому собираетесь отправлять валентинку. В формате @username.',
                                   chat_id=call.message.chat.id)
            await Form.open.set()
        else:
            await bot.send_message(text='К сожалению, у вас в профиле не указан ваш @username.'
                                        ' Поэтому получатель не сможет увидеть его. '
                                        'Вы можете отправить анонимную валентинку или же установить @username, '
                                        'после чего ввести /start снова!',
                                   chat_id=call.message.chat.id)

    elif req in ['continueanonim', 'continueopen']:
        if format[call.from_user.id] == 'text':

            await bot.edit_message_text(message_id=call.message.message_id,
                                        chat_id=call.message.chat.id,
                                        text='Хорошо! теперь отправьте послание сюда же одним сообщением:')
            if req == 'continueanonim':
                await Form.anonim_text.set()
            else:
                await Form.open_text.set()
        else:
            await bot.edit_message_text(message_id=call.message.message_id,
                                        chat_id=call.message.chat.id,
                                        text='Хорошо! теперь отправьте фото сюда же:')
            if req == 'continueanonim':
                await Form.anonim_photo.set()
            else:
                await Form.open_photo.set()


    elif req in ['finalsendanonim', 'finalsendopen', 'continuesendingphotopen', 'continuesendanonphoto']:
        if req in ['finalsendanonim', 'finalsendopen']:
            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        message_id=call.message.message_id,
                                        text='Хорошо! Ждите! '
                                             'Как только получатель откроет валентинку, вы получите уведомление!')
        else:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=call.message.chat.id, text='Хорошо! Ждите! '
                                             'Как только получатель откроет валентинку, вы получите уведомление!')

        async with aiosqlite.connect('database.db') as conn:
            cur = await conn.cursor()
            await cur.execute(
                '''CREATE TABLE IF NOT EXISTS valentines
                (fromwho TEXT, towhom TEXT, message TEXT, open TEXT, type TEXT, fromwhoid INT)''')
            await conn.commit()

            if req == 'finalsendanonim':
                await cur.execute("""INSERT OR IGNORE INTO valentines (fromwho, towhom, message, open, type, fromwhoid)
                                            VALUES (?, ?, ?, ?, ?, ?)""",
                                  (call.from_user.username.lower(),
                                   valentinesusernmaes[call.from_user.id].lower(),
                                   valentinesmessages[call.from_user.id], 'NO', 'anonim', call.from_user.id))
                await conn.commit()
            elif req == 'finalsendopen':
                await cur.execute("""INSERT OR IGNORE INTO valentines (fromwho, towhom, message, open, type, fromwhoid)
                                                            VALUES (?, ?, ?, ?, ?, ?)""",
                                  (call.from_user.username.lower(),
                                   valentinesusernmaes[call.from_user.id].lower(),
                                   valentinesmessages[call.from_user.id], 'NO', 'open', call.from_user.id))
                await conn.commit()
            elif req == 'continuesendingphotopen':
                await cur.execute("""INSERT OR IGNORE INTO valentines (fromwho, towhom, message, open, type, fromwhoid)
                                                                            VALUES (?, ?, ?, ?, ?, ?)""",
                                  (call.from_user.username.lower(),
                                   valentinesusernmaes[call.from_user.id].lower(),
                                   valentinesphotos[call.from_user.id], 'NO', 'openphoto', call.from_user.id))
                await conn.commit()
            elif req == 'continuesendanonphoto':
                await cur.execute("""INSERT OR IGNORE INTO valentines (fromwho, towhom, message, open, type, fromwhoid)
                                                                                            VALUES (?, ?, ?, ?, ?, ?)""",
                                  (call.from_user.username.lower(),
                                   valentinesusernmaes[call.from_user.id].lower(),
                                   valentinesphotos[call.from_user.id], 'NO', 'anonphoto', call.from_user.id))
                await conn.commit()


            try:
                await cur.execute(f'SELECT * FROM accounts WHERE username = ?', (valentinesusernmaes[call.from_user.id][1:].lower(),))
                row = await cur.fetchall()
                rows = [list(i) for i in row][0]
                if rows:
                    await bot.send_message(chat_id=rows[1], text='Вам прислали валентинку! Нажмите кнопку "Проверить мои валентинки", чтобы открыть ее!')
            except Exception as E:
                pass

    elif req[-22:] == 'finalthemessagingstage':
        async with aiosqlite.connect('database.db') as conn:
            cur = await conn.cursor()
            await cur.execute(f'''SELECT * FROM accounts''', )
            rows = await cur.fetchall()
            rows = [list(i) for i in rows]
            users = [i[1] for i in rows]

            for i in users:
                await bot.send_message(text=message_to_send_as_mailing, chat_id=i)
        await bot.edit_message_text(chat_id=call.message.chat.id, text='Успешно!', message_id=call.message.message_id)

    elif req == 'showvalentines':
        async with aiosqlite.connect('database.db') as conn:
            cur = await conn.cursor()
            await cur.execute(f'SELECT * FROM valentines WHERE towhom = ?', ('@' + call.from_user.username.lower(),))
            rows = await cur.fetchall()
            rows = [list(i) for i in rows]

            for i in rows:
                if i[0]:
                    fromwhom = 'Анонимная' if i[4] in ['anonim', 'anonphoto'] else '@' + i[0]
                    if i[4] in ['anonphoto', 'openphoto']:
                        await bot.send_photo(photo=open(i[2], 'rb'), chat_id=call.message.chat.id, caption=f'От: {fromwhom}')
                    else:
                        await bot.send_message(chat_id=call.message.chat.id, text=f'От: {fromwhom}\n\n{i[2]}')
                    await bot.send_message(chat_id=i[5], text=f'{i[1]} прочитал вашу валентинку!!!')
                else:
                    await bot.send_message(chat_id=call.message.chat.id, text=f'От: null\n\n{i[2]}')
            await cur.execute(f'DELETE FROM valentines WHERE towhom = ?', ('@' + call.from_user.username.lower(),))
            await conn.commit()

    elif req == 'Cancel':
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text='Хорошо! Вы можете попробовать снова!')
    elif req == 'Cancelphoto':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.message.chat.id, text='Хорошо! Вы можете попробовать снова!')
    else:
        print(req)


@dp.message_handler(state=Form.anonim)
async def anonimvalentine(message: types.Message, state: FSMContext):
    username = message.text
    if username[0] == '@':

        valentinesusernmaes[message.from_user.id] = username

        markup = InlineKeyboardMarkup()
        button1 = InlineKeyboardButton(text='Продолжить', callback_data='continueanonim')
        button2 = InlineKeyboardButton(text='Отмена', callback_data='Cancel')

        markup.add(button1)
        markup.add(button2)

        await bot.send_message(text=f'Хорошо, вы отправляете валентинку: {username}.\n\nПродолжить?',
                               chat_id=message.chat.id, reply_markup=markup)

        await state.finish()
    else:
        await bot.send_message(text=f'Кажется, это не имя пользователя. Оно должно начинаться с @. '
                                    f'Пожалуйста, попробуйте снова нажав на кнопку ниже',
                               chat_id=message.chat.id)

        await state.finish()


@dp.message_handler(state=Form.anonim_text)
async def anonimvalentinecontinue(message: types.Message, state: FSMContext):
    messagetosend = message.text


    valentinesmessages[message.from_user.id] = messagetosend

    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text='Продолжить', callback_data='finalsendanonim')
    button2 = InlineKeyboardButton(text='Отмена', callback_data='Cancel')

    markup.add(button1)
    markup.add(button2)

    await bot.send_message(text=f'Хорошо, вы отправляете валентинку: {valentinesusernmaes[message.from_user.id]} в анонимном формате'
                                f'\n\nТекст валентинки: {valentinesmessages[message.from_user.id]}',
                           chat_id=message.chat.id, reply_markup=markup)
    await state.finish()


@dp.message_handler(state=Form.open)
async def anonimvalentine(message: types.Message, state: FSMContext):
    username = message.text
    if username[0] == '@':

        valentinesusernmaes[message.from_user.id] = username

        markup = InlineKeyboardMarkup()
        button1 = InlineKeyboardButton(text='Продолжить', callback_data='continueopen')
        button2 = InlineKeyboardButton(text='Отмена', callback_data='Cancel')

        markup.add(button1)
        markup.add(button2)

        await bot.send_message(text=f'Хорошо, вы отправляете валентинку: {username}.\n\nПродолжить?',
                               chat_id=message.chat.id, reply_markup=markup)
        await state.finish()
    else:
        await bot.send_message(text=f'Кажется, это не имя пользователя. Оно должно начинаться с @. '
                                    f'Пожалуйста, попробуйте снова нажав на кнопку ниже',
                               chat_id=message.chat.id)

        await state.finish()


@dp.message_handler(state=Form.open_text)
async def anonimvalentinecontinue(message: types.Message, state: FSMContext):
    messagetosend = message.text

    valentinesmessages[message.from_user.id] = messagetosend

    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text='Продолжить', callback_data='finalsendopen')
    button2 = InlineKeyboardButton(text='Отмена', callback_data='Cancel')

    markup.add(button1)
    markup.add(button2)

    await bot.send_message(text=f'Хорошо, вы отправляете валентинку: {valentinesusernmaes[message.from_user.id]} в открытом формате'
                                f'\n\nТекст валентинки: {valentinesmessages[message.from_user.id]}',
                           chat_id=message.chat.id, reply_markup=markup)
    await state.finish()


@dp.message_handler(state=Form.mailing)
async def phone_number(message: types.Message, state: FSMContext):
    global message_to_send_as_mailing
    message_to_send_as_mailing = message.text
    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text='Продолжить', callback_data=f'finalthemessagingstage')
    button2 = InlineKeyboardButton(text='Отмена', callback_data='Cancel')
    markup.add(button1, button2)

    await bot.send_message(chat_id=message.chat.id,
                           text=f'Хорошо, вы собираетесь отправить следующее сообщение пользователям: \n\n{message_to_send_as_mailing}',
                           reply_markup=markup)

    await state.finish()

@dp.message_handler(state=Form.open_photo, content_types=['photo'])
async def save_photo(message: Message, state: FSMContext):
    global photo_path

    photo = message.photo[-1].file_id
    file = await bot.get_file(photo)
    response = requests.get(f"https://api.telegram.org/file/bot{Token}/{file.file_path}")
    with open(f"valentines_photos/{file.file_id}.jpg", "wb") as f:
        photo_path = f"valentines_photos/{file.file_id}.jpg"
        valentinesphotos[message.from_user.id] = photo_path
        f.write(response.content)

    await bot.send_message(chat_id=message.chat.id,
                           text=f'Итак, вы отправляете валентинку: {valentinesusernmaes[message.from_user.id]}'
                                f' в открытом формате. Вот так она будет выглядеть:')

    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text='Продолжить', callback_data='continuesendingphotopen')
    button2 = InlineKeyboardButton(text='Отмена', callback_data='Cancelphoto')
    markup.add(button1, button2)

    await bot.send_photo(photo=open(valentinesphotos[message.from_user.id], 'rb'),
                         chat_id=message.chat.id, caption=f'От: @{message.from_user.username}',
                         reply_markup=markup)
    await state.finish()


@dp.message_handler(state=Form.anonim_photo, content_types=['photo'])
async def save_photo(message: Message, state: FSMContext):
    global photo_path

    photo = message.photo[-1].file_id
    file = await bot.get_file(photo)
    response = requests.get(f"https://api.telegram.org/file/bot{Token}/{file.file_path}")
    with open(f"valentines_photos/{file.file_id}.jpg", "wb") as f:
        photo_path = f"valentines_photos/{file.file_id}.jpg"
        valentinesphotos[message.from_user.id] = photo_path
        f.write(response.content)

    await bot.send_message(chat_id=message.chat.id,
                           text=f'Итак, вы отправляете валентинку: {valentinesusernmaes[message.from_user.id]}'
                                f' в анонимном формате. Вот так она будет выглядеть:')

    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text='Продолжить', callback_data='continuesendanonphoto')
    button2 = InlineKeyboardButton(text='Отмена', callback_data='Cancelphoto')
    markup.add(button1, button2)

    await bot.send_photo(photo=open(valentinesphotos[message.from_user.id], 'rb'),
                         chat_id=message.chat.id, caption=f'От: Анонимная',
                         reply_markup=markup)
    await state.finish()



executor.start_polling(dp, skip_updates=True)


