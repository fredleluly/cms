# Secure File Downloads

## Overview

This module provides a secure way to serve files for download only to authorized superusers. It uses dynamic, randomly generated tokens in URLs to prevent unauthorized access and directory listing.

## Features

1. **Token-Based Security**: Access to files requires a valid token in the URL
2. **Dynamic URLs**: URLs are not predictable and include random tokens
3. **Superuser-Only Access**: Only superusers can access the download area
4. **Directory Listing**: Browse directories and download files through a web interface
5. **Token Management**: Create, activate/deactivate, and delete access tokens
6. **Path Traversal Protection**: Prevents attackers from accessing files outside the designated download area

## Setup

1. The feature stores tokens in the database via the `DownloadToken` model
2. Set the `SECURE_DOWNLOAD_ROOT` in settings.py to point to your secure files directory
3. Run migrations to create the required database tables
4. Configure URLs to include the secure file browser routes

## Usage

### Managing Tokens

1. Go to `/admin/download-tokens/` (Superuser only)
2. Create a new token with a descriptive name
3. The generated token URL will look like: `/secure-files/abcd1234.../`
4. Share this URL only with authorized superusers

### Browsing Files

1. Navigate to the token URL, e.g., `/secure-files/abcd1234.../`
2. The interface shows all files and directories in the secure download area
3. Click on directories to navigate, and files to download them
4. The breadcrumb navigation helps you keep track of your location

### Security Considerations

- All access is logged
- Only superusers can access files, even with a valid token
- The token page shows who created each token and when
- Inactive or expired tokens will not work
- Path traversal attempts are blocked and logged

## Implementation Details

### Models

- `DownloadToken`: Stores token information, description, expiry date, and active status

### Views

- `secure_file_browser`: Main view to browse and download files
- `manage_download_tokens`: View to manage tokens (create, activate/deactivate, delete)

### Utilities

- `superuser_required`: Decorator to restrict access to superusers
- `safe_join_paths`: Safely join paths to prevent path traversal attacks
- `get_file_details`: Get details about files for directory listing

### Templates

- `admin/file_browser.html`: Display files and directories
- `admin/download_tokens.html`: Manage download tokens

## Troubleshooting

If you encounter issues:

1. Verify the `SECURE_DOWNLOAD_ROOT` directory exists and has proper permissions
2. Check that the token is active and not expired
3. Ensure the user is a superuser
4. Review logs for any security-related messages

## Security Best Practices

1. Regularly rotate tokens for sensitive data
2. Set expiry dates on tokens for temporary access
3. Use HTTPS for all file transfers
4. Do not store sensitive files in publicly accessible directories
5. Keep the token URLs confidential 