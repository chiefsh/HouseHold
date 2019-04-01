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
        select([func.count(Community.name)]).where(and_(Community.community_id == ProductBase.community_id)))


class ProductModel(MysqlModel):

    def add_product(self, product_id, name, category_id, group_price, market_price, charge_unit, group_member,
                    community_id, brief, sell_point, detail, transport_sale):
        self.session.begin()
        if product_id:
            self.session.query(ProductBase).filter(
                ProductBase.product_id == product_id
            ).update({
                ProductBase.name: name and name or ProductBase.name,
                ProductBase.category_id: category_id and category_id or ProductBase.category_id,
                ProductBase.group_price: group_price and group_price or ProductBase.group_price,
                ProductBase.market_price: market_price and market_price or ProductBase.market_price,
                ProductBase.charge_unit: charge_unit and charge_unit or ProductBase.charge_unit,
                ProductBase.group_member: group_member and group_member or ProductBase.group_member,
                ProductBase.community_id: community_id and community_id or ProductBase.community_id,
                ProductBase.brief: brief and brief or ProductBase.brief,
                ProductBase.sell_point: sell_point and sell_point or ProductBase.sell_point,
                ProductBase.detail: detail and detail or ProductBase.detail,
                ProductBase.transport_sale: transport_sale and transport_sale or ProductBase.transport_sale,
                ProductBase.created_at: int(time.time())
            }, synchronize_session=False)
        else:
            product = ProductBase(
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
            self.session.query(ProductBase).delete()
        else:
            for _id in product_ids:
                self.session.qeury(ProductBase).filter(
                    ProductBase.product_id == _id
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
