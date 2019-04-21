from core.base_handler import BaseHandler, arguments, authenticated
from core.exception import NotFound, ParametersError
from .model import CategoryModel


class CategoryAddHandler(BaseHandler):

    @authenticated
    @arguments
    def post(self, category_id: int = None, name: str = "", model: CategoryModel = None):
        if not name:
            raise ParametersError("类型名称不能为空")
        model.add_category(category_id, name)
        self.finish({
            "code": 0,
            "msg": 'success',
        })


class CategoryQueryHandler(BaseHandler):

    @arguments
    def get(self, category_id: int = None, page: int = 0, size: int = 20, model: CategoryModel = None):
        data, total = model.query_category(category_id, page, size)
        self.finish({
            "code": 0,
            "msg": 'success',
            "data": data,
            "total": total
        })


class CategoryDeleteHandler(BaseHandler):

    @authenticated
    @arguments
    def post(self, category_ids: str = None, model: CategoryModel = None):
        if category_ids is None:
            raise ParametersError()
        category_ids = category_ids.split(",")
        model.delete_category(category_ids)
        self.finish({
            "code": 0,
            "msg": '操作成功',
        })


class CategoryIsTopHandler(BaseHandler):

    @authenticated
    @arguments
    def post(self, category_id: int = None, is_top: int = None, model: CategoryModel = None):
        if not category_id:
            raise ParametersError()
        model.handle_is_top(category_id, is_top)
        self.finish({
            "code": 0,
            "msg": '操作成功',
        })

class CategorySortHandler(BaseHandler):

    @authenticated
    @arguments
    def post(self, above_category_id: int = None, under_category_id: int = None, model: CategoryModel = None):
        if not above_category_id or not under_category_id:
            raise ParametersError()
        model.sort_category_list(above_category_id, under_category_id)
        self.finish({
            "code": 0,
            "msg": '操作成功',
        })
