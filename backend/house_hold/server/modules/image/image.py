import logging

from core.base_handler import BaseHandler, arguments, authenticated
from core.exception import NotFound, ParametersError
from .model import ImageModel


class ImageUploadHandler(BaseHandler):

    @arguments
    def post(self, model: ImageModel = None):
        imgfile = self.request.files.get('files')
        if not imgfile:
            raise ParametersError("参数错误")
        img_name = model.upload_image(imgfile)
        self.finish({
            "code": 0,
            "msg": "success",
            "data": {"image_name": img_name}
        })


class ImageDownloadHandler(BaseHandler):

    def get(self, image_name: str = "", model: ImageModel = None):
        if not image_name:
            raise ParametersError("参数错误")
        result = model.download_image(image_name)
        self.write(result)


class ImageDeleteHandler(BaseHandler):

    def delete(self, image_name: str = "", model: ImageModel = None):
        if not image_name:
            raise ParametersError("参数错误")
        result = model.delete_image(image_name)
        if result is not True:
            raise ParametersError(result)
        self.finish({
            "code": 0,
            "msg": "success"
        })