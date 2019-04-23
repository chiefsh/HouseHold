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
    __tablename__ = "account"
    user_id = Column(Integer, primary_key=True)
    username = Column(String(128), nullable=False, server_default=text("''"))
    password = Column(String(128), nullable=False, server_default=text("''"))
    created_at = Column(Integer, nullable=False, server_default=text("0"))


class Product(Base):
    __tablename__ = "product"
    product_id = Column(ObjID(12))
    name = Column(String(128), nullable=False, server_default=text("''"))
    category_ids = Column(String(128), nullable=False, server_default=text("0"))
    group_price = Column(Float, nullable=False, server_default=text("0"))
    market_price = Column(Float, nullable=False, server_default=text("0"))
    charge_unit = Column(String(15), nullable=False, server_default=text("''"))
    group_number = Column(Integer, nullable=False, server_default=text("0"))
    community_id = Column(String(128), nullable=False, server_default=text("0"))
    brief = Column(String(128), nullable=False, server_default=text("''"))
    sell_point = Column(String(128), nullable=False, server_default=text("''"))
    detail = Column(String(1024), nullable=False, server_default=text("''"))
    transport_sale = Column(String(128), nullable=False, server_default=text("''"))
    rate = Column(String(64), nullable=False, server_default=text("''"))
    introduction  = Column(String(512), nullable=False, server_default=text("''"))
    image_0 = Column(String(128), nullable=False, server_default=text("''"))
    image_1 = Column(String(128), nullable=False, server_default=text("''"))
    image_2 = Column(String(128), nullable=False, server_default=text("''"))
    image_3 = Column(String(128), nullable=False, server_default=text("''"))
    image_4 = Column(String(128), nullable=False, server_default=text("''"))
    created_at = Column(Integer, nullable=False, server_default=text("0"))
    is_top = Column(Integer, nullable=False, server_default=text("0"))
    rank = Column(Integer, primary_key=True)
    deleted = Column(Integer, nullable=False, server_default=text("0"))


class CacheData(Base):
    __tablename__ = "cache_data"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), nullable=False, server_default=text("''"))
    sid = Column(String(128), nullable=False, server_default=text("''"))
    deadline = Column(Integer, nullable=False, server_default=text("0"))


class Category(Base):
    __tablename__ = "category"
    category_id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, server_default=text("''"))
    created_at = Column(Integer, nullable=False, server_default=text("0"))
    is_top = Column(Integer, nullable=False, server_default=text("0"))


class Community(Base):
    __tablename__ = 'community'
    community_id = Column(Integer, primary_key=True)
    province_id = Column(Integer, nullable=False, server_default=text("0"))
    city_id = Column(Integer, nullable=False, server_default=text("0"))
    area = Column(Integer, nullable=False, server_default=text("0"))
    viewpager_0 = Column(String(64), nullable=False, server_default=text("''"))
    viewpager_1 = Column(String(64), nullable=False, server_default=text("''"))
    viewpager_2 = Column(String(64), nullable=False, server_default=text("''"))
    viewpager_3 = Column(String(64), nullable=False, server_default=text("''"))
    ad_image = Column(String(64), nullable=False, server_default=text("''"))
    name = Column(String(128), nullable=False, server_default=text("''"))
    note = Column(String(512), nullable=False, server_default=text("''"))
    created_at = Column(Integer, nullable=False, server_default=text("0"))
    link_0 =  Column(String(128), nullable=False, server_default=text("''"))
    link_1 =  Column(String(128), nullable=False, server_default=text("''"))
    link_2 =  Column(String(128), nullable=False, server_default=text("''"))
    link_3 =  Column(String(128), nullable=False, server_default=text("''"))
    is_top = Column(Integer, nullable=False, server_default=text("0"))


class Region(Base):
    __tablename__ = "region"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, server_default=text("''"))
    parent_id = Column(Integer, nullable=False, server_default=text("0"))


class BasicInfo(Base):
    __tablename__ = "basic_info"
    id = Column(Integer, primary_key=True)
    topic = Column(String(512), nullable=False, server_default=text("''"))
    qr_code = Column(String(512), nullable=False, server_default=text("''"))
    contact = Column(String(512), nullable=False, server_default=text("''"))
    created_at = Column(Integer, nullable=False, server_default=text("0"))


class OrderForm(Base):
    __tablename__ = "order_form"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, server_default=text("''"))
    telephone = Column(String(15), nullable=False, server_default=text("''"))
    community_id = Column(Integer, nullable=False, server_default=text("0"))
    address = Column(String(64), nullable=False, server_default=text("''"))
    apartment = Column(Integer, nullable=False, server_default=text("0"))
    product_id = Column(ObjID(12), nullable=False, server_default=text("''"))
    review_status = Column(Integer, nullable=False, server_default=text("0"))
    note = Column(String(128), nullable=False, server_default=text("''"))
    created_at = Column(Integer, nullable=False, server_default=text("0"))
