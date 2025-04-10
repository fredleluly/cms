import os
import sys
import subprocess
import shutil
import logging
import datetime
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

# Default patterns to exclude from backup
DEFAULT_EXCLUDES = [
    '.git',
    '.github',
    '__pycache__',
    '*.pyc',
    '.idea',
    '.vscode',
    'venv',
    'env',
    'node_modules',
    'tmp',
    'temp',
    '*.log',
    '*.zip',
    '*.bak',
    '*.swp',
    '*.tmp',
]

def should_exclude(path, exclude_patterns, exclude_dirs):
    """
    Determine if a file or directory should be excluded from the backup.
    
    Args:
        path (str): Path to check
        exclude_patterns (list): List of patterns to exclude
        exclude_dirs (list): List of directories to exclude
    
    Returns:
        bool: True if the path should be excluded, False otherwise
    """
    path = Path(path)
    
    # Check if path is in excluded directories
    for dir_path in exclude_dirs:
        try:
            if os.path.abspath(path).startswith(os.path.abspath(dir_path)):
                return True
        except Exception:
            continue
    
    # Check if path matches any exclude pattern
    for pattern in exclude_patterns:
        # Simple pattern matching - could be enhanced with regex for more complex patterns
        if pattern.startswith('*') and path.name.endswith(pattern[1:]):
            return True
        elif pattern.endswith('*') and path.name.startswith(pattern[:-1]):
            return True
        elif pattern == path.name or pattern == str(path):
            return True
    
    return False

def get_project_size_estimation(exclude_patterns=None, exclude_dirs=None):
    """
    Estimate the size of the project for backup purposes.
    
    Args:
        exclude_patterns (list): List of patterns to exclude
        exclude_dirs (list): List of directories to exclude
    
    Returns:
        str: Human-readable string representing the estimated size
    """
    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDES
    
    if exclude_dirs is None:
        exclude_dirs = []
    
    project_root = os.path.abspath(settings.BASE_DIR)
    total_size = 0
    
    try:
        for root, dirs, files in os.walk(project_root):
            # Check if current directory should be excluded
            if should_exclude(root, exclude_patterns, exclude_dirs):
                dirs[:] = []  # Don't explore subdirectories
                continue
            
            # Filter dirs
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), exclude_patterns, exclude_dirs)]
            
            # Add file sizes
            for file in files:
                file_path = os.path.join(root, file)
                if not should_exclude(file_path, exclude_patterns, exclude_dirs):
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, FileNotFoundError):
                        # Skip files that can't be accessed
                        continue
    
    except Exception as e:
        logger.error(f"Error estimating project size: {str(e)}")
        return "Unknown"
    
    # Convert to human-readable format
    return format_size(total_size)

def check_available_space(required_space, target_dir):
    """
    Check if there's enough space in the target directory.
    
    Args:
        required_space (int): Required space in bytes
        target_dir (str): Target directory path
    
    Returns:
        bool: True if there's enough space, False otherwise
    """
    try:
        if not os.path.exists(target_dir):
            # Try to create target directory if it doesn't exist
            os.makedirs(target_dir, exist_ok=True)
        
        # Get free space in bytes
        free_space = shutil.disk_usage(target_dir).free
        
        # Check if there's enough space (with 10% buffer)
        return free_space > required_space * 1.1
    
    except Exception as e:
        logger.error(f"Error checking available space: {str(e)}")
        return False

def format_size(size_bytes):
    """
    Format size in bytes to human readable string.
    
    Args:
        size_bytes (int): Size in bytes
    
    Returns:
        str: Human-readable size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def backup_sqlite_database():
    """
    Create a backup of the SQLite database with the specified filename format.
    
    Returns:
        dict: Result dictionary with keys:
            - success (bool): Whether the backup was successful
            - filename (str): Name of the backup file (if successful)
            - path (str): Path to the backup file (if successful)
            - error (str): Error message (if unsuccessful)
    """
    try:
        # Get database path from Django settings
        if hasattr(settings, 'DATABASES') and 'default' in settings.DATABASES:
            db_settings = settings.DATABASES['default']
            if db_settings.get('ENGINE') == 'django.db.backends.sqlite3':
                db_path = db_settings.get('NAME')
                if db_path and os.path.exists(db_path):
                    # Create backup directory if it doesn't exist
                    backup_dir = os.path.join(settings.SECURE_DOWNLOAD_ROOT)
                    os.makedirs(backup_dir, exist_ok=True)
                    
                    # Generate filename with the requested format: db.sqlite3-2025-04-08---00-29
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d---%H-%M")
                    backup_filename = f"db.sqlite3-{timestamp}"
                    backup_path = os.path.join(backup_dir, backup_filename)
                    
                    # Copy the database file
                    shutil.copy2(db_path, backup_path)
                    
                    backup_size = os.path.getsize(backup_path)
                    backup_size_formatted = format_size(backup_size)
                    
                    logger.info(f"Database backup completed: {backup_path} ({backup_size_formatted})")
                    
                    return {
                        'success': True,
                        'filename': backup_filename,
                        'path': backup_path,
                        'size': backup_size_formatted
                    }
                else:
                    error_msg = f"SQLite database file not found at {db_path}"
                    logger.error(error_msg)
                    return {
                        'success': False,
                        'error': error_msg
                    }
            else:
                error_msg = "The project is not using SQLite database"
                logger.info(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
        else:
            error_msg = "Database settings not found"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    except Exception as e:
        logger.exception(f"Database backup failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def create_project_backup(backup_name=None, exclude_patterns=None, exclude_dirs=None, backup_db=True):
    """
    Create a backup of the project directory using the Linux zip command.
    
    Args:
        backup_name (str): Optional name for the backup file
        exclude_patterns (list): List of patterns to exclude
        exclude_dirs (list): List of directories to exclude
        backup_db (bool): Whether to create a separate backup of the SQLite database
    
    Returns:
        dict: Result dictionary with keys:
            - success (bool): Whether the backup was successful
            - filename (str): Name of the backup file (if successful)
            - path (str): Path to the backup file (if successful)
            - size (str): Human-readable size of the backup file (if successful)
            - error (str): Error message (if unsuccessful)
            - db_backup (dict): Database backup result (if backup_db is True)
    """
    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDES
    
    if exclude_dirs is None:
        exclude_dirs = []
    
    # Get project root directory and set up backup directory
    project_root = os.path.abspath(settings.BASE_DIR)
    backup_dir = os.path.join(settings.SECURE_DOWNLOAD_ROOT)
    
    try:
        # Create database backup if requested
        db_backup_result = None
        if backup_db:
            db_backup_result = backup_sqlite_database()
            if db_backup_result and db_backup_result.get('success'):
                logger.info(f"SQLite database backup created: {db_backup_result.get('filename')}")
            else:
                logger.warning("SQLite database backup failed or not applicable")
        
        # Verify that zip command is available
        try:
            subprocess.run(['zip', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.error(f"zip command not available: {str(e)}")
            return {
                'success': False,
                'error': "zip command not available on the server. Please contact the administrator.",
                'db_backup': db_backup_result
            }
        
        # Make sure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp if not provided
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if not backup_name:
            backup_name = f"project_backup_{timestamp}"
        elif not backup_name.endswith(".zip"):
            backup_name = f"{backup_name}_{timestamp}"
        
        if not backup_name.endswith(".zip"):
            backup_name += ".zip"
        
        backup_path = os.path.join(backup_dir, backup_name)
        
        # Create a temporary file with exclusion patterns
        exclude_file_path = os.path.join(backup_dir, f"temp_exclude_{timestamp}.txt")
        
        with open(exclude_file_path, 'w') as exclude_file:
            for pattern in exclude_patterns:
                exclude_file.write(f"{pattern}\n")
            
            # Add excluded directories
            for dir_path in exclude_dirs:
                if os.path.exists(dir_path):
                    # Convert to relative path from project root if possible
                    try:
                        rel_path = os.path.relpath(dir_path, project_root)
                        exclude_file.write(f"{rel_path}/*\n")
                    except ValueError:
                        # If not relative, add the full path
                        exclude_file.write(f"{dir_path}/*\n")
        
        logger.info(f"Starting backup to {backup_path}")
        
        # Build zip command
        # -r: recursive
        # -q: quiet (less verbose output)
        # -x@: exclude files listed in the file
        zip_cmd = [
            'zip', '-r', '-q',
            backup_path,
            '.',
            '-x@' + exclude_file_path
        ]
        
        # Change to project root and run zip command
        original_dir = os.getcwd()
        os.chdir(project_root)
        
        try:
            # Execute zip command
            process = subprocess.run(
                zip_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False  # Don't raise exception, we'll handle errors ourselves
            )
            
            # Check if command was successful
            if process.returncode != 0:
                error_msg = process.stderr or f"zip command failed with return code {process.returncode}"
                logger.error(f"Backup failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'db_backup': db_backup_result
                }
            
            # Get backup file size
            backup_size = os.path.getsize(backup_path)
            backup_size_formatted = format_size(backup_size)
            
            logger.info(f"Backup completed: {backup_path} ({backup_size_formatted})")
            
            result = {
                'success': True,
                'filename': backup_name,
                'path': backup_path,
                'size': backup_size_formatted,
                'db_backup': db_backup_result
            }
        
        finally:
            # Clean up
            os.chdir(original_dir)
            
            # Remove temporary exclusion file
            try:
                if os.path.exists(exclude_file_path):
                    os.remove(exclude_file_path)
            except Exception as e:
                logger.warning(f"Failed to remove temporary exclusion file: {str(e)}")
        
        return result
    
    except Exception as e:
        logger.exception(f"Backup failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'db_backup': db_backup_result if 'db_backup_result' in locals() else None
        }