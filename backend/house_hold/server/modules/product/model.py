import time
from sqlalchemy.orm import relationship, joinedload, lazyload, column_property, foreign, aliased
from sqlalchemy import select, outerjoin, or_, func, and_, between, desc, join

from core.base_model import MysqlModel
from core.schema import Product as ProductBase, Community, Category
from core.utils import row2dict


class Product(ProductBase):
    category = column_property(
        select([func.count(Category.name)]).where(and_(Category.category_id == ProductBase.category_id)))

    community = column_property(
        select([func.count(Community.name)]).where(and_(Community.community_id == ProductBase.community)))


class ProductModel(MysqlModel):

    def add_product(self, product_id, name, category_id, group_price, market_price, charge_unit, group_member,
                    community_id, brief, sell_point, detail, transport_sale):
        self.session.begin()
        if product_id:
            self.session.query(Product).filter(
                Product.product_id == product_id
            ).update({
                Product.name: name and name or Product.name,
                Product.category_id: category_id and category_id or Product.category_id,
                Product.group_price: group_price and group_price or Product.group_price,
                Product.market_price: market_price and market_price or Product.market_price,
                Product.charge_unit: charge_unit and charge_unit or Product.charge_unit,
                Product.group_member: group_member and group_member or Product.group_member,
                Product.community_id: community_id and community_id or Product.community_id,
                Product.brief: brief and brief or Product.brief,
                Product.sell_point: sell_point and sell_point or Product.sell_point,
                Product.detail: detail and detail or Product.detail,
                Product.transport_sale: transport_sale and transport_sale or Product.transport_sale,
                Product.created_at: int(time.time())
            }, synchronize_session=False)
        else:
            product = Product(
                name=name,
                category_id=category_id,
                group_price=group_price,
                market_price=market_price,
                charge_unit=charge_unit,
                group_member=group_member,
                community_id=community_id,
                brief=brief,
                sell_point=sell_point,
                detail=detail,
                transport_sale=transport_sale,
                created_at=int(time.time())
            )
            self.session.add(product)
        self.session.commit()

    def delete_product(self, product_ids):
        self.session.begin()
        if not product_ids:
            self.session.query(Product).delete()
        else:
            for _id in product_ids:
                self.session.qeury(Product).filter(
                    Product.product_id == _id
                ).delete()
        self.session.commit()

    def query_one_page(self, product_id, page, size):
        # 带转换类型和社区名，relationship
        if product_id is None:
            query = self.session.qeury(Product)
            result = self.query_one_page(query, page, size)
            return [row2dict(item) for item in result] if result else []
        else:
            result = self.session.qeury(Product).filter(
                Product.product_id == product_id
            ).first()
            return row2dict(result) if result else ''
