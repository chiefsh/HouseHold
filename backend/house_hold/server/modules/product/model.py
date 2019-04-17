import time
from sqlalchemy.orm import relationship, joinedload, lazyload, column_property, foreign, aliased
from sqlalchemy import select, outerjoin, or_, func, and_, between, desc, join

from core.base_model import MysqlModel
from core.schema import Product as ProductBase, Community, Category, ObjID
from core.utils import row2dict


class Product(ProductBase):
    #category = column_property(
    #    select([Category.name]).where(and_(Category.category_id == ProductBase.category_id))

    community = column_property(
        select([Community.name]).where(and_(Community.community_id == ProductBase.community_id)))


class ProductModel(MysqlModel):

    def add_product(self, product_id, name, category_id, group_price, market_price, rate, charge_unit, group_member,
                          community_id, brief, sell_point, detail, transport_sale, introduction, image_0, image_1,
                          image_2, image_3, image_4):
        self.session.begin()
        if product_id:
            self.session.query(ProductBase).filter(
                ProductBase.product_id == product_id
            ).update({
                ProductBase.name: name and name or ProductBase.name,
                ProductBase.category_ids: category_id and category_id or ProductBase.category_ids,
                ProductBase.group_price: group_price and group_price or ProductBase.group_price,
                ProductBase.market_price: market_price and market_price or ProductBase.market_price,
                ProductBase.rate: rate and rate or ProductBase.rate,
                ProductBase.charge_unit: charge_unit and charge_unit or ProductBase.charge_unit,
                ProductBase.group_number: group_member and group_member or ProductBase.group_number,
                ProductBase.community_id: community_id and community_id or ProductBase.community_id,
                ProductBase.brief: brief and brief or ProductBase.brief,
                ProductBase.sell_point: sell_point and sell_point or ProductBase.sell_point,
                ProductBase.detail: detail and detail or ProductBase.detail,
                ProductBase.transport_sale: transport_sale and transport_sale or ProductBase.transport_sale,
                ProductBase.introduction: introduction and introduction or ProductBase.introduction,
                ProductBase.image_0: image_0 and image_0 or ProductBase.image_0,
                ProductBase.image_1: image_1 and image_1 or ProductBase.image_1,
                ProductBase.image_2: image_2 and image_2 or ProductBase.image_2,
                ProductBase.image_3: image_3 and image_3 or ProductBase.image_3,
                ProductBase.image_4: image_4 and image_4 or ProductBase.image_4,
                ProductBase.created_at: int(time.time())
            }, synchronize_session=False)
        else:
            product = ProductBase(
                product_id= ObjID.new_id(),
                name=name,
                category_ids=category_id,
                group_price=group_price,
                market_price=market_price,
                charge_unit=charge_unit,
                group_number=group_member,
                community_id=community_id,
                rate=rate,
                brief=brief,
                sell_point=sell_point,
                detail=detail,
                transport_sale=transport_sale,
                introduction=introduction,
                image_0=image_0,
                image_1=image_1,
                image_2=image_2,
                image_3=image_3,
                image_4=image_4,
                created_at=int(time.time())
            )
            self.session.add(product)
        self.session.commit()

    def delete_product(self, product_ids):
        self.session.begin()
        for _id in product_ids:
            self.session.query(ProductBase).filter(
                ProductBase.product_id == _id
            ).delete()
        self.session.commit()

    def query_product(self, product_id, page, size):
        # 带转换类型和社区名，relationship
        if product_id is None:
            count = self.session.query(func.count(Product.product_id)).scalar()
            query = self.session.query(Product).order_by(Product.is_top.desc(), Product.rank.asc(), Product.product_id)
            result = self.query_one_page(query, page, size)
            data = [row2dict(item) for item in result] if result else []
            for item in data:
                import json
                ids = item["category_ids"].split(",")
                item["categorys"] = []
                for id in ids:
                    name = self.session.query(Category.name).filter(Category.category_id==int(id)).first()
                    item["categorys"].append(name[0] if name else '')
                item["categorys"] = json.dumps(item["categorys"])
                item["category_id"]=json.dumps(item["category_ids"].split(","))
            return data, count
        else:
            result = self.session.query(Product).filter(
                Product.product_id == product_id
            ).first()
            data = row2dict(result) if result else ''
            if data:
                data['category_id'] = data['category_ids'].split(",")
            return data, 0

    def top_product(self, product_id, is_top):
        if is_top:
            self.session.begin()
            self.session.query(ProductBase).filter(
                ProductBase.product_id == product_id
            ).update({
                ProductBase.is_top: int(time.time())
            }, synchronize_session=False)
            self.session.commit()

    def sorted_product_list(self, above_product_id, under_product_id):
        self.session.begin()
        above_rank = self.session.query(ProductBase.rank).filter(ProductBase.product_id == above_product_id).first()
        under_rank = self.session.query(ProductBase.rank).filter(ProductBase.product_id == under_product_id).first()
        if not (above_rank and under_rank):
            return
        self.session.query(ProductBase.rank).filter(ProductBase.product_id == above_product_id).update({
            ProductBase.rank: under_rank[0]
        }, synchronize_session=False)
        self.session.query(ProductBase.rank).filter(ProductBase.product_id == under_product_id).update({
            ProductBase.rank: above_rank[0]
        }, synchronize_session=False)
        self.session.flush()

