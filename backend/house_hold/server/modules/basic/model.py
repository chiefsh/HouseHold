import time

from core.base_model import MysqlModel
from core.schema import BasicInfo
from core.utils import row2dict


class BasicModel(MysqlModel):

    def update_basic_info(self, basic_id, topic,
                           qr_code, contact):
        self.session.begin()
        if basic_id is None:
            basic_info = BasicInfo(
                topic=topic,
                qr_code=qr_code,
                contact=contact,
                created_at=int(time.time())
            )
            self.session.add(basic_info)
        else:
            self.session.query(BasicInfo).filter(
                BasicInfo.id == basic_id
            ).update({
                BasicInfo.topic: topic and topic or BasicInfo.topic,
                BasicInfo.qr_code: qr_code and qr_code or BasicInfo.qr_code,
                BasicInfo.contact: contact and contact or BasicInfo.contact,
            })
        self.session.commit()

    def query_basic_info(self):
        data = self.session.query(BasicInfo).all()
        return row2dict(data[0]) if data else ''
