from .image import ImageDeleteHandler, ImageDownloadHandler, ImageUploadHandler

urls = [
    ("/api/image/upload", ImageUploadHandler),
    ("/api/image/download", ImageDownloadHandler),
    ("/api/image/delete", ImageDeleteHandler),
]