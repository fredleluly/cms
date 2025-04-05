### Core Components

1. **Backup Utility Functions** (`apps/pages/backup_utils.py`):
   - `create_project_backup()`: Creates a ZIP archive of the project using the Linux `zip` command.
   - `get_project_size_estimation()`: Estimates the size of the project.
   - `check_available_space()`: Checks if there's enough disk space.
   - `format_size()`: Formats byte sizes into human-readable format.
   - `should_exclude()`: Determines if files should be excluded from backup.

2. **Backup Views** (`apps/pages/views.py`):
   - `backup_project_view()`: Handles the backup form and process.
   - `backup_api_view()`: API endpoint for triggering backups programmatically and in the background.
   - `_perform_backup_in_background()`: Helper function to run backup in a separate thread.
   - Protected by `@superuser_required` decorator.

3. **Backup Templates** (`templates/admin/backup_project.html`):
   - Displays the backup form and results.
   - Shows progress indication during backup creation.
   - Provides download links for completed backups.

4. **File Browser Integration** (`templates/admin/file_browser.html`):
   - Allows triggering backups directly from the file browser interface.
   - Shows real-time feedback with toast notifications.
   - Runs backups in the background without blocking the UI.

5. **URL Configuration** (`project/urls.py`):
   - URL pattern for accessing the backup page: `/admin/backup-project/`.
   - API endpoint for background backups: `/admin/api/backup/`.

### Implementation Details

The backup feature uses the Linux `zip` command-line utility rather than Python's built-in zipfile module for better performance and compatibility with larger projects. Key implementation details include:

1. **Linux Zip Command**: 
   - Utilizes the system's native `zip` command for efficient compression.
   - Command is executed via Python's `subprocess` module.
   - Exclusion patterns are passed to `zip` using a temporary exclusion file.
   - Error handling captures both exit codes and stderr output.

2. **Background Processing**:
   - Backups can be triggered to run in a background thread.
   - Prevents web server timeouts for large projects.
   - Uses Python's threading module with daemon threads.
   - Progress is tracked in the server logs.

3. **File Browser Integration**:
   - Quick backup button in the file browser UI.
   - AJAX requests to the API endpoint.
   - Toast notifications for user feedback.
   - Seamless reloading to show new backup files.

### Security Considerations

- **Superuser Access**: Only superusers can access the backup page and create backups.
- **Secure Storage**: Backups are stored in the secure downloads directory, which requires a valid token to access.
- **Excluded Files**: Sensitive files and directories (like `.git`, `__pycache__`, etc.) are automatically excluded.
- **Disk Space Check**: The system checks for sufficient disk space before creating a backup.
- **Command Injection Prevention**: All user-provided inputs are properly sanitized before being used in commands.

### System Requirements

For the backup system to function properly, the following requirements must be met:

1. **Linux Operating System**: The server must be running a Linux distribution.
2. **Zip Command Available**: The `zip` command must be installed on the server.
3. **Sufficient Disk Space**: At least 2-3x the project size in free disk space.
4. **File Permissions**: The web server must have permission to execute the `zip` command and write to the backup directory.

To verify if the zip command is available, you can run:
```bash
which zip
# or
zip --version
```

If not installed, you can typically install it on Debian/Ubuntu with:
```bash
sudo apt-get update
sudo apt-get install zip
```

Or on CentOS/RHEL:
```bash
sudo yum install zip
```

### File Exclusions

The following files and directories are automatically excluded from backups:

- Version control directories (`.git`, `.github`)
- Cache directories (`__pycache__`)
- Python cache files (`*.pyc`)
- IDE configuration directories (`.idea`, `.vscode`)
- Virtual environments (`venv`, `env`)
- Node modules (`node_modules`)
- Temporary files and directories (`tmp`, `temp`, `*.tmp`)
- Log files (`*.log`)
- Existing archives (`*.zip`)
- Backup files (`*.bak`)
- Swap files (`*.swp`)

### Performance Considerations

- **Native Zip Command**: Using the system's native `zip` command is typically faster than Python's zipfile module.
- **Background Processing**: Backups run in a separate thread to avoid blocking web requests.
- **Progress Monitoring**: Background backups log progress for monitoring.
- **Temporary Files**: Uses temporary exclusion files that are automatically cleaned up.

### Troubleshooting

- **Error: "zip command not available"**: The `zip` command is not installed on the server. Install it using your distribution's package manager.
- **Error: "Not enough disk space"**: Free up disk space or reduce the backup scope by excluding database or media files.
- **Error: "Backup failed"**: Check the Django logs for detailed error information, particularly subprocess errors.
- **Missing Download Tokens**: Create a download token in the Download Tokens management page before creating a backup.
- **Slow Backup Process**: Large projects may take time to backup. Check the logs for progress updates. 