import shutil
from pathlib import Path

from fastapi import UploadFile


async def save_upload_file_tmp(upload_file: UploadFile) -> Path:
    try:
        file_name = upload_file.filename
        current_dir = Path.cwd()
        file_path = current_dir / file_name

        with open(file_path, 'wb') as f:
            shutil.copyfileobj(upload_file.file, f)
    finally:
        upload_file.file.close()

    return file_path