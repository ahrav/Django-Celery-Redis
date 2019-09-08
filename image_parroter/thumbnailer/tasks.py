import os
from typing import Any, Dict, List
from zipfile import ZipFile

from celery import shared_task
from django.conf import settings
from PIL import Image


@shared_task
def make_thumbnails(file_path: str, thumbnails: List = []) -> Dict[str, str]:
    """Creates thumbnail image with passed in image file and returns URL to to the zip archive of thumbnail"""

    os.chdir(settings.IMAGES_DIR)
    path, file = os.path.split(file_path)
    file_name, ext = os.path.splitext(file)

    zip_file: str = f'{file_name}.zip'
    results: Dict[str, str] = {
        'archive_path': f'{settings.MEDIA_URL}images/{zip_file}'
    }

    try:
        img: Image = Image.open(file_path)
        zipper: ZipFile = ZipFile(zip_file, 'w')
        os.remove(file_path)
        for w, h in thumbnails:
            img_copy: Image = img.copy()
            img_copy.thumbnail((w, h))
            thumbnail_file: str = f'{file_name}_{w}x{h}.{ext}'
            img_copy.save(thumbnail_file)
            zipper.write(thumbnail_file)
            os.remove(thumbnail_file)

        img.close()
        zipper.close()
    except IOError as e:
        print(e)

    return results
