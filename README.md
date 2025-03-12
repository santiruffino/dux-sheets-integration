# DUX Client Data Automation Script

This script automates the process of extracting client data from DUX ERP system and updating it to a Google Sheet.

## Recent Updates

### Error Handling and Notifications
- Added comprehensive try-catch blocks throughout the code
- Implemented email notification system for error reporting using SSL connection
- Errors are now caught at both main execution and table iteration levels

### Logging System
- Added detailed logging functionality with both file and console output
- Logs are stored in the `logs` directory
- Implemented rotating log files (5MB max size, 5 backup files)
- Different log levels:
  - DEBUG: Detailed information (file only)
  - INFO: General progress information (console and file)
  - ERROR: Error messages and stack traces (console and file)

## Setup

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with the following variables:
```
DUX_USERNAME=your_dux_username
DUX_PASSWORD=your_dux_password
SMTP_EMAIL=your_email@example.com
SMTP_PASSWORD=your_email_password
NOTIFICATION_EMAIL=recipient_email@example.com
SMTP_SERVER=your.smtp.server  # default: c1850991.ferozo.com
SMTP_PORT=465  # default: 465 for SSL
```

3. Ensure you have the Google Sheets API credentials file (`dux-integration-api-5f2a21be17a1.json`)

## Features

- Automated login to DUX ERP system
- Data extraction from client tables
- Automatic pagination handling
- Google Sheets integration
- Error notification system via email (SSL)
- Comprehensive logging system
- Automatic cleanup of resources

## Logging

Logs are stored in the `logs` directory:
- Main log file: `logs/dux_script.log`
- Rotating backup files: `dux_script.log.1` through `dux_script.log.5`
- Console output shows INFO level and above
- File logs contain complete DEBUG level information

## Error Notifications

The script will send email notifications when errors occur, including:
- Full error message
- Stack trace
- Timestamp of the error

The email notifications are sent using a secure SSL connection to the SMTP server.

## Dependencies

See `requirements.txt` for a complete list of dependencies.

## Links de Interes
- https://github.com/password123456/setup-selenium-with-chrome-driver-on-ubuntu_debian?tab=readme-ov-file#step-2-download-google-chrome-stable-package