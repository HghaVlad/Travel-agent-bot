from aiogram.dispatcher.filters import Filter
from base_req import get_user_name


class IsLogin(Filter):
    async def check(self, message) -> bool:
        user = get_user_name(message.chat.id)
        return user is not None


class IsNotLogin(Filter):
    async def check(self, message) -> bool:
        user = get_user_name(message.chat.id)
        return user is  None