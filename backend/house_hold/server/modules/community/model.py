import time

from core.base_model import MysqlModel
from core.schema import Community, Region
from core.utils import row2dict


class CommunityModel(MysqlModel):

    def add_community(self, community_id, province_id, city_id, area, viewpager_0, viewpager_1, viewpager_2, viewpager_3, ad_image,  name, note):
        self.session.begin()
        if community_id is None:
            community = Community(
                province_id=province_id,
                city_id=city_id,
                area=area,
                viewpager_0=viewpager_0,
                viewpager_1=viewpager_1,
                viewpager_2=viewpager_2,
                viewpager_3=viewpager_3,
                ad_image=ad_image,
                name=name,
                note=note,
                created_at=int(time.time())
            )
            self.session.add(community)
        else:
            self.session.query(Community).filter(
                Community.community_id == community_id
            ).update({
                Community.province_id: province_id and province_id or Community.province_id,
                Community.city_id: city_id and city_id or Community.city_id,
                Community.area: area and area or Community.area,
                Community.viewpager_0: viewpager_0 and viewpager_0 or Community.viewpager_0,
                Community.viewpager_1: viewpager_1 and viewpager_1 or Community.viewpager_1,
                Community.viewpager_2: viewpager_2 and viewpager_2 or Community.viewpager_2,
                Community.viewpager_3: viewpager_3 and viewpager_3 or Community.viewpager_3,
                Community.ad_image: ad_image and ad_image or Community.ad_image,
                Community.name: name and name or Community.name,
                Community.note: note and note or Community.note,
            })
        self.session.commit()

    def get_region_name(self, region_id):
        result = self.session.query(Region.name).filter(Region.id==int(region_id)).first()
        return result[0] if result else ''

    def query_community_info(self, community_id, page, size):
        if community_id is None:
            query = self.session.query(Community)
            total = self.query_total(query)
            result = self.query_one_page(query, page, size)
            data = [row2dict(item) for item in result] if result else []
            for item in data:
                item['province'] = self.get_region_name(item['province_id'])
                item['city'] = self.get_region_name(item['city_id'])
                item['area_name'] = self.get_region_name(item['area'])
        else:
            result = self.session.query(Community).filter(
                Community.community_id == community_id
            ).first()
            data = row2dict(result) if result else ''
            if data:
                data['province'] = self.get_region_name(data['province_id'])
                data['city'] = self.get_region_name(data['city_id'])
                data['area_name'] = self.get_region_name(data['area'])
            total = 0
        return data, total

    def delete_community(self, community_ids):
        for id_ in community_ids:
            self.session.query(Community).filter(Community.community_id==id_).delete()
