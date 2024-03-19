from sqlalchemy import create_engine, Integer, VARCHAR, ARRAY, TIMESTAMP, Date, ForeignKey, Table, Column
from sqlalchemy.orm import declarative_base, mapped_column, relationship
from datetime import datetime

engine = create_engine("postgresql://postgres:postgrespw@localhost:55000/postgres")

Base = declarative_base()


association_table = Table(
    "user_journey",
    Base.metadata,
    Column("user_id", ForeignKey("User.id"), primary_key=True),
    Column("journey_id", ForeignKey("Journey.id"), primary_key=True),
)

friendship = Table(
    'friendships', Base.metadata,
    Column('friend_a_id', Integer, ForeignKey('User.id'), primary_key=True),
    Column('friend_b_id', Integer, ForeignKey('User.id'), primary_key=True)
)


class User(Base):
    __tablename__ = "User"
    id = mapped_column("id", Integer, primary_key=True)
    telegram_id = mapped_column("telegram_id", VARCHAR(15), nullable=False)
    name = mapped_column("name", VARCHAR(50))
    age = mapped_column("age", Integer)
    gender = mapped_column("gender", VARCHAR(1))  # F/M
    country = mapped_column("country", VARCHAR(50))
    city = mapped_column("city", VARCHAR(50))
    locations = mapped_column("locations", ARRAY(VARCHAR(50)))
    bio = mapped_column("bio", VARCHAR(500))
    date_joined = mapped_column("date_joined", TIMESTAMP, default=datetime.now)

    friends = relationship("User", secondary=friendship,
                           primaryjoin=id == friendship.c.friend_a_id,
                           secondaryjoin=id == friendship.c.friend_b_id,)


class Journey(Base):
    __tablename__ = "Journey"
    id = mapped_column("id", Integer, primary_key=True)
    name = mapped_column("name", VARCHAR(50))
    description = mapped_column("description", VARCHAR(200))
    user_id = mapped_column(ForeignKey("User.id"))
    user = relationship("User")
    travelers = relationship("User", secondary=association_table)
    is_public = mapped_column("is_public", Integer, default=0)
    date_created = mapped_column("date_created", TIMESTAMP, default=datetime.now)

    locations = relationship("Location", backref="Journey")


class Location(Base):
    __tablename__ = "Location"
    id = mapped_column("id", Integer, primary_key=True)
    name = mapped_column("name", VARCHAR(100))
    address = mapped_column("address", VARCHAR(300))
    start_date = mapped_column("start_date", Date)
    end_date = mapped_column("end_date", Date)
    user_id = mapped_column(ForeignKey("User.id"))
    journey_id = mapped_column(ForeignKey("Journey.id"))


class FriendRequest(Base):
    __tablename__ = "FriendRequest"
    id = mapped_column(Integer, primary_key=True)
    user_telegram_id = mapped_column("user_id", VARCHAR(15), nullable=False)
    friend_telegram_id = mapped_column("friend_id", VARCHAR(15), nullable=False)
    date_created = mapped_column("date_created", TIMESTAMP, default=datetime.now)


#Base.metadata.create_all(engine)
