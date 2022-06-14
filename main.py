import logging
from PIL import Image
from io import BytesIO
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message
from config import API_TOKEN
from httpx import AsyncClient
from aiogram.types import InputFile

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

COURSE_COMMANDS = {
    "1й курс новое", "2й курс новое", "3й курс новое", "4й курс новое",
    "1й курс старое", "2й курс старое", "3й курс старое", "4й курс старое",
    "1й курс сегодня", "2й курс сегодня", "3й курс сегодня", "4й курс сегодня"
}

def main_buttons():
    button0 = types.KeyboardButton("Информация про ПДФ файлы расписания")
    button1 = types.KeyboardButton("Новое расписание")
    button2 = types.KeyboardButton("1й курс новое")
    button3 = types.KeyboardButton("2й курс новое")
    button4 = types.KeyboardButton("3й курс новое")
    button5 = types.KeyboardButton("4й курс новое")
    button6 = types.KeyboardButton("Старое расписание")
    button7 = types.KeyboardButton("1й курс старое")
    button8 = types.KeyboardButton("2й курс старое")
    button9 = types.KeyboardButton("3й курс старое")
    button10 = types.KeyboardButton("4й курс старое")
    button11 = types.KeyboardButton("1й курс сегодня")
    button12 = types.KeyboardButton("2й курс сегодня")
    button13 = types.KeyboardButton("3й курс сегодня")
    button14 = types.KeyboardButton("4й курс сегодня")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).row(
        button11, button12, button13, button14
    ).row(
        button0
    ).row(
        button1
    ).row(
        button2, button3, button4, button5
    ).row(
        button6
    ).row(
        button7, button8, button9, button10
    )
    return markup

@dp.message_handler(commands=['start'])
async def start(message: Message):
    send_message = [
        'Привет, это Эдос. Я написал телеграм бота, чтобы было легче смотреть расписания.',
        'Бот делает простые вещи - скачивает с сайта последние два расписания в формате PDF,'
        'преобразовывает в png файл и ручками производит обрезание без сложных алгоритмов.'
        'Поэтому если вдруг поменяется формат пдф файла или с ним что то не то будет, то бот сломается',
        'Для удобства есть кнопочки. Можно посмотреть полное расписание, а можно только определенного курса.'
    ]

    await bot.send_message(message.from_user.id, '\n'.join(send_message), reply_markup=main_buttons())


@dp.message_handler(content_types=['text'], text='Информация про ПДФ файлы расписания')
async def get_schedule_pdf_info(message: Message):
    try:
        async with AsyncClient() as client:
            r = await client.get(f'http://localhost:8000/get_schedule_pdf_info')
            info = r.json()
            info[0] += ' - Новое расписание'
            info[1] += ' - Старое расписание'
            send_message = "\n".join(info)
            await bot.send_message(message.from_user.id, f'Файлы:\n{send_message}')
    except Exception as e:
        await bot.send_message(message.from_user.id,
                               f'Похоже, сейчас нарезается расписание, попробуйте через пару минут.\n {e}')


async def course_schedule_newest(message: Message, course):
    try:
        async with AsyncClient() as client:
            r = await client.get(f'http://localhost:8000/get_course_schedule_newest/{course}')
            filename = f'{course}-й_курс_новое.png'

            if r.status_code != 200:
                await bot.send_message(message.from_user.id, f'Не удалось выполнить запрос. {r.json()["detail"]}')
                return

            bio = BytesIO(r.content)
            bio.name = filename
            await bot.send_photo(chat_id=message.from_user.id, photo=bio)

            document = BytesIO(r.content)
            document.name = filename
            await bot.send_document(chat_id=message.from_user.id, document=document)
    except Exception as e:
        await bot.send_message(message.from_user.id, f'Похоже, сейчас нарезается расписание, попробуйте через пару минут.\n {e}')


async def course_today_schedule(message: Message, course):
    try:
        async with AsyncClient() as client:
            r = await client.get(f'http://localhost:8000/get_today_schedule/{course}')
            filename = f'{course}-й_курс_сегодня.png'

            if r.status_code != 200:
                await bot.send_message(message.from_user.id, f'Не удалось выполнить запрос. {r.json()["detail"]}')
                return

            bio = BytesIO(r.content)
            bio.name = filename
            await bot.send_photo(chat_id=message.from_user.id, photo=bio)
    except Exception as e:
        await bot.send_message(message.from_user.id, f'Похоже, сейчас нарезается расписание, попробуйте через пару минут.\n {e}')


async def course_schedule_old(message: Message, course):
    try:
        async with AsyncClient() as client:
            r = await client.get(f'http://localhost:8000/get_course_schedule_old/{course}')
            filename = f'{course}-й_курс_старое.png'

            if r.status_code != 200:
                await bot.send_message(message.from_user.id, f'Не удалось выполнить запрос. {r.json()["detail"]}')
                return

            bio = BytesIO(r.content)
            bio.name = filename
            await bot.send_photo(chat_id=message.from_user.id, photo=bio)

            document = BytesIO(r.content)
            document.name = filename
            await bot.send_document(chat_id=message.from_user.id, document=document)

    except Exception as e:
        await bot.send_message(message.from_user.id, f'Похоже, сейчас нарезается расписание, попробуйте через пару минут.\n {e}')


@dp.message_handler(content_types=['text'], text='Новое расписание')
async def get_full_schedule_newest(message: Message):
    try:
        async with AsyncClient() as client:
            r = await client.get(f'http://localhost:8000/get_full_schedule_newest')
            filename = f'новое_расписание.png'

            if r.status_code != 200:
                await bot.send_message(message.from_user.id, f'Не удалось выполнить запрос. {r.json()["detail"]}')
                return

            bio = BytesIO(r.content)
            bio.name = filename
            await bot.send_photo(chat_id=message.from_user.id, photo=bio)

            document = BytesIO(r.content)
            document.name = filename
            await bot.send_document(chat_id=message.from_user.id, document=document)

    except Exception as e:
        await bot.send_message(message.from_user.id,
                               f'Похоже, сейчас нарезается расписание, попробуйте через пару минут.\n {e}')


@dp.message_handler(content_types=['text'], text='Старое расписание')
async def get_full_schedule_old(message: Message):
    try:
        async with AsyncClient() as client:
            r = await client.get(f'http://localhost:8000/get_full_schedule_old')
            filename = f'старое_расписание.png'

            if r.status_code != 200:
                await bot.send_message(message.from_user.id, f'Не удалось выполнить запрос. {r.json()["detail"]}')
                return

            bio = BytesIO(r.content)
            bio.name = filename
            await bot.send_photo(chat_id=message.from_user.id, photo=bio)

            document = BytesIO(r.content)
            document.name = filename
            await bot.send_document(chat_id=message.from_user.id, document=document)

    except Exception as e:
        await bot.send_message(message.from_user.id,
                               f'Похоже, сейчас нарезается расписание, попробуйте через пару минут.\n {e}')


@dp.message_handler(content_types=['text'])
async def course_schedule_request(message: Message):
    text = message.text
    if text not in COURSE_COMMANDS:
        await bot.send_message(message.from_user.id, 'Неопознанная команда.')
        return

    course = int(text[0])
    if text.find('новое') != -1:
        await course_schedule_newest(message, course)
    elif text.find('старое') != -1:
        await course_schedule_old(message, course)
    else:
        await course_today_schedule(message, course)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)