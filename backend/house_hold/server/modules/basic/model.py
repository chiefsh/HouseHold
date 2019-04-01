import time

from core.base_model import MysqlModel
from core.schema import BasicInfo
from core.utils import row2dict


class BasicModel(MysqlModel):

    def update_basic_info(self, basic_id, topic, viewpager_1, viewpager_2, viewpager_3, viewpager_4, viewpager_5,
                          ad_image, qr_code, contact):
        self.session.begin()
        if basic_id is None:
            basic_info = BasicInfo(
                topic=topic,
                viewpager_1=viewpager_1,
                viewpager_2=viewpager_2,
                viewpager_3=viewpager_3,
                viewpager_4=viewpager_4,
                viewpager_5=viewpager_5,
                ad_image=ad_image,
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
                BasicInfo.viewpager_1: viewpager_1 and viewpager_1 or BasicInfo.viewpager_1,
                BasicInfo.viewpager_2: viewpager_2 and viewpager_2 or BasicInfo.viewpager_2,
                BasicInfo.viewpager_3: viewpager_3 and viewpager_3 or BasicInfo.viewpager_3,
                BasicInfo.viewpager_4: viewpager_4 and viewpager_4 or BasicInfo.viewpager_4,
                BasicInfo.viewpager_5: viewpager_5 and viewpager_5 or BasicInfo.viewpager_5,
                BasicInfo.ad_image: ad_image and ad_image or BasicInfo.ad_image,
                BasicInfo.qr_code: qr_code and qr_code or BasicInfo.qr_code,
                BasicInfo.contact: contact and contact or BasicInfo.contact,
            })
        self.session.commit()

    def query_basic_info(self, basic_id):
        data = self.session.query(BasicInfo).filter(BasicInfo.id == basic_id).first()
        return row2dict(data) if data else ''
