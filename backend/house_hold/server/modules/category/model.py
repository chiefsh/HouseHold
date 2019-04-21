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
            query = self.session.query(Category).order_by(Category.is_top.desc(), Category.created_at.desc())
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

    def handle_is_top(self, category_id, is_top):
        if is_top:
            self.session.begin()
            self.session.query(Category.is_top).filter(Category.is_top == 10).update({
                Category.is_top: 0
            },  synchronize_session=False)
            self.session.query(Category.is_top).filter(Category.category_id == category_id).update({
                Category.is_top: 10
            }, synchronize_session=False)
            self.session.commit()

    def sort_category_list(self, above_category_id, under_category_id):
        above = self.session.query(Category.created_at, Category.is_top).filter(Category.category_id == above_category_id).first()
        under = self.session.query(Category.created_at).filter(Category.category_id == under_category_id).first()
        if not (above and under):
            return
        if above[1] == 10:
            self.session.begin()
            self.session.query(Category.is_top).filter(Category.category_id == above_category_id).update({
                Category.is_top : 0
            }, synchronize_session=False)
            self.session.commit()
        above = above[0]
        under = under[0]
        self.session.begin()
        self.session.query(Category.created_at).filter(Category.category_id == above_category_id).update({
            Category.created_at: under
        }, synchronize_session=False)
        self.session.commit()
        self.session.begin()
        self.session.query(Category.created_at).filter(Category.category_id == under_category_id).update({
            Category.created_at: above
        }, synchronize_session=False)
        self.session.commit()

