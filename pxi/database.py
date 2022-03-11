from os import PathLike
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from pxi.models import Base


def get_session(sqlite_filepath: str) -> Session:
    db = create_engine(f"sqlite:///{sqlite_filepath}")
    Base.metadata.create_all(db)
    session = sessionmaker(bind=db)()
    return session
