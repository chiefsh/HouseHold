import time

from core.base_model import MysqlModel
from core.schema import Product
from core.utils import row2dict


class ProductModel(MysqlModel):

    def add_product(self, product_id, name, category_id, group_price, market_price, charge_unit, group_member,
                    community_id, brief, sell_point, detail, transport_sale):
        self.session.begin()
        if product_id:
            self.session.query(ProductModel).filter(
                ProductModel.product_id == product_id
            ).update({
                ProductModel.name: name and name or ProductModel.name,
                ProductModel.category_id: category_id and category_id or ProductModel.category_id,
                ProductModel.group_price: group_price and group_price or ProductModel.group_price,
                ProductModel.market_price: market_price and market_price or ProductModel.market_price,
                ProductModel.charge_unit: charge_unit and charge_unit or ProductModel.charge_unit,
                ProductModel.group_member: group_member and group_member or ProductModel.group_member,
                ProductModel.community_id: community_id and community_id or ProductModel.community_id,
                ProductModel.brief: brief and brief or ProductModel.brief,
                ProductModel.sell_point: sell_point and sell_point or ProductModel.sell_point,
                ProductModel.detail: detail and detail or ProductModel.detail,
                ProductModel.transport_sale: transport_sale and transport_sale or ProductModel.transport_sale,
                ProductModel.created_at: int(time.time())
            }, synchronize_session=False)
        else:
            product = ProductModel(
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
            self.session.query(ProductModel).delete()
        else:
            for _id in product_ids:
                self.session.qeury(ProductModel).filter(
                    ProductModel.product_id == _id
                ).delete()
        self.session.commit()

    def query_one_page(self, page, size):
        # 带转换类型和社区名，relationship
        query = self.session.qeury(ProductModel)
        result = self.query_one_page(query, page, size)
        return [row2dict(item) for item in result] if result else []
