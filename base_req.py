from datetime import timedelta
from sqlalchemy import create_engine, and_, update, delete, func
#from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session
from models.DBSM import User, Friend, FriendRequest

engine = create_engine("postgresql://postgres:postgrespw@localhost:55000/postgres")

session = Session(engine)


def get_user_name(telegram_id):
    user = session.query(User.name).filter(User.telegram_id == str(telegram_id)).first()
    return user


def get_user_data(telegram_id):
    user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
    return user


def make_user(data, telegram_id):
    gender = "M"
    if data['gender'] == "Женщина":
        gender = "F"
    new_user = User(
        telegram_id=str(telegram_id),
        name=data['name'],
        age=data['age'],
        gender=gender,
        country=data['country'],
        city=data['city'],
        locations=data['locations'].split(","),
        bio=data['bio']
    )
    session.add(new_user)
    session.commit()


def update_user_value(telegram_id, new_value, column):
    session.execute(update(User).where(User.telegram_id == str(telegram_id)).values({column: new_value}))
    session.commit()


def delete_user(telegram_id):
    session.execute(delete(User).where(User.telegram_id == str(telegram_id)))
    session.commit()


def get_friends(telegram_id):
    return session.query(User).filter(User.telegram_id == str(telegram_id)).first().friends


def is_friend(telegram_id, friend_telegram_id):
    user_friends = session.query(User.friends).filter(User.telegram_id == str(telegram_id)).all()
    for friend in user_friends:
        if friend.telegram_id == str(friend_telegram_id):
            return True

    return False


def is_sent_request(telegram_id, friend_telegram_id):
    seven_days_ago = func.now() - timedelta(days=7)
    r = session.query(FriendRequest.id).filter(and_(FriendRequest.user_telegram_id == str(telegram_id),
                                                       FriendRequest.friend_telegram_id == str(friend_telegram_id),
                                                       FriendRequest.date_created <= seven_days_ago)).first()
    return r


def new_friend_request(telegram_id, friend_telegram_id):
    friend_request = FriendRequest(user_telegram_id=str(telegram_id), friend_telegram_id=str(friend_telegram_id)).first()
    session.add(friend_request)
    session.commit()

    return friend_request.id


def get_friend_request(request_id):
    return session.query(FriendRequest).filter(FriendRequest.id == request_id).first()


def make_friends(request: FriendRequest):  # Костыль
    user_1 = session.query(User).filter(User.telegram_id == request.user_telegram_id).first()
    user_2 = session.query(User).filter(User.telegram_id == request.friend_telegram_id).first()
    user_1.friends.append(user_2)
    user_2.friends.append(user_1)
    session.commit()
    return True


