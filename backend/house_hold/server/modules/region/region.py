from core.base_handler import BaseHandler, arguments, authenticated
from core.exception import NotFound, ParametersError
from .model import RegionModel


class RegionProvinceQuery(BaseHandler):

    @arguments
    def get(self, model: RegionModel = None):
        result = model.query_province()
        self.finish({
            "code": 0,
            "msg": "success",
            "data": result
        })


class RegionCityQuery(BaseHandler):

    @arguments
    def get(self, province_id: int = None, model: RegionModel = None):
        result = model.query_city(province_id)
        self.finish({
            "code": 0,
            "msg": "success",
            "data": result
        })
