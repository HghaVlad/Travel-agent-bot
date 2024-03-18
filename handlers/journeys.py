from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from bot import dp
from filters import IsLogin
from base_req import get_user_journeys


@dp.message_handler(IsLogin(), lambda message: message.text == "Мои путешествия")
async def my_journeys(message: Message):
    journeys, friends_journeys = get_user_journeys(message.chat.id)
    await message.answer("<b>Ваши путешествия</b>\n\n"
                         f"<b>Вы создали</b> {len(journeys)} <b>путешествий\n"
                         f"У вас есть доступ к {len(friends_journeys)} ваших друзей")
