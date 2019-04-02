import json
import logging

from core.base_handler import BaseHandler, arguments, authenticated
from .model import ProductModel


class ProductAddHandler(BaseHandler):

    @authenticated
    @arguments
    def post(self,
             product_id: int = None,
             name: str = "",
             category_id: int = None,
             group_price: float = None,
             market_price: float = None,
             rate: str = '',
             charge_unit: str = "",
             group_member: int = None,
             community_id: int = None,
             brief: str = "",
             sell_point: str = "",
             detail: str = "",
             transport_sale: str = '',
             introduction: str = '',
             image_0: str = '',
             image_1: str = '',
             image_2: str = '',
             image_3: str = '',
             image_4: str = '',
             model: ProductModel = None
             ):
        model.add_product(product_id, name, category_id, group_price, market_price, rate, charge_unit, group_member,
                          community_id, brief, sell_point, detail, transport_sale, introduction, image_0, image_1,
                          image_2, image_3, image_4)
        self.finish({
            "code": 0,
            "msg": "操作成功"
        })


class ProductDeleteHandler(BaseHandler):

    @authenticated
    @arguments
    def delete(self, product_ids: int = None, model: ProductModel = None):
        model.delete_product(product_ids)
        self.finish({
            "code": 0,
            "msg": "操作成功"
        })


class ProductQueryHandler(BaseHandler):

    @arguments
    def get(self, product_id: int = None, page: int = 0, size: int = 20, model: ProductModel = None):
        result = model.query_one_page(product_id, page, size)
        self.finish({
            "code": 0,
            "msg": "success",
            "data": result
        })
