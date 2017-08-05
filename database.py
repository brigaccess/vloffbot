from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

import config
from models import Base


def init_db():
    e = create_engine(config.SQLALCHEMY_DATABASE_URI, pool_size=10)
    s = scoped_session(sessionmaker(bind=e))
    return e, s

engine, Session = init_db()
Base.metadata.create_all(engine)


def uses_db(*args, session=Session):
    def uses_db_decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            s = session()
            result = None
            try:
                result = func(*args, **kwargs, session=s)
            finally:
                s.close()
            return result
        return func_wrapper
    if args:
        return uses_db_decorator(args[0])
    return uses_db_decorator
