import os
import uuid
import platform
from django.core.files.storage import FileSystemStorage

def task_file_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    return new_filename

# Detect OS and set base path
if platform.system() == "Windows":
    base_path = r"C:/assignmentpros/protected/task_files"
else:  # Linux / macOS (Ubuntu, etc.)
    base_path = "/home/ubuntu/assignmentpros/protected/task_files"

# Create the directory if it does not exist
os.makedirs(base_path, exist_ok=True)

# Protected storage
protected_storage = FileSystemStorage(location=base_path)
