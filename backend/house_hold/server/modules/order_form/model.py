import time
from sqlalchemy.orm import relationship, joinedload, lazyload, column_property, foreign, aliased
from sqlalchemy import select, outerjoin, or_, func, and_, between, desc, join

from core.base_model import MysqlModel
from core.schema import Category, Product, OrderForm, Community
from core.utils import row2dict


class OrderFormNew(OrderForm):
    community = column_property(
        select([func.count(Community.name)]).where(and_(Community.community_id == OrderForm.community_id)))


class OrderFormModel(MysqlModel):

    def add_order_form(self, name, telephone, community_id, address, apartment, product_ids):
        self.session.begin()
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

    def query_all_order_form(self, review_status, page, size):
        query = self.session.query(OrderFormNew).filter(
            OrderForm.review_status == review_status
        )
        result = self.query_one_page(query, page, size)
        return [row2dict(item) for item in result] if result else []

    def delete_order_form(self, order_ids):
        for id_ in order_ids:
            self.session.query(OrderForm).filter(OrderForm.id == int(id_)).delete()
