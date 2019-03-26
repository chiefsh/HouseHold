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
             charge_unit: str = "",
             group_member: int = None,
             community_id: int = None,
             brief: str = "",
             sell_point: str = "",
             detail: str = "",
             transport_sale: str = '',
             model: ProductModel = None
             ):
        model.add_product(product_id, name, category_id, group_price, market_price, charge_unit, group_member,
                          community_id,
                          brief, sell_point, detail, transport_sale)
        self.finish({
            "code": 0,
            "msg": "操作成功"
        })

    @authenticated
    @arguments
    def delete(self, product_ids: int = None, model: ProductModel = None):
        model.delete_product(product_ids)
        self.finish({
            "code": 0,
            "msg": "操作成功"
        })

    @arguments
    def get(self, page: int = 0, size: int = 20, model: ProductModel = None):
        result = model.query_one_page(page, size)
        self.finish({
            "code":
        })
