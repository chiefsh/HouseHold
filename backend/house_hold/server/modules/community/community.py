from core.base_handler import BaseHandler, arguments, authenticated
from .model import CommunityModel
from core.exception import NotFound, ParametersError


class CommunityAddHandler(BaseHandler):

    @authenticated
    @arguments
    def post(self, community_id: int = None, province_id: int = None, city_id: int = None, area: int = None,
             viewpager_0:str = "", viewpager_1:str = '', viewpager_2:str = '', viewpager_3:str = '', ad_image:str = '',
             name: str = '', note: str = '', link_0: str = '', link_1: str = "", link_2: str = '', link_3 : str = '',
             model: CommunityModel = None):
        if province_id is None or city_id is None:
            raise ParametersError()
        model.add_community(community_id, province_id, city_id, area, viewpager_0, viewpager_1, viewpager_2, viewpager_3, ad_image, name, note, link_0, link_1, link_2, link_3)
        self.finish({
            "code": 0,
            "msg": "success",
        })


class CommunityQueryHandler(BaseHandler):

    @arguments
    def get(self, community_id: int = None, page: int = 0, size: int=20, model:CommunityModel=None):
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
    def post(self, community_ids: str = None, model:CommunityModel=None):
        if not community_ids:
            raise ParametersError()
        community_ids = community_ids.split(",")
        model.delete_community(community_ids)
        self.finish({
            "code": 0,
            "msg": 'success'
        })


class CommunityIsTopHandler(BaseHandler):

    @authenticated
    @arguments
    def post(self, community_id:int = None, is_top:int = None, model:CommunityModel=None):
        if not community_id:
            raise ParametersError()
        model.handle_is_top(community_id, is_top)
        self.finish({
            "code": 0,
            "msg": 'success'
        })

class CommunitySortHandler(BaseHandler):

    @authenticated
    @arguments
    def post(self, above_community_id:int = None, under_community_id:int = None, model:CommunityModel=None):
        if not (above_community_id and under_community_id):
            raise ParametersError()
        model.handle_sort_list(above_community_id, under_community_id)
        self.finish({
            "code": 0,
            "msg": 'success'
        })
