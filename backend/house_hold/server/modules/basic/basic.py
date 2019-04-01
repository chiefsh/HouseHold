from core.base_handler import BaseHandler, arguments, authenticated
from .model import BasicModel
from core.exception import NotFound, ParametersError


class BasicUpdateHandler(BaseHandler):

    @authenticated
    @arguments
    def post(self, basic_id: int = None, topic: str = "", viewpager_1: str = '', viewpager_2: str = '',
             viewpager_3: str = '',
             viewpager_4: str = '', viewpager_5: str = '', ad_image: str = '', qr_code: str = '', contact: str = '',
             model:BasicModel=None):
        model.update_basic_info(basic_id, topic, viewpager_1, viewpager_2, viewpager_3, viewpager_4, viewpager_5,
                                ad_image, qr_code, contact)
        self.finish({
            "code": 0,
            "msg": "success"
        })


class BasicQueryHandler(BaseHandler):

    @arguments
    def get(self, basic_id:int = None, model:BasicModel=None):
        if not basic_id:
            raise ParametersError()
        result = model.query_basic_info(basic_id)
        self.finish({
            "code": 0,
            "msg": 'success',
            "data": result
        })

