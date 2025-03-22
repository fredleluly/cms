# Secure download settings
SECURE_DOWNLOAD_ROOT = os.path.join(BASE_DIR, 'secure_downloads')
SECURE_DOWNLOAD_ALLOWED_EXTENSIONS = [
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.jpg', '.jpeg', '.png', '.gif', '.zip', '.rar', '.7z', '.tar', '.gz',
    '.txt', '.csv', '.json', '.xml'
]

# Ensure the secure downloads directory exists
import os
os.makedirs(SECURE_DOWNLOAD_ROOT, exist_ok=True) 