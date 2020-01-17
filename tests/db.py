
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Connection
from sqlalchemy.exc import IntegrityError

from pxi.models import User, InventoryItem
from tests import DatabaseTestCase


test_users = [
    {
        "name": "testuser1",
        "fullname": "Test User Number One",
        "nickname": "uno"
    },
    {
        "name": "testuser2",
        "fullname": "Test User Number Two",
        "nickname": "dos"
    },
]


class DatabaseTests(DatabaseTestCase):

    def test_connection(self):
        """Open connection to database."""
        conn = self.db.connect()
        self.assertIsInstance(conn, Connection)

    def test_add_user(self):
        """Add a User."""
        user = User(**test_users[0])
        self.session.add(user)
        self.session.commit()
        self.assertEqual(user.id, 1)

    def test_fetch_user(self):
        """Fetch a User."""
        user = User(**test_users[0])
        self.session.add(user)
        result = self.session.query(User).filter(
            User.name == test_users[0]["name"]).one()
        self.assertEqual(result, user)