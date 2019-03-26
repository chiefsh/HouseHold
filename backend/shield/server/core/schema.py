import bson
import json
import logging
from sqlalchemy import (
    Column, TIMESTAMP, Integer, String,
    text, BINARY, Float
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ObjID(BINARY):
    """基于bson.ObjectId用于mysql主键的自定义类型"""
    def bind_processor(self, dialect):
        def processor(value):
            return bson.ObjectId(value).binary if bson.ObjectId.is_valid(value) else value

        return processor

    def result_processor(self, dialect, coltype):
        def processor(value):
            return str(bson.ObjectId(value)) if bson.ObjectId.is_valid(value) else value

        return processor

    @staticmethod
    def new_id():
        return str(bson.ObjectId())

    @staticmethod
    def is_valid(value):
        return bson.ObjectId.is_valid(value)


class JSONStr(String):
    """自动转换 str 和 dict 的自定义类型"""
    def bind_processor(self, dialect):
        def processor(value):
            try:
                return json.dumps(value)
            except Exception as e:
                logging.exception(e)
                return value
        return processor

    def result_processor(self, dialect, coltype):
        def processor(value):
            try:
                return json.loads(value)
            except Exception as e:
                logging.exception(e)
                return value
        return processor

    @staticmethod
    def is_valid(value):
        try:
            json.loads(value)
            return True
        except Exception as e:
            logging.exception(e)
            return False


class User(Base):
    """用户账号"""
    __tablename__ = 'user'
    user_id = Column(ObjID(12), primary_key=True)
    name = Column(String(128), nullable=False, server_default=text("''"))
    telephone = Column(String(13), nullable=False, server_default=text("''"))
    email = Column(String(128), nullable=False, server_default=text("''"))

    extra = Column(JSONStr, nullable=False, server_default=text("{}"))

    deleted = Column(Integer, nullable=False, server_default=text("'0'"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    modified_at = Column(TIMESTAMP, nullable=False,
                         server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class Account(Base):
    __tablename__="account"
    user_id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, server_default=text("''"))
    password = Column(String(128), nullable=False, server_default=text("''"))
    created_at = Column(Integer, nullable=False, server_default=text("0"))


class product(Base):
    __tablename__="product"
    product_id = Column(ObjID(12), primary_key=True)
    name = Column(String(128), nullable=False, server_default=text("''"))
    category_id = Column(Integer, nullable=False, server_default=text("0"))
    group_price = Column(Float, nullable=False, server_default=text("0"))
    market_price = Column(Float, nullable=False, server_default=text("0"))
    charge_unit = Column(String(15), nullable=False, server_default=text("''"))
    group_number = Column(Integer, nullable=False, server_default=text("0"))
    community_id = Column(Integer, nullable=False, server_default=text("0"))
    brief = Column(String(128), nullable=False, server_default=text("''"))
    sell_point = Column(String(128), nullable=False, server_default=text("''"))
    detail = Column(String(1024), nullable=False, server_default=text("''"))
    transport_sale = Column(String(128), nullable=False, server_default=text("''"))
    created_at = Column(Integer, nullable=False, server_default=text("0"))


