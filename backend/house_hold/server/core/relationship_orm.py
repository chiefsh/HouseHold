from sqlalchemy.orm import relationship, foreign

from core.schema import *


class UserWithWx(User):
    """附带微信关联信息"""
    wx = relationship(
        WxUser,
        primaryjoin=foreign(WxUser.user_id) == User.user_id,
        order_by=WxUser.modified.desc(),
        uselist=False,
    )
