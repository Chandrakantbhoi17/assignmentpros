import os
import uuid
from django.conf import settings
from django.core.files.storage import FileSystemStorage


def task_file_upload_path(instance, filename):
    ext = os.path.splitext(filename)[-1].lower()
    new_filename = f"{uuid.uuid4()}{ext}"
    return f"tasks/{new_filename}"  # Optional: use task ID if available


protected_storage = FileSystemStorage(location=settings.PROTECTED_MEDIA_ROOT)

