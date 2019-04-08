import time

from core.base_model import MysqlModel
from core.schema import Category
from core.utils import row2dict


class CategoryModel(MysqlModel):

    def add_category(self, category_id, name):
        self.session.begin()
        if category_id is None:
            category = Category(
                name=name,
                created_at=int(time.time())
            )
            self.session.add(category)
        else:
            self.session.query(Category).filter(
                Category.category_id == category_id
            ).update({
                Category.name: name
            }, synchronize_session=False)
        self.session.commit()

    def query_category(self, category_id, page, size):
        if category_id is None:
            query = self.session.query(Category)
            result = self.query_one_page(query, page, size)
            data = [row2dict(item) for item in result] if result else []
            total = self.query_total(query)
        else:
            result = self.session.query(Category).filter(
                Category.category_id == category_id
            ).first()
            data = row2dict(result) if result else ''
            total = 0
        return data, total

    def delete_category(self, category_id):
        self.session.query(Category).filter(Category.category_id == category_id).delete()
