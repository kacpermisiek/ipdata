from typing import Any, Iterator

from pydantic import SecretStr
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from ipdata.settings import settings

Base = declarative_base()
Meta = MetaData()


def get_session(database_dsn: SecretStr) -> Any:
    session_constructor = get_session_constructor(database_dsn)
    session = session_constructor()
    return session


def get_session_constructor(database_dsn: SecretStr) -> Any:
    engine = prepare_database(database_dsn)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def prepare_database(database_dsn: SecretStr) -> Any:
    return create_engine(
        database_dsn.get_secret_value(),
    )


def get_db():
    def inner() -> Iterator[Session]:
        db = get_session(settings.database_dsn)
        try:
            yield db
        finally:
            db.close()

    return inner
