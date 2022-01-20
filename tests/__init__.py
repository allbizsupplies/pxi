
import unittest

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pxi.models import Base


class PXITestCase(unittest.TestCase):

    def __init__(self, methodName="runTest"):
        super().__init__(methodName=methodName)


class DatabaseTestCase(PXITestCase):

    def setUp(self):
        """
        Initialise connection to in-memory database.
        """
        super().setUp()
        self.db = create_engine('sqlite://')
        Base.metadata.create_all(self.db)
        self.session = sessionmaker(bind=self.db)()

    def tearDown(self):
        """
        Delete all records from database.
        """
        super().tearDown()
        for tbl in reversed(Base.metadata.sorted_tables):
            self.session.execute(tbl.delete())
        self.session.commit()

    def seed(self, records):
        """
        Add records to database.
        """
        for record in records:
            self.session.add(record)
        self.session.commit()
