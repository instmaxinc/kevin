import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType
import aiogram.utils.exceptions
import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import sqlalchemy
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from aiogram.types import ChatMember

# Создание базы данных и таблицы для пользователей
engine = create_engine('sqlite:///users.db')
Session = sessionmaker(bind=engine)
Base = sqlalchemy.orm.declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    
class QuizStates(StatesGroup):
    WaitingForBuyAdvertisement = State()
    WaitingForSellAdvertisement = State()
    WaitingForErrorArticle = State()
    WaitingForQuiz = State()
    MainMenu = State()
    
Base.metadata.create_all(engine)

# Создание объектов бота и диспетчера 6461948069:AAH6NWO4H7oWV0vKYPprQV5D7pYGFhGBD10
bot = Bot(token='6922708631:AAHIAfIx1DcJsUdImjJqg94hANCAoQkT4Xo')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Настройки логирования
logging.basicConfig(level=logging.INFO)
        
@dp.callback_query_handler(lambda c: c.data == 'main_menu')
async def handle_main_menu(callback_query: types.CallbackQuery):
    name = callback_query.from_user.first_name
    chat_id = callback_query.from_user.id
    text = f"🤖 Привет, *{name}*! Kevin подключен и рад помочь! " \
           f"Наверное, ты уже заметил, что я не просто бот, " \
           f"а настоящий спутник для твоих идей и запросов! 🚀\n\n" \
           f"Перед тем, как мы начнем, я должен предложить тебе подписаться на наш второй проект - [Психология игр🎮](https://t.me/+83jRZOcmq8ExNTQy). Там *Создатель* больше шутит и рассказывает про классные игры. Кевин тоже любит игры, просто обожает, ахаха! 😄\n\n" \
           f"*Я отвлекся, извини. Давай начнем. Что ты хочешь сделать сегодня?*\n\n"
           
    # Создание клавиатуры с кнопками
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("Общение с Создателем", callback_data="contact_creator"),
        InlineKeyboardButton("Реклама", callback_data="advertisement"),
        InlineKeyboardButton("Ошибка в статье", callback_data="article_error"),
        InlineKeyboardButton("Психология эволюции🛸", url="https://t.me/+YcSlaRutwHMyMzIy"),
        InlineKeyboardButton("Психология игр🎮", url="https://t.me/+83jRZOcmq8ExNTQy")
    ]
    keyboard.add(*buttons)
    # Отправка сообщения с картинкой и встроенной клавиатурой
    with open("img/pic_1.jpg", "rb") as photo:
         await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo, caption=text, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
         await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

# Проверка подписки на группы и обработка заявки на вступление
@dp.message_handler(content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
async def check_subscription_and_accept_join_request(message: types.Message):
    # Проверьте, есть ли в группах, которым должен быть подписан пользователь
    group1_chat_id = -1001667553552  # Замените на ID первой группы
    group2_chat_id = -1002065063517  # Замените на ID второй группы

    chat_member_group1 = await bot.get_chat_member(group1_chat_id, message.from_user.id)
    chat_member_group2 = await bot.get_chat_member(group2_chat_id, message.from_user.id)

    # Если пользователь подписан на обе группы, принять заявку на вступление и добавить в канал
    if chat_member_group1.status in ['administrator', 'member', 'creator'] and chat_member_group2.status in ['administrator', 'member', 'creator']:
        channel_chat_id = -1001667553552  # Замените на ID канала
        try:
            await bot.promote_chat_member(chat_id=channel_chat_id, user_id=message.from_user.id, can_change_info=False)
            await bot.send_message(chat_id=message.from_user.id, text="Ваша заявка на вступление была принята. Добро пожаловать в канал!")
        except Exception as e:
            await bot.send_message(chat_id=message.from_user.id, text="Произошла ошибка при принятии вашей заявки. Попробуйте позже.")
            
# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    # Регистрация пользователя в базе данных
    session = Session()

    existing_user = session.query(User).filter_by(id=message.from_user.id).first()

    if existing_user:
        # Пользователь уже существует в базе данных
        session.close()
        # Вы можете выполнить необходимые действия для уже существующего пользователя,
        # например, обновить его данные или пропустить добавление
    else:
        # Создание нового пользователя и добавление его в базу данных
        user = User(
            id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        session.add(user)
        session.commit()
        session.close()
    
    # Проверка подписки на группы
    group1_chat_id = -1001667553552  # Замените на ID первой группы
    group2_chat_id = -1002065063517  # Замените на ID второй группы

    chat_member_group1 = await bot.get_chat_member(group1_chat_id, message.from_user.id)
    chat_member_group2 = await bot.get_chat_member(group2_chat_id, message.from_user.id)
    text = ""
    if not (chat_member_group1.status in ['administrator', 'member', 'creator'] and chat_member_group2.status in ['administrator', 'member', 'creator']):
        # Пользователь не подписан на обе группы
        text += "\n\n⚠️ Пожалуйста, подпишитесь на оба наших проекта, чтобы получить полный доступ ко всем функциям бота! ⚠️"

    if chat_member_group1.status not in ['administrator', 'member', 'creator']:
        text += "\n\nПодпишитесь на первую группу: [Подписаться](https://t.me/+YcSlaRutwHMyMzIy)"

    if chat_member_group2.status not in ['administrator', 'member', 'creator']:
        text += "\n\nПодпишитесь на вторую группу: [Подписаться](https://t.me/+83jRZOcmq8ExNTQy)"

    # Если пользователь не подписан на обе группы, отправить сообщение с просьбой подписаться на группы
    if text != "":
        await bot.send_message(chat_id=message.from_user.id, text=text, parse_mode=types.ParseMode.MARKDOWN)
        return
    # Если пользователь подписан на обе группы, продолжаем выполнение
    name = message.from_user.first_name
    text = f"🤖 Привет, *{name}*! Kevin подключен и рад помочь! " \
           f"Наверное, ты уже заметил, что я не просто бот, " \
           f"а настоящий спутник для твоих идей и запросов! 🚀\n\n" \
           f"Перед тем, как мы начнем, я должен предложить тебе подписаться на наш второй проект - [Психология игр🎮](https://t.me/+83jRZOcmq8ExNTQy). Там *Создатель* больше шутит и рассказывает про классные игры. Кевин тоже любит игры, просто обожает, ахаха! 😄\n\n" \
           f"*Я отвлекся, извини. Давай начнем. Что ты хочешь сделать сегодня?*\n\n"

    # Создание клавиатуры с кнопками
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("Общение с Создателем", callback_data="contact_creator"),
        InlineKeyboardButton("Реклама", callback_data="advertisement"),
        InlineKeyboardButton("Ошибка в статье", callback_data="article_error"),
        InlineKeyboardButton("Психология эволюции🛸", url="https://t.me/+YcSlaRutwHMyMzIy"),
        InlineKeyboardButton("Психология игр🎮", url="https://t.me/+83jRZOcmq8ExNTQy")
    ]
    keyboard.add(*buttons)

    # Отправка сообщения с картинкой и встроенной клавиатурой
    with open("img/pic_1.jpg", "rb") as photo:
        await bot.send_photo(chat_id=message.from_user.id, photo=photo, caption=text, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@dp.callback_query_handler(lambda c: c.data == 'contact_creator')
async def return_button(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    name = callback_query.from_user.first_name
    chat_id = callback_query.from_user.id
    message_text = f'🤖 *{name}*, ты выбрал *"Общение с создателем"* и Кевин рад помочь тебе в этом!\n\n' \
                   f'_Здесь время — это нечто особенное, и разговор с_ *Создателем* _может быть как интересное размышлением вслух._\n\n' \
                   f'Чтобы сделать наше общение максимально продуктивным - *пиши одним сообщением, предварительно структурируя мысль и переходи сразу к сути.*\n\n' \
                   f'Мы запустили модуль переадресации, так что можешь начать общение. *Удачи!*😉🍸\n\n'
  
    keyboard = InlineKeyboardMarkup(row_width=1)
    get_menu_button = InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
    keyboard.add(get_menu_button)
        
    with open("img/pic_2.jpg", "rb") as photo:
         sent_message = await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo, caption=message_text, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
         # Устанавливаем состояние ожидания ответа от пользователя
         await QuizStates.WaitingForQuiz.set()
         # Сохраняем информацию о коллбэке для последующего использования
         await dp.current_state().update_data(callback_message_id=callback_query.message.message_id)
         
@dp.message_handler(lambda message: True)
async def ignore_messages(message: types.Message):
    condition = True  # Здесь можно определить условие
    if condition:
        # Вывод главного меню
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        await show_main_menu(message)
    else:
        # Обрабатываем другие сообщения или проигнорировать их (по вашему усмотрению)
        await process_other_messages(message)

async def show_main_menu(message: types.Message):
    # Отправка сообщения с главным меню
    name = message.from_user.first_name
    text = f"🤖 Привет, *{name}*! Kevin подключен и рад помочь! " \
           f"Наверное, ты уже заметил, что я не просто бот, " \
           f"а настоящий спутник для твоих идей и запросов! 🚀\n\n" \
           f"Перед тем, как мы начнем, я должен предложить тебе подписаться на наш второй проект - [Психология игр🎮](https://t.me/+83jRZOcmq8ExNTQy). Там *Создатель* больше шутит и рассказывает про классные игры. Кевин тоже любит игры, просто обожает, ахаха! 😄\n\n" \
           f"*Я отвлекся, извини. Давай начнем. Что ты хочешь сделать сегодня?*\n\n"

    # Создание клавиатуры с кнопками
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("Общение с Создателем", callback_data="contact_creator"),
        InlineKeyboardButton("Реклама", callback_data="advertisement"),
        InlineKeyboardButton("Ошибка в статье", callback_data="article_error"),
        InlineKeyboardButton("Психология эволюции🛸", url="https://t.me/+YcSlaRutwHMyMzIy"),
        InlineKeyboardButton("Психология игр🎮", url="https://t.me/+83jRZOcmq8ExNTQy")
    ]
    keyboard.add(*buttons)

    # Отправка сообщения с картинкой и встроенной клавиатурой
    with open("img/pic_1.jpg", "rb") as photo:
         await bot.send_photo(chat_id=message.from_user.id, photo=photo, caption=text, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
         await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

async def process_other_messages(message: types.Message):
    # Обработка остальных сообщений или игнорирование их
    pass
    
@dp.callback_query_handler(lambda c: c.data == 'advertisement')
async def return_button(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    name = callback_query.from_user.first_name
    chat_id = callback_query.from_user.id
    message_text = f'🤖 *{name}*, ого, мы попали в раздел "*Реклама*"! Ну что, друг, готов к бизнесу?😉\n\n' \
                       f'*Для начала выбери, что ты хочешь сделать:*\n' 
  
    # Создание клавиатуры с кнопками
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("Купить рекламу", callback_data="buyadvertisement"),
        InlineKeyboardButton("Продать рекламу", callback_data="selladvertisement"),
        InlineKeyboardButton("Вернуться в главное меню", callback_data="main_menu")
    ]
    keyboard.add(*buttons)
        
    with open("img/pic_5.jpg", "rb") as photo:
         await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo, caption=message_text, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
    
@dp.callback_query_handler(lambda c: c.data == 'article_error')
async def return_button(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    name = callback_query.from_user.first_name
    chat_id = callback_query.from_user.id
    message_text = f'🤖 Привет, остроумный искатель ошибок! Здесь Кевин, *и я хочу представить извинения от лица нашей команды за любые ошибки, которые могли появиться в наших статьях.* Помни, что посты и факт-чек делают люди, и у них, конечно же, есть _человеческий фактор._\n\n' \
                   f'_Если бы Kevin делал эту работу - ошибок не было бы точно, ведь у меня нет человеческого фактора!_ 🤣\n\n' \
                   f'🤖 Если ты нашел *ошибку в статье, не стесняйся прислать отрывок с ошибкой*. А *если речь идет о неточности в факте, предоставь пожалуйста ссылку на источник, которая подтвердит это*. Мы ценим твою внимательность и готовы сделать наши статьи еще лучше благодаря твоей помощи! 🚀\n\n'
  
    keyboard = InlineKeyboardMarkup(row_width=1)
    get_menu_button = InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
    keyboard.add(get_menu_button)
        
    with open("img/pic_8.jpg", "rb") as photo:
         await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo, caption=message_text, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
         # Устанавливаем состояние ожидания ответа от пользователя
         await QuizStates.WaitingForErrorArticle.set()
         # Сохраняем информацию о коллбэке для последующего использования
         await dp.current_state().update_data(callback_message_id=callback_query.message.message_id)
        
@dp.callback_query_handler(lambda c: c.data == 'buyadvertisement')
async def return_button(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    name = callback_query.from_user.first_name
    chat_id = callback_query.from_user.id
    message_text = f'🤑 *{name}*, _кто-то захотел увеличить количество своих подписчиков или продать свой продукт, хехе, что ж, ты обратился по адресу - наши подписчики это самые осознанные и платежеспособные люди на всей вселенной!_\n\n' \
                   f'🤖 *{name}*, при всем уважение, перед отправкой твоего предложения я должен тебя предупредить заранее, если ты хочешь получить ответ - *пожалуйста пиши все одним сообщением и отвечай на каждый вопрос по пунктам и по факту*, _это гарантирует ответ:_\n\n' \
                   f'*1) Ссылка вашего канала/продукта*\n' \
                   f'*2) Ссылка на телеметр вашего канала*\n' \
                   f'*3) Рекламный креатив ( если отсутствует, обязательно укажи это - мы можем написать его сами, за отдельную плату)*\n' \
                   f'*4) За какую цену ты хочешь приобрести рекламу?*💼\n\n' \
                   f'P.S. наш канал продает рекламу только качественным каналам и продуктам, которые мы могли бы читать/использовать сами\n\n'
  
    keyboard = InlineKeyboardMarkup(row_width=1)
    get_menu_button = InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
    keyboard.add(get_menu_button)
        
    with open("img/pic_6.jpg", "rb") as photo:
         await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo, caption=message_text, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
         # Устанавливаем состояние ожидания ответа от пользователя
         await QuizStates.WaitingForBuyAdvertisement.set()
         # Сохраняем информацию о коллбэке для последующего использования
         await dp.current_state().update_data(callback_message_id=callback_query.message.message_id)
        
@dp.callback_query_handler(lambda c: c.data == 'selladvertisement')
async def return_button(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    name = callback_query.from_user.first_name
    chat_id = callback_query.from_user.id
    message_text = f'💸 *{name}*, кто-то хочет заработать биовыживательные бумажки, хехе, Kevin уважает это!\n\n' \
                   f'🤖 *{name}*, при всем упомянутом уважение, перед отправкой твоего предложения - __я должен предупредить заранее:__\n\n' \
                   f'*1) Наш канал ни в коем случае не покупает рекламу у мошенников/каперов/закрытых каналов, развитых байт постом/накрученных ботами/каналы с сомнительным контентом*, перед предложением - подумай, наша команда экспертов всегда проверяет каналы на все эти пункты, а так же каналы, которым канал продавал рекламу, пожалуйста не трать наше время в этом случае, *спасибо!*❤️\n\n🔥2) Если ты хочешь получить ответ - *пожалуйста пиши все одним сообщением и отвечай на каждый вопрос по пунктам и по факту*, _это гарантирует ответ:_\n\n' \
                   f'*1) Ссылка на канал*\n' \
                   f'*2) Ссылка канала на телеметр*\n' \
                   f'*3) Цена CPM, если выше рыночной - то почему?*\n' \
                   f'*4) Количество охватов 24 часа*\n' \
                   f'*5) ER 24 часа*\n' \
                   f'*6) Будут ли закупы у канала? Если да – конкретные даты и время.*\n' \
                   f'*7) Статистика канал плюсовая?*\n\n'
                   
    keyboard = InlineKeyboardMarkup(row_width=1)
    get_menu_button = InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
    keyboard.add(get_menu_button)
        
    with open("img/pic_10.jpg", "rb") as photo:
         sent_message = await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo, caption=message_text, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
         # Устанавливаем состояние ожидания ответа от пользователя
         await QuizStates.WaitingForSellAdvertisement.set()
         # Сохраняем информацию о коллбэке для последующего использования
         await dp.current_state().update_data(callback_message_id=callback_query.message.message_id)
    
message_count = {}
previous_message_id = {}
# Обработчик текстовых сообщений пользователя в состоянии ожидания ответа
@dp.message_handler(state=QuizStates.WaitingForQuiz)
async def handle_user_response(message: types.Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    # Получаем сохраненные данные о коллбэке
    await QuizStates.WaitingForQuiz.set()
    data = await state.get_data()
    callback_message_id = data.get('callback_message_id')
    global sent_message  # Определение переменной как глобальной
    
    chat_id = message.chat.id

    if chat_id not in message_count:
        message_count[chat_id] = 1
    else:
        message_count[chat_id] += 1

    if chat_id in previous_message_id:
        try:
            await bot.delete_message(chat_id, previous_message_id[chat_id])
        except aiogram.utils.exceptions.MessageToDeleteNotFound:
            # Если сообщение не найдено, ничего не делаем
            pass

    if message_count[chat_id] == 1:
        # Обработка первого сообщения после ответа от Кевина
        name = message.from_user.first_name
        reply_text = f'*{ name }*, *твое сообщение доставлено*, и Кевин надеется, что там нет какого-то бреда, вроде шуток от Кевина, АХАХА😝\n\n*Создатель* в скором времени пришлет ответ👍'
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu'))
        # Отправка сообщения с картинкой и встроенной клавиатурой
        with open("img/pic_3.jpg", "rb") as photo:
             sent_message = await bot.send_photo(chat_id=message.from_user.id, photo=photo, caption=reply_text, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
             previous_message_id[chat_id] = sent_message.message_id
    elif message_count[chat_id] == 2:
        name = message.from_user.first_name
        # Обработка второго сообщения после ответа от Кевина - переход в главное меню
        reply_text = f'*Создатель не информирует меня о своих планах, если ответ до сих пор не пришел - значит он скорее всего занят*, Кевин тоже скучает по создателю...или...ты написал КАКОЙ-ТО БРЕД!? АХАХА🤣 Кевин знал, что ты такой же безбашенный шутник!'
        keyboard = InlineKeyboardMarkup(row_width=1)
        get_menu_button = InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
        keyboard.add(get_menu_button)
        
        with open("img/pic_4.jpg", "rb") as photo:
             sent_message = await bot.send_photo(chat_id=message.from_user.id, photo=photo, caption=reply_text, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
             previous_message_id[chat_id] = sent_message.message_id

    # Добавляем проверку на наличие сообщений после второго сообщения
    elif message_count[chat_id] > 2:
        # Пользователь написал после второго сообщения, переводим в главное меню
        name = message.from_user.first_name
        text = f"🤖 Привет, *{name}*! Kevin подключен и рад помочь! " \
               f"Наверное, ты уже заметил, что я не просто бот, " \
               f"а настоящий спутник для твоих идей и запросов! 🚀\n\n" \
               f"Перед тем, как мы начнем, я должен предложить тебе подписаться на наш второй проект - [Психология игр🎮](https://t.me/+83jRZOcmq8ExNTQy). Там *Создатель* больше шутит и рассказывает про классные игры. Кевин тоже любит игры, просто обожает, ахаха! 😄\n\n" \
               f"*Я отвлекся, извини. Давай начнем. Что ты хочешь сделать сегодня?*\n\n"

        # Создание клавиатуры с кнопками
        keyboard = InlineKeyboardMarkup(row_width=2)
        buttons = [
            InlineKeyboardButton("Общение с Создателем", callback_data="contact_creator"),
            InlineKeyboardButton("Реклама", callback_data="advertisement"),
            InlineKeyboardButton("Ошибка в статье", callback_data="article_error"),
            InlineKeyboardButton("Психология эволюции🛸", url="https://t.me/+YcSlaRutwHMyMzIy"),
            InlineKeyboardButton("Психология игр🎮", url="https://t.me/+83jRZOcmq8ExNTQy")
        ]
        keyboard.add(*buttons)

        # Отправка сообщения с картинкой и встроенной клавиатурой
        with open("img/pic_1.jpg", "rb") as photo:
             sent_message = await bot.send_photo(chat_id=message.from_user.id, photo=photo, caption=text, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
             previous_message_id[chat_id] = sent_message.message_id

        # Сбрасываем счетчик сообщений
        message_count.pop(chat_id)
        await state.finish()

    else:
        # Обработка остальных сообщений
        name = message.from_user.first_name
        reply_text = f'Ой, я не знаю, что сказать на это... Может, тебе нужно перейти в главное меню? 😉'
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu'))
        sent_message = await bot.send_message(message.chat.id, reply_text, reply_markup=keyboard, parse_mode=types.ParseMode.MARKDOWN)
        previous_message_id[chat_id] = sent_message.message_id
        
# Реклама покупка  
# Обработчик текстовых сообщений пользователя в состоянии ожидания ответа
@dp.message_handler(state=QuizStates.WaitingForBuyAdvertisement)
async def handle_user_response(message: types.Message, state: FSMContext):
    # Получаем сохраненные данные о коллбэке
    await QuizStates.WaitingForBuyAdvertisement.set()
    data = await state.get_data()
    callback_message_id = data.get('callback_message_id')

    # Отправляем ответ от бота
    reply_message = f"🤖*Сообщение отправлено!* *Cоздатель* свяжется с тобой в скором времени, конечно же если ты написал все согласно пунктам😊"
    keyboard = InlineKeyboardMarkup(row_width=1)
    get_menu_button = InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
    keyboard.add(get_menu_button)
    
    await state.finish()
    
    with open("img/pic_7.jpg", "rb") as photo:
        await bot.send_photo(chat_id=message.from_user.id, photo=photo, caption=reply_message, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await dp.current_state().set_state(QuizStates.MainMenu)
    
# Реклама продажа
# Обработчик текстовых сообщений пользователя в состоянии ожидания ответа
@dp.message_handler(state=QuizStates.WaitingForSellAdvertisement)
async def handle_user_response(message: types.Message, state: FSMContext):
    # Получаем сохраненные данные о коллбэке
    await QuizStates.WaitingForSellAdvertisement.set()
    data = await state.get_data()
    callback_message_id = data.get('callback_message_id')

    # Отправляем ответ от бота
    reply_message = f"🤖*Сообщение отправлено!* *Cоздатель* свяжется с тобой в скором времени, конечно же если ты написал все согласно пунктам😊"
    keyboard = InlineKeyboardMarkup(row_width=1)
    get_menu_button = InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
    keyboard.add(get_menu_button)
    
    with open("img/pic_9.jpg", "rb") as photo:
        await bot.send_photo(chat_id=message.from_user.id, photo=photo, caption=reply_message, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await state.finish()
    await dp.current_state().set_state(QuizStates.MainMenu)
    
# Ошибки в статье - сценарий 
# Обработчик текстовых сообщений пользователя в состоянии ожидания ответа
@dp.message_handler(state=QuizStates.WaitingForErrorArticle)
async def handle_user_response(message: types.Message, state: FSMContext):
    # Получаем сохраненные данные о коллбэке
    await QuizStates.WaitingForErrorArticle.set()
    data = await state.get_data()
    callback_message_id = data.get('callback_message_id')

    # Отправляем ответ от бота
    reply_message = f"🤖 Kevin выражает тебе любовь от всего процессора, спасибо за твою помощь! *Ты настоящий герой, мы искренне благодарны за то что Ты помогаешь сделать наши статьи более точными и правильными* 💖"
    keyboard = InlineKeyboardMarkup(row_width=1)
    get_menu_button = InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
    keyboard.add(get_menu_button)
    
    with open("img/pic_11.jpg", "rb") as photo:
        await bot.send_photo(chat_id=message.from_user.id, photo=photo, caption=reply_message, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await state.finish()
    await dp.current_state().set_state(QuizStates.MainMenu)
    
# Возврат в меню  
# Обработчик текстовых сообщений пользователя в состоянии ожидания ответа
@dp.message_handler(state=QuizStates.MainMenu)
async def handle_user_response(message: types.Message, state: FSMContext):
    # Получаем сохраненные данные о коллбэке
    await QuizStates.MainMenu.set()
    data = await state.get_data()
    callback_message_id = data.get('callback_message_id')

    # Пользователь написал после второго сообщения, переводим в главное меню
    name = message.from_user.first_name
    text = f"🤖 Привет, *{name}*! Kevin подключен и рад помочь! " \
           f"Наверное, ты уже заметил, что я не просто бот, " \
           f"а настоящий спутник для твоих идей и запросов! 🚀\n\n" \
           f"Перед тем, как мы начнем, я должен предложить тебе подписаться на наш второй проект - [Психология игр🎮](https://t.me/+83jRZOcmq8ExNTQy). Там *Создатель* больше шутит и рассказывает про классные игры. Кевин тоже любит игры, просто обожает, ахаха! 😄\n\n" \
           f"*Я отвлекся, извини. Давай начнем. Что ты хочешь сделать сегодня?*\n\n"

    # Создание клавиатуры с кнопками
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("Общение с Создателем", callback_data="contact_creator"),
        InlineKeyboardButton("Реклама", callback_data="advertisement"),
        InlineKeyboardButton("Ошибка в статье", callback_data="article_error"),
        InlineKeyboardButton("Психология эволюции🛸", url="https://t.me/+YcSlaRutwHMyMzIy"),
        InlineKeyboardButton("Психология игр🎮", url="https://t.me/+83jRZOcmq8ExNTQy")
    ]
    keyboard.add(*buttons)

    # Отправка сообщения с картинкой и встроенной клавиатурой
    with open("img/pic_1.jpg", "rb") as photo:
         await bot.send_photo(chat_id=message.from_user.id, photo=photo, caption=text, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
         await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
         # Сбрасываем состояние
         await state.finish()
         
         
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'main_menu', state='*')
async def handle_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    # Ваш код для обработки нажатия на кнопку "Вернуться в главное меню"
    # Например, завершите состояние ожидания ответа:
    await state.finish()
    # Отправьте сообщение и кнопки главного меню:
    name = callback_query.from_user.first_name
    chat_id = callback_query.from_user.id
    text = f"🤖 Привет, *{name}*! Kevin подключен и рад помочь! " \
           f"Наверное, ты уже заметил, что я не просто бот, " \
           f"а настоящий спутник для твоих идей и запросов! 🚀\n\n" \
           f"Перед тем, как мы начнем, я должен предложить тебе подписаться на наш второй проект - [Психология игр🎮](https://t.me/+83jRZOcmq8ExNTQy). Там *Создатель* больше шутит и рассказывает про классные игры. Кевин тоже любит игры, просто обожает, ахаха! 😄\n\n" \
           f"*Я отвлекся, извини. Давай начнем. Что ты хочешь сделать сегодня?*\n\n"
    # Создание клавиатуры с кнопками
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("Общение с Создателем", callback_data="contact_creator"),
        InlineKeyboardButton("Реклама", callback_data="advertisement"),
        InlineKeyboardButton("Ошибка в статье", callback_data="article_error"),
        InlineKeyboardButton("Психология эволюции🛸", url="https://t.me/+YcSlaRutwHMyMzIy"),
        InlineKeyboardButton("Психология игр🎮", url="https://t.me/+83jRZOcmq8ExNTQy")
    ]
    keyboard.add(*buttons)
    # Отправка сообщения с картинкой и встроенной клавиатурой
    with open("img/pic_1.jpg", "rb") as photo:
         await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo, caption=text, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
         await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
         
# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)