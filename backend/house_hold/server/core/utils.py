import logging
import os
import sys
from copy import deepcopy
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.orm.attributes import QueryableAttribute, InstrumentedAttribute
from sqlalchemy.orm.base import instance_state

from core.schema import Base, bson
from core.exception import ParametersError
from settings.constant import BASE_IMAGE_PATH


def row2dict(row):
    """将对象(一般为orm row)转换为dict"""
    record = {}
    # 清除掉过期状态，强制的跳过state._load_expired(state, passive)
    # 如果有字段确实需要而没有的，要么设置default值，要么使用refresh从数据库拿到server_default值
    state = instance_state(row)
    state.expired_attributes.clear()
    attributes, cls = deepcopy(row.__dict__), row.__class__
    for c in dir(row):
        if hasattr(cls, c):
            a = getattr(cls, c)
            # hybrid_property
            if isinstance(a, QueryableAttribute) and not isinstance(a, InstrumentedAttribute):
                attributes[c] = 1  # 这里只需要有attribute name就可以了

    for c in attributes:
        if not c.startswith('_') and 'metadata' != c:
            try:
                v = row.__getattribute__(c)
            except KeyError as e:  # https://github.com/zzzeek/sqlalchemy/blob/master/lib/sqlalchemy/orm/attributes.py#L579 这个函数可能会raise KeyError出来
                logging.exception(e)
                v = datetime.now() if c in ['created', 'modified'] else None
            if isinstance(v, Base):
                v = row2dict(v)
            if isinstance(v, Decimal):
                v = int(v)
            # 特殊处理一下生日，以及开始时间结束时间
            if c in ['start', 'end'] and row.__tablename__ in ['work', 'education']:
                v = v.strftime('%Y.%m')
            if c in ['birthday'] and row.__tablename__ in ['user']:
                v = v.strftime('%Y.%m.%d')
            if isinstance(v, datetime):
                v = v.strftime('%Y.%m.%d %H:%M:%S')
            if isinstance(v, InstrumentedList):
                v = list(map(lambda i: row2dict(i), v))
            record[c] = v

    return record


def check_file_exist(image_name):
    """判断文件是否存在"""
    logging.info("file_path::::::%r", os.path.join(BASE_IMAGE_PATH, image_name))
    return os.path.isfile(os.path.join(BASE_IMAGE_PATH, image_name))


def delete_image_file(image_name):
    try:
        logging.info("file_path_delete::::::%r", os.path.join(BASE_IMAGE_PATH, image_name))
        sys.path.remove(os.path.join(BASE_IMAGE_PATH, image_name))
    except Exception as e:
        logging.info(e)
        return False


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class DateTimeStr(str):

    def __new__(cls, value, **kwargs):
        try:
            datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logging.exception(e)
            raise ParametersError(value)
        return str(value, **kwargs)


class DateStr(str):

    def __new__(cls, value, **kwargs):
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except Exception as e:
            logging.exception(e)
            raise ParametersError(value)
        return str(value, **kwargs)


class ObjIDStr(str):

    def __new__(cls, value, **kwargs):
        if not bson.ObjectId.is_valid(value):
            raise ParametersError(value)
        return str(value, **kwargs)


