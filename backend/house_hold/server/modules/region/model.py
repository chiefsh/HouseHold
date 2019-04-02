from core.base_model import MysqlModel
from core.schema import Region
from core.utils import row2dict


class RegionModel(MysqlModel):

    def query_province(self, address_id):
        result = self.session.query(Region).filter(
            Region.parent_id == address_id
        ).all()
        return [row2dict(item) for item in result] if result else []

    def query_city(self, parent_id):
        result = self.session.query(Region).filter(
            Region.parent_id == parent_id
        ).all()
        return [row2dict(item) for item in result] if result else []
