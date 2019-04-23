import math
import time
from sqlalchemy.orm import relationship, joinedload, lazyload, column_property, foreign, aliased
from sqlalchemy import select, outerjoin, or_, func, and_, between, desc, join

from core.base_model import MysqlModel
from core.schema import Category, Product, OrderForm, Community
from core.utils import row2dict

APARTMENT_DICT = {0: "一居室", 1: "二居室", 2: "三居室"}


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
            query = query.filter(OrderForm.community_id == int(community_id))
        if review_status or review_status == 0:
            query = query.filter(
                OrderForm.review_status == int(review_status)
            )
        query = query.order_by(OrderForm.created_at.desc())
        result = self.query_one_page(query, page, size)
        total = self.query_total(query)
        data = [row2dict(item) for item in result] if result else []
        for item in data:
            item["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item["created_at"]))
            item["order_form_detail"] = str(item['name']) + " " + str(item["telephone"]) + " " + str(
                item["community"]) + " " + item['address'] + " " + APARTMENT_DICT.get(item['apartment'],
                                                                                      "") + " " + str(item['product'])
        return data, total

    def delete_order_form(self, order_ids):
        for id_ in order_ids:
            self.session.query(OrderForm).filter(OrderForm.id == int(id_)).delete()

    def _get_total_order_num(self, product_id):
        return self.session.query(func.count(OrderForm.id)).filter(OrderForm.product_id == product_id).scalar()

    def _get_pass_order_num(self, product_id):
        return self.session.query(func.count(OrderForm.id)).filter(and_(OrderForm.product_id == product_id,
                                                                        OrderForm.review_status == 1)).scalar()

    def _get_newest_orders(self, product_id):
        order_list = self.session.query(OrderFormNew).filter(and_(
            OrderForm.product_id == product_id,
            OrderForm.review_status == 1
        )).order_by(
            OrderForm.created_at.desc()
        ).limit(5).all()
        detail_list = list()
        order_list = [row2dict(item) for item in order_list] if order_list else []
        for item in order_list:
            name = str(item['name']).replace(str(item['name'])[1:], len(str(item['name'])[1:]) * "*")
            telephone = str(item["telephone"]).replace(str(item['telephone'])[3:8], 4 * "*") if len(
                str(item["telephone"])) >= 11 else str(item["telephone"])
            detail_list.append(str(item["community"]) + "的" + name + ", " + telephone + ", 拼团成功！")
        return detail_list

    def _format_product(self, product):
        product_id = product['product_id']
        product['total_order'] = self._get_total_order_num(product_id)
        product['pass_order'] = self._get_pass_order_num(product_id)
        product['current_round_pass'] = product['pass_order'] % product['group_number']
        product['round'] = math.ceil(product['pass_order'] / product['group_number']) + 1 if product[
                                                                                                 'current_round_pass'] == 0 else math.ceil(
            product['pass_order'] / product['group_number'])  # 轮数
        product['remain_num'] = product['group_number'] - product['current_round_pass']
        product['newest_orders'] = self._get_newest_orders(product_id)
        return product

    def get_group_order_form_info(self, community_id, category_id, product_id):
        if product_id is None or not product_id:
            query = self.session.query(Product.product_id, Product.name, Product.category_ids, Product.image_0,
                                       Product.image_1,
                                       Product.image_2, Product.image_3, Product.image_4,
                                       Product.community_id, Product.group_number, Product.group_price,
                                       Product.market_price,
                                       Product.charge_unit, Product.rate)
            if community_id:
                query = query.filter(Product.community_id.like("%{}%".format(str(community_id))))
            if category_id:
                query = query.filter(Product.category_ids.like("%{}%".format(str(category_id))))
            product_list = query.order_by(
                Product.is_top.desc(), Product.created_at.desc()
            ).all()
            # product_list = [row2dict(product) for product in product_list] if product_list else []
            product_list = [{"product_id": item[0], "name": item[1], "category_ids": item[2], "image_0": item[3],
                             "image_1": item[4], "image_2": item[5], "image_3": item[6], "image_4": item[7],
                             "community_id": item[8], "group_number": item[9], "group_price": item[10],
                             "market_price": item[11], "charge_unit": item[12], "rate": item[13]} for item in
                            product_list] if product_list else []
            for product in product_list:
                self._format_product(product)

            return product_list
        else:
            query = self.session.query(Product)
            product = query.filter(Product.product_id == product_id).first()
            if not product:
                return ''
            else:
                product = row2dict(product)
            return self._format_product(product)
