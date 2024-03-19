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

journey_edit_keyboard = InlineKeyboardMarkup()
journey_edit_name = InlineKeyboardButton("Название", callback_data="journey_edit_name")
journey_edit_description = InlineKeyboardButton("Описание", callback_data="journey_edit_description")
journey_edit_status = InlineKeyboardButton("Статус", callback_data="journey_edit_status")
journey_edit_locations = InlineKeyboardButton("Локации", callback_data="journey_edit_locations")
journey_edit_keyboard.row(journey_edit_name, journey_edit_description)
journey_edit_keyboard.row(journey_edit_status, journey_edit_locations)

journey_edit_status_keyboard = InlineKeyboardMarkup(row_width=2)
edit_status_public = InlineKeyboardButton("Доступен друзьям", callback_data="journey_edit_status_public")
edit_status_private = InlineKeyboardButton("Приватный", callback_data="journey_edit_status_private")
journey_edit_status_keyboard.add(edit_status_public, edit_status_private)
