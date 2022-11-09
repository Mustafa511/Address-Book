from sqlalchemy import Column, Integer, String, Float

from database import Base


class AddressBook(Base):
    __tablename__ = "addressbook"
    aid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    latitude = Column(Float)
    longitude = Column(Float)
    name = Column(String)
