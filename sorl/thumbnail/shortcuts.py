from sorl.thumbnail.images import ImageFile
from sorl.thumbnail import default


def delete(file_, delete_file=True):
    image_file = ImageFile(file_)
    if delete_file:
        image_file.delete()
    default.kvstore.delete(image_file)

