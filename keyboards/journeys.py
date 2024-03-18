from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

journey_menu_keyboard = InlineKeyboardMarkup(row_width=1)
see_journeys = InlineKeyboardButton("Просмотр путешествий", callback_data="journeys_see")
new_journey = InlineKeyboardButton("Создать путешествие",callback_data="journeys_new")
journey_menu_keyboard.add(see_journeys, new_journey)

see_journey_keyboard = InlineKeyboardMarkup()

new_journey_keyboard = ReplyKeyboardMarkup()
new_journey_keyboard.add("Да", "Нет")

see_journey_back = InlineKeyboardButton("⬅️", callback_data="journey_see_back")
see_journey_next = InlineKeyboardButton("➡️️", callback_data="journey_see_next")

share_journey = InlineKeyboardButton("Поделиться", callback_data="journey_share")
edit_journey = InlineKeyboardButton("Редактировать", callback_data="journey_edit")