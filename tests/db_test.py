import os
import unittest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.DBSM import Base, User, Journey, Location, Note, Task, Transaction


class DBTestCase(unittest.TestCase):
    # Первоначальная настройка
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(os.getenv("DATABASE_URL", "postgresql://postgres:postgrespw@localhost:55000/postgres"))
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(cls.engine)

    def setUp(self):
        self.session = self.Session()

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    # Тесты для таблицы User
    def test_01_create_user(self):
        new_user = User(
            telegram_id="123456789",
            name="John Doe",
            age=30,
            gender="M",
            country="Country",
            city="City",
            locations=["Location1", "Location2"],
            bio="Bio",
            is_search_traveller=True,
            username="username",
            date_joined=datetime.now()
        )
        self.session.add(new_user)
        self.session.commit()

        added_user = self.session.query(User).filter_by(telegram_id="123456789").first()
        self.assertIsNotNone(added_user)
        self.assertEqual(added_user.name, "John Doe")

    def test_02_update_user(self):
        user = self.session.query(User).filter_by(telegram_id="123456789").first()
        user.age = 31
        self.session.commit()

        updated_user = self.session.query(User).filter_by(telegram_id="123456789").first()
        self.assertEqual(updated_user.age, 31)

    def test_03_delete_user(self):
        user_to_delete = self.session.query(User).filter_by(telegram_id="123456789").first()
        self.session.delete(user_to_delete)
        self.session.commit()

        deleted_user = self.session.query(User).filter_by(telegram_id="123456789").first()
        self.assertIsNone(deleted_user)

    # Тесты для таблицы Journey
    def test_04_create_journey(self):
        test_user = self.session.query(User).filter_by(telegram_id="123456789").first()
        if not test_user:
            test_user = User(
                telegram_id="123456789",
                name="John Doe",
                age=30,
                gender="M",
                country="Country",
                city="City",
                locations=["Location1", "Location2"],
                bio="Bio",
                is_search_traveller=True,
                username="username",
                date_joined=datetime.now()
            )
            self.session.add(test_user)
            self.session.commit()

        new_journey = Journey(
            name="Test Journey",
            description="Description of Test Journey",
            user_id=test_user.id,
            is_public=True,
            date_created=datetime.now()
        )
        self.session.add(new_journey)
        self.session.commit()

        added_journey = self.session.query(Journey).filter_by(name="Test Journey").first()
        self.assertIsNotNone(added_journey)
        self.assertEqual(added_journey.description, "Description of Test Journey")

    def test_05_update_journey(self):
        journey = self.session.query(Journey).filter_by(name="Test Journey").first()
        journey.description = "Updated Description"
        self.session.commit()

        updated_journey = self.session.query(Journey).filter_by(name="Test Journey").first()
        self.assertEqual(updated_journey.description, "Updated Description")

    def test_06_delete_journey(self):
        journey_to_delete = self.session.query(Journey).filter_by(name="Test Journey").first()
        self.session.delete(journey_to_delete)
        self.session.commit()

        deleted_journey = self.session.query(Journey).filter_by(name="Test Journey").first()
        self.assertIsNone(deleted_journey)

    def test_07_create_location(self):
        test_journey = self.session.query(Journey).filter_by(name="Test Journey").first()
        if not test_journey:
            self.test_04_create_journey()
            test_journey = self.session.query(Journey).filter_by(name="Test Journey").first()

        new_location = Location(
            name="Test Location",
            address="123 Test St",
            start_date=datetime.today(),
            end_date=datetime.today() + timedelta(days=1),
            user_id=test_journey.user_id,
            journey_id=test_journey.id,
            lon=123.456,
            lat=78.910
        )
        self.session.add(new_location)
        self.session.commit()

        added_location = self.session.query(Location).filter_by(name="Test Location").first()
        self.assertIsNotNone(added_location)
        self.assertEqual(added_location.address, "123 Test St")

    def test_08_update_location(self):
        location = self.session.query(Location).filter_by(name="Test Location").first()
        location.address = "Updated Address"
        self.session.commit()

        updated_location = self.session.query(Location).filter_by(name="Test Location").first()
        self.assertEqual(updated_location.address, "Updated Address")

    def test_09_delete_location(self):
        location_to_delete = self.session.query(Location).filter_by(name="Test Location").first()
        self.session.delete(location_to_delete)
        self.session.commit()

        deleted_location = self.session.query(Location).filter_by(name="Test Location").first()
        self.assertIsNone(deleted_location)

    # Тесты для таблицы Note
    def test_10_create_note_with_text(self):
        user = self.session.query(User).filter_by(telegram_id="123456789").first()
        journey = self.session.query(Journey).filter_by(name="Test Journey").first()

        new_note = Note(
            journey_id=journey.id,
            user_id=user.id,
            is_public=True,
            text="This is a test note."
        )
        self.session.add(new_note)
        self.session.commit()

        added_note = self.session.query(Note).filter_by(text="This is a test note.").first()
        self.assertIsNotNone(added_note)
        self.assertEqual(added_note.text, "This is a test note.")
        self.assertTrue(added_note.is_public)

    def test_11_create_note_with_photo(self):
        user = self.session.query(User).filter_by(telegram_id="123456789").first()
        journey = self.session.query(Journey).filter_by(name="Test Journey").first()

        new_note = Note(
            journey_id=journey.id,
            user_id=user.id,
            is_public=False,
            photo_file_id="photo_id_123"
        )
        self.session.add(new_note)
        self.session.commit()

        added_note = self.session.query(Note).filter_by(photo_file_id="photo_id_123").first()
        self.assertIsNotNone(added_note)
        self.assertEqual(added_note.photo_file_id, "photo_id_123")
        self.assertFalse(added_note.is_public)

    def test_12_create_note_with_document(self):
        user = self.session.query(User).filter_by(telegram_id="123456789").first()
        journey = self.session.query(Journey).filter_by(name="Test Journey").first()

        new_note = Note(
            journey_id=journey.id,
            user_id=user.id,
            is_public=True,
            document_file_id="document_id_123"
        )
        self.session.add(new_note)
        self.session.commit()

        added_note = self.session.query(Note).filter_by(document_file_id="document_id_123").first()
        self.assertIsNotNone(added_note)
        self.assertEqual(added_note.document_file_id, "document_id_123")
        self.assertTrue(added_note.is_public)

    def test_13_delete_note(self):
        note_to_delete = self.session.query(Note).filter_by(text="This is a test note.").first()
        if note_to_delete is not None:
            self.session.delete(note_to_delete)
            self.session.commit()

        deleted_note = self.session.query(Note).filter_by(text="This is a test note.").first()
        self.assertIsNone(deleted_note)

    # Тесты на таблицу Task
    def test_14_create_task(self):
        user = self.session.query(User).filter_by(telegram_id="123456789").first()
        journey = self.session.query(Journey).filter_by(name="Test Journey").first()

        new_task = Task(
            journey_id=journey.id,
            user_id=user.id,
            name="Test Task"
        )
        self.session.add(new_task)
        self.session.commit()

        added_task = self.session.query(Task).filter_by(name="Test Task").first()
        self.assertIsNotNone(added_task)
        self.assertEqual(added_task.name, "Test Task")
        self.assertFalse(added_task.is_completed)

    def test_15_update_task(self):
        task_to_update = self.session.query(Task).filter_by(name="Test Task").first()
        task_to_update.is_completed = True
        self.session.commit()

        updated_task = self.session.query(Task).filter_by(name="Test Task").first()
        self.assertTrue(updated_task.is_completed)

    def test_16_delete_task(self):
        task_to_delete = self.session.query(Task).filter_by(name="Test Task").first()
        self.session.delete(task_to_delete)
        self.session.commit()

        deleted_task = self.session.query(Task).filter_by(name="Test Task").first()
        self.assertIsNone(deleted_task)

    # Тесты для таблицы Transaction
    def test_17_create_transaction(self):
        test_user = User(
            telegram_id="987654321",
            name="Doe John",
            age=40,
            gender="M",
            country="Country",
            city="City",
            locations=["Location3", "Location4"],
            bio="Bio",
            is_search_traveller=False,
            date_joined=datetime.now()
        )
        self.session.add(test_user)
        self.session.commit()
        payer = self.session.query(User).filter_by(telegram_id="123456789").first()
        debtor = self.session.query(User).filter_by(telegram_id="987654321").first()
        journey = self.session.query(Journey).filter_by(name="Test Journey").first()

        new_transaction = Transaction(
            journey_id=journey.id,
            payer_id=payer.id,
            debtor_id=debtor.id,
            name="Test Transaction",
            amount=100,
            is_settled=False,
            date=datetime.now()
        )
        self.session.add(new_transaction)
        self.session.commit()

        added_transaction = self.session.query(Transaction).filter_by(name="Test Transaction").first()
        self.assertIsNotNone(added_transaction)
        self.assertEqual(added_transaction.amount, 100)
        self.assertFalse(added_transaction.is_settled)

    def test_18_update_transaction(self):
        transaction_to_update = self.session.query(Transaction).filter_by(name="Test Transaction").first()
        transaction_to_update.is_settled = True
        self.session.commit()

        updated_transaction = self.session.query(Transaction).filter_by(name="Test Transaction").first()
        self.assertTrue(updated_transaction.is_settled)

    def test_19_delete_transaction(self):
        transaction_to_delete = self.session.query(Transaction).filter_by(name="Test Transaction").first()
        self.session.delete(transaction_to_delete)
        self.session.commit()

        deleted_transaction = self.session.query(Transaction).filter_by(name="Test Transaction").first()
        self.assertIsNone(deleted_transaction)
