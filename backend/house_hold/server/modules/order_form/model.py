import time
from sqlalchemy.orm import relationship, joinedload, lazyload, column_property, foreign, aliased
from sqlalchemy import select, outerjoin, or_, func, and_, between, desc, join

from core.base_model import MysqlModel
from core.schema import Category, Product, OrderForm, Community
from core.utils import row2dict
APARTMENT_DICT = {0:"一居室", 1:"二居室", 2:"三居室"}

class OrderFormNew(OrderForm):
    community = column_property(
        select([Community.name]).where(and_(Community.community_id == OrderForm.community_id)))
    product = column_property(
        select([Product.name]).where(Product.product_id == OrderForm.product_id)
    )


class OrderFormModel(MysqlModel):

    def add_order_form(self, name, telephone, community_id, address, apartment, product_ids):
        self.session.begin()
        product_ids = product_ids.split(",")
        for product_id in product_ids:
            order = OrderForm(
                name=name,
                telephone=telephone,
                community_id=community_id,
                address=address,
                apartment=apartment,
                product_id=product_id,
                review_status=0,
                created_at=int(time.time())
            )
            self.session.add(order)
        self.session.commit()

    def update_order_form(self, order_id, note, review_status):
        self.session.begin()
        if note:
            self.session.query(OrderForm).filter(
                OrderForm.id == order_id
            ).update({
                OrderForm.note: note
            })
        if review_status:
            self.session.query(OrderForm).filter(
                OrderForm.id == order_id
            ).update({
                OrderForm.review_status: review_status
            })
        self.session.commit()

    def query_all_order_form(self, telephone, community_id, review_status, page, size):
        query = self.session.query(OrderFormNew)
        if telephone:
           query = query.filter(OrderForm.telephone.like("%{}%".format(telephone)))
        if community_id or community_id == 0:
           query = query.filter(OrderForm.community_id==int(community_id))
        if review_status or review_status == 0:
            query = query.filter(
                OrderForm.review_status == int(review_status)
            )
        result = self.query_one_page(query, page, size)
        total = self.query_total(query)
        data = [row2dict(item) for item in result] if result else []
        for item in data:
            item["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item["created_at"]))
            item["order_form_detail"] = str(item['name']) + " " + str(item["telephone"]) + " " + str(item["community"]) + " " + item['address'] + " " + APARTMENT_DICT.get(item['apartment'], "") + " " + str(item['product'])
        return data, total

    def delete_order_form(self, order_ids):
        for id_ in order_ids:
            self.session.query(OrderForm).filter(OrderForm.id == int(id_)).delete()
