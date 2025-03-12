# DUX Client Data Automation Script

This script automates the process of extracting client data from DUX ERP system and updating it to a Google Sheet.

## Recent Updates

### Error Handling and Notifications
- Added comprehensive try-catch blocks throughout the code
- Implemented email notification system for error reporting
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
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_specific_password
NOTIFICATION_EMAIL=recipient_email@example.com
```

3. Ensure you have the Google Sheets API credentials file (`file.json`)

## Features

- Automated login to DUX ERP system
- Data extraction from client tables
- Automatic pagination handling
- Google Sheets integration
- Error notification system via email
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

Note: For Gmail, you need to use an App-Specific Password rather than your regular account password.

## Dependencies

See `requirements.txt` for a complete list of dependencies.

