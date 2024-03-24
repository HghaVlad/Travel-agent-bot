from datetime import timedelta
from sqlalchemy import create_engine, and_, update, delete, func, or_, not_
from sqlalchemy.orm import Session
from models.DBSM import User, FriendRequest, Journey, Location, Note, Task, Transaction

engine = create_engine("postgresql://postgres:postgrespw@localhost:55000/postgres")

session = Session(engine)


def get_user_name(telegram_id):
    user = session.query(User.name).filter(User.telegram_id == str(telegram_id)).first()
    return user


def get_user_telegram_id(user_id):
    return session.query(User.telegram_id).filter(User.id == user_id).first()

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
    user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
    for friend in user.friends:
        if friend.telegram_id == str(friend_telegram_id):
            return True

    return False


def is_sent_request(telegram_id, friend_telegram_id):
    seven_days_ago = func.now() - timedelta(days=7)
    r = session.query(FriendRequest.id).filter(and_(FriendRequest.user_telegram_id == str(telegram_id),
                                                    FriendRequest.friend_telegram_id == str(friend_telegram_id),
                                                    FriendRequest.date_created >= seven_days_ago)).first()
    return r


def new_friend_request(telegram_id, friend_telegram_id):
    friend_request = FriendRequest(user_telegram_id=str(telegram_id), friend_telegram_id=str(friend_telegram_id))
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
    session.delete(request)
    session.commit()
    return True


def remove_user_from_friends(telegram_id, friend_telegram_id):
    user_1 = session.query(User).filter(User.telegram_id == telegram_id).first()
    user_2 = session.query(User).filter(User.telegram_id == friend_telegram_id).first()
    user_1.friends.remove(user_2)
    user_2.friends.remove(user_1)
    session.commit()


def get_user_journeys(telegram_id):
    user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
    journeys = session.query(Journey.id).filter(Journey.user_id == user.id).all()
    friends_journeys = session.query(Journey.id).filter(
        and_(Journey.user_id.in_([user.id for user in user.friends]), Journey.is_public == True)).all()
    travelers_journeys = session.query(Journey.id).filter(and_(Journey.travelers.any(User.id == user.id), not_(
        or_(Journey.user_id == user.id,
            and_(Journey.user_id.in_([user.id for user in user.friends]), Journey.is_public == True))))).all()
    return journeys, friends_journeys, travelers_journeys


def get_journeys_by_traveller(telegram_id):
    user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
    journeys = session.query(Journey).filter(or_(Journey.user_id == user.id,
                                                 and_(Journey.user_id.in_([user.id for user in user.friends]),
                                                      Journey.is_public == True),
                                                 Journey.travelers.any(User.id == user.id))).all()
    return journeys


def make_journey(data, telegram_id):
    user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
    new_journey = Journey(name=data['name'], description=data['description'], user=user)
    session.add(new_journey)
    session.commit()
    for name, date_start, date_end, address, lon, lat in data['locations']:
        new_location = Location(name=name, address=address, start_date=date_start, end_date=date_end, user_id=user.id,
                                journey_id=new_journey.id, lon=float(lon), lat=float(lat))
        session.add(new_location)
    new_journey.travelers.append(user)
    session.commit()


def claim_journey(telegram_id, journey_id):
    journey = session.query(Journey).filter(Journey.id == journey_id).first()
    user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
    if user in journey.travelers:
        return False
    journey.travelers.append(user)
    session.commit()
    return True


def delete_friend_request(request_id):
    request = session.query(FriendRequest).filter(FriendRequest.id == request_id).first()
    session.delete(request)
    session.commit()


def add_friend_with_link(telegram_id, friend_telegram_id):
    user_1 = session.query(User).filter(User.telegram_id == telegram_id).first()
    user_2 = session.query(User).filter(User.telegram_id == friend_telegram_id).first()
    if user_1 in user_2.friends:
        return False
    user_1.friends.append(user_2)
    user_2.friends.append(user_1)
    session.commit()
    return True


def update_journey_name(journey_id, new_value):
    journey = session.query(Journey).filter(Journey.id == journey_id).first()
    journey.name = new_value
    session.commit()


def update_journey_description(journey_id, new_value):
    journey = session.query(Journey).filter(Journey.id == journey_id).first()
    journey.description = new_value
    session.commit()


def update_journey_status(journey_id, new_value):
    journey = session.query(Journey).filter(Journey.id == journey_id).first()
    journey.is_public = new_value
    session.commit()


def update_journey_locations(journey_id, locations, telegram_id):
    user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
    journey = session.query(Journey).filter(Journey.id == journey_id).first()
    for location in journey.locations:
        session.delete(location)
    for name, date_start, date_end, address, lon, lat in locations:
        new_location = Location(name=name, address=address, start_date=date_start, end_date=date_end, user_id=user.id,
                                journey_id=journey.id, lon=float(lon), lat=float(lat))
        session.add(new_location)
    session.commit()


def delete_journey(journey):
    for location in journey.locations:
        session.delete(location)
    session.commit()
    journey.travelers.clear()
    session.delete(journey)
    session.commit()


def get_notes(journey_id, telegram_id):
    user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
    notes = session.query(Note).filter(and_(Note.journey_id == journey_id, or_(Note.is_public == True, Note.user_id == user.id))).all()
    return notes


def create_note(journey_id, telegram_id, note_text, note_photo, note_file):
    user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
    newnote = Note(journey_id=journey_id, user_id=user.id, text=note_text, photo_file_id=note_photo, document_file_id=note_file)
    session.add(newnote)
    session.commit()


def change_note_public(note_id, status):
    note = session.query(Note).filter(Note.id == note_id).first()
    note.is_public = status
    session.commit()


def get_location(location_id):
    location = session.query(Location).filter(Location.id == location_id).first()
    return location


def get_tasks(journey_id, telegram_id):
    user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
    tasks = session.query(Task).filter(and_(Task.journey_id == journey_id, Task.user_id == user.id)).order_by(Task.id).all()

    return tasks


def change_status_task(task_id):
    task = session.query(Task).filter(Task.id == int(task_id)).first()
    task.is_completed = int(not(task.is_completed))
    session.commit()


def add_new_task(journey_id, telegram_id, task_name):
    user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
    task = Task(journey_id=journey_id, user_id=user.id, name=task_name)
    session.add(task)
    session.commit()


def delete_task(task_id):
    task = session.query(Task).filter(Task.id == int(task_id)).first()
    session.delete(task)
    session.commit()


def add_transaction(telegram_id, debtor_id, amount, journey_id, name):
    user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
    new_transaction = Transaction(payer_id=user.id, debtor_id=debtor_id, amount=amount, journey_id=journey_id, name=name)
    session.add(new_transaction)
    session.commit()
    return new_transaction.id


def get_user_debts(telegram_id):
    user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
    debts = session.query(Transaction).filter(Transaction.debtor_id == user.id).all()
    return debts


def settle_expense(transaction_id):
    transaction = session.query(Transaction).filter_by(id=transaction_id).first()
    transaction.is_settled = True
    session.commit()


def get_journey_users(journey_id):
    journey = session.query(Journey).filter(Journey.id == journey_id).first()
    user = journey.user
    travelers = journey.travelers
    friends = []
    if journey.is_public:
        friends = user.friends
    all_users = list(set(friends + travelers))

    return all_users


def get_user_expenses(telegram_id):
    user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
    expenses = session.query(Transaction).filter(Transaction.payer_id == user.id).order_by(Transaction.date).all()
    return expenses


def get_non_settled_expenses(telegram_id):
    user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
    expenses = session.query(Transaction).filter(Transaction.payer_id == user.id, Transaction.is_settled == False).all()
    return expenses
