from core.base_handler import BaseHandler, arguments, authenticated
from .model import BasicModel
from core.exception import NotFound, ParametersError


class BasicUpdateHandler(BaseHandler):

    @authenticated
    @arguments
    def post(self, id: int = None, topic: str = "", qr_code: str = '', contact: str = '',
             model:BasicModel=None):
        model.update_basic_info(id, topic, qr_code, contact)
        self.finish({
            "code": 0,
            "msg": "success"
        })


class BasicQueryHandler(BaseHandler):

    @arguments
    def get(self, basic_id:int = None, model:BasicModel=None):
       # if not basic_id:
       #     raise ParametersError()
        result = model.query_basic_info()
        self.finish({
            "code": 0,
            "msg": 'success',
            "data": result
        })

