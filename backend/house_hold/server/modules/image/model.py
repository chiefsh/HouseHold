import os
import time
import sys

from core.utils import delete_image_file, check_file_exist
from settings.constant import BASE_IMAGE_PATH
from core.base_model import MysqlModel


class ImageModel(MysqlModel):

    def upload_image(self, imgfile):
        img_list = []
        for file in imgfile:
            # 避免重复文件名
            img_name = str(int(time.time() * 1000)) + "." + file['filename'].split('.')[-1]
            image_path = os.path.join(BASE_IMAGE_PATH, img_name)
            with open(image_path, 'wb') as f:
                f.write(file['body'])
            img_list.append(img_name)
        return img_list

    def download_image(self, image_name):
        if check_file_exist(image_name):
            with open(os.path.join(BASE_IMAGE_PATH, image_name), 'rb') as f:
                return f.read()
        else:
            return ''

    def delete_image(self, image_name):
        if check_file_exist(image_name):
            delete_image_file(image_name)
            return True

        else:
            return "{} 不存在"
