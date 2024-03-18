from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

my_profile_keyboard = InlineKeyboardMarkup(row_width=1)
edit_profile = InlineKeyboardButton("Редактировать профиль", callback_data="my_profile_edit")
delete_profile = InlineKeyboardButton("Удалить профиль", callback_data="my_profile_delete")
my_profile_keyboard.add(edit_profile, delete_profile)

profile_edit_keyboard = InlineKeyboardMarkup()
edit_name = InlineKeyboardButton("Имя", callback_data="my_profile_edit_name")
edit_age = InlineKeyboardButton("Возраст", callback_data="my_profile_edit_age")
edit_gender = InlineKeyboardButton("Пол", callback_data="my_profile_edit_gender")
edit_country = InlineKeyboardButton("Страну", callback_data="my_profile_edit_country")
edit_city = InlineKeyboardButton("Город", callback_data="my_profile_edit_city")
edit_locations = InlineKeyboardButton("Локации", callback_data="my_profile_edit_locations")
edit_bio = InlineKeyboardButton("Информацию о себе", callback_data="my_profile_edit_bio")
profile_edit_keyboard.add(edit_name, edit_age, edit_gender, edit_country, edit_city, edit_locations, edit_bio)

cancel_keyboard = ReplyKeyboardMarkup()
cancel_keyboard.add("Отмена")

gender_edit_keyboard = ReplyKeyboardMarkup()
gender_edit_keyboard.add("Мужчина", "Женщина")

delete_profile_keyboard = ReplyKeyboardMarkup()
delete_profile_keyboard.add("Да", "Нет")


my_friends_keyboard = InlineKeyboardMarkup()
friends_profiles = InlineKeyboardButton("Профили друзей", callback_data="my_friends_profiles")
add_friend = InlineKeyboardButton("Добавить друга", callback_data="my_friends_add")
delete_friend = InlineKeyboardButton("Удалить друга", callback_data="my_friends_delete")
my_friends_keyboard.row(friends_profiles)
my_friends_keyboard.add(add_friend, delete_friend)
