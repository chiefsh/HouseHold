from core.base_handler import BaseHandler, arguments, authenticated
from .model import CommunityModel
from core.exception import NotFound, ParametersError


class CommunityAddHandler(BaseHandler):

    @authenticated
    @arguments
    def post(self, community_id: int = None, province_id: int = None, city_id: int = None, area: int = None,
             name: str = '', note: str = '',
             model: CommunityModel = None):
        if not province_id or not city_id:
            raise ParametersError()
        model.add_community(community_id, province_id, city_id, area, name, note)
        self.finish({
            "code": 0,
            "msg": "success",
        })


class CommunityQueryHandler(BaseHandler):

    @arguments
    def post(self, community_id: int = None, page: int = 0, size=20, model=CommunityModel):
        result, total = model.query_community_info(community_id, page, size)
        self.finish({
            "code": 0,
            "msg": 'success',
            "data": result,
            "total": total
        })


class CommunityDeleteHandler(BaseHandler):

    @authenticated
    @arguments
    def delete(self, community_ids: int = None, model:CommunityModel=None):
        if not community_ids:
            raise ParametersError()
        model.delete_community(community_ids)
        self.finish({
            "code": 0,
            "msg": 'success'
        })
