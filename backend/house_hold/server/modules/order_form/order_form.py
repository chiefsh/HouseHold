from core.base_handler import BaseHandler, arguments, authenticated
from core.exception import NotFound, ParametersError
from .model import OrderFormModel


class OrderFormAddHandler(BaseHandler):

    @arguments
    def post(self, name: str = '',
             telephone: str = '',
             community_id: int = None,
             address: str = '',
             apartment: int = None,
             product_id: int = None,
             model: OrderFormModel = None
             ):
        if not name or not telephone or not address or not product_id:
            raise ParametersError()
        model.add_order_form(name, telephone, community_id, address, apartment, product_id)
        self.finish({
            "code": 0,
            "msg": "success",
        })


class OrderFormCheckHandler(BaseHandler):

    @authenticated
    @arguments
    def post(self, order_id:int = None, note: str = '', review_status: int = 0, model: OrderFormModel = None):
        if order_id is None:
            raise ParametersError()
        model.update_order_form(order_id, note, review_status)
        self.finish({
            "code": 0,
            "msg": "success",
        })


class OrderFormQueryHandler(BaseHandler):

    @authenticated
    @arguments
    def get(self, review_status: int = None, page: int = 0, size: int = 20, model: OrderFormModel = None):
        result = model.query_all_order_form(review_status, page, size)
        self.finish({
            "code": 0,
            "msg": 'success',
            "data": result
        })