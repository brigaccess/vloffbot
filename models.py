from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, ForeignKey

Base = declarative_base()


class Chat(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    added_on = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)


class Subscribition(Base):
    __tablename__ = 'subscribitions'

    id = Column(Integer, primary_key=True)
    chat = Column(BigInteger)
    address_id = Column(Integer, ForeignKey('addresses.id'))
    address = relationship('Address')
    added_on = Column(DateTime, default=datetime.utcnow)


class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    address = Column(String)
    url = Column(String)

    __mapper_args__ = {
        "order_by": address
    }


class Blackout(Base):
    __tablename__ = 'blackouts'

    id = Column(Integer, primary_key=True)
    type_ = Column(String)
    date_ = Column(String)
    time_ = Column(String)
    description = Column(String)
    addresses_checksum = Column(String)
    done = Column(Boolean, default=False)


class BlackoutAddress(Base):
    __tablename__ = 'blackout_addresses'

    id = Column(Integer, primary_key=True)
    blackout_id = Column(Integer)
    address_url = Column(String)  # vl.ru/off link
