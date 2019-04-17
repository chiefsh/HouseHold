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
             product_ids: str = None,
             model: OrderFormModel = None
             ):
        if not name or not telephone or not address or not product_ids:
            raise ParametersError()
        model.add_order_form(name, telephone, community_id, address, apartment, product_ids)
        self.finish({
            "code": 0,
            "msg": "success",
        })


class OrderFormCheckHandler(BaseHandler):

    @authenticated
    @arguments
    def post(self, order_id: int = None, note: str = '', review_status: int = 0, model: OrderFormModel = None):
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
    def get(self, telephone:str = None, community_id:str = None, review_status: str = None, page: int = 0, size: int = 20, model: OrderFormModel = None):
        result, total = model.query_all_order_form(telephone, community_id, review_status, page, size)
        self.finish({
            "code": 0,
            "msg": 'success',
            "data": result,
            "total": total
        })


class OrderFormDeleteHandler(BaseHandler):

    @authenticated
    @arguments
    def delete(self, order_ids: int = None, model: OrderFormModel = None):
        model.delete_order_form(order_ids)
        self.finish({
            "code": 0,
            "msg": 'success',
        })
