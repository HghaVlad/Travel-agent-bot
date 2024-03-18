from aiogram.dispatcher.filters.state import State, StatesGroup


class RegistrationState(StatesGroup):
    name = State()
    age = State()
    gender = State()
    country = State()
    city = State()
    locations = State()
    bio = State()
    confirm = State()


class EditProfileState(StatesGroup):
    name = State()
    age = State()
    gender = State()
    country = State()
    city = State()
    locations = State()
    bio = State()


class Profile(StatesGroup):
    delete_profile = State()
    add_friend = State()
    remove_friend = State()
    see_friends = State()
