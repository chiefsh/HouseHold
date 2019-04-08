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
    def delete(self, category_id: int = None, model: CategoryModel = None):
        if category_id is None:
            raise ParametersError()
        model.delete_category(category_id)
        self.finish({
            "code": 0,
            "msg": '操作成功',
        })
