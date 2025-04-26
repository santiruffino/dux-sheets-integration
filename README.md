# DUX-GHL Contacts Integration

This script automates the integration between DUX ERP system and GHL (Go High Level) CRM, synchronizing client data and invoice information.

## Overview

The script performs the following main functions:
1. Extracts client data from DUX ERP system
2. Synchronizes client information with GHL CRM
3. Processes and updates invoice information
4. Maintains comprehensive logging of all operations
5. Sends error notifications via email

## Features

### Client Data Synchronization
- Automated login to DUX ERP system
- Extraction of client data from DUX tables
- Validation of client information
- Upsert operations to GHL CRM
- Custom field mapping between systems

### Invoice Processing
- Daily invoice data extraction
- Branch office-specific processing
- Contact updates with invoice information
- Custom field updates in GHL

### Error Handling & Logging
- Comprehensive error handling at all levels
- Daily rotating log files (7-day retention)
- Detailed API request/response logging
- Email notifications for critical errors
- Masked sensitive information in logs

## Technical Details

### Logging System
- Daily log rotation with 7-day retention
- Log files stored in `logs/` directory
- Format: `dux_script.log.YYYY-MM-DD.log`
- Log levels:
  - DEBUG: Detailed information (file only)
  - INFO: General progress information
  - ERROR: Error messages and stack traces

### API Integration
- DUX ERP API integration
- GHL CRM API integration
- Secure API key handling
- Request/response logging
- Error handling and retry logic

### Data Processing
- CSV file handling for client data
- JSON payload construction
- Data validation and sanitization
- Custom field mapping

## Setup

### Prerequisites
- Python 3.x
- Chrome browser (for Selenium)
- Access to DUX ERP system
- GHL CRM account and API credentials

### Environment Variables
Create a `.env` file with the following variables:
```env
# DUX Credentials
DUX_USERNAME=your_dux_username
DUX_PASSWORD=your_dux_password
DUX_API_KEY=your_dux_api_key
DUX_ID_EMPRESA=your_dux_company_id

# GHL Credentials
GHL_PRIVATE_INTEGRATION_KEY=your_ghl_api_key
GHL_LOCATION_ID=your_ghl_location_id

# Email Configuration
SMTP_SERVER=your.smtp.server
SMTP_PORT=465
SMTP_EMAIL=your_email@example.com
SMTP_PASSWORD=your_email_password
NOTIFICATION_EMAIL=recipient_email@example.com
```

### Installation
1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Script
```bash
python dux-ghl-contacts-integration.py
```

### Log Files
- Current log: `logs/dux_script.log`
- Daily logs: `logs/dux_script.log.YYYY-MM-DD.log`
- Log retention: 7 days

### Error Notifications
- Email notifications sent for critical errors
- Includes:
  - Error message
  - Stack trace
  - System information
  - Timestamp
  - Log file location

## Code Structure

### Main Functions

#### `main()`
- Entry point of the script
- Handles Selenium WebDriver setup
- Manages the overall execution flow
- Implements error handling and cleanup

#### `upsert_contacts()`
- Processes client data from CSV
- Creates/updates contacts in GHL
- Handles API requests and responses
- Tracks success/failure statistics

#### `search_invoices()`
- Fetches invoice data from DUX
- Processes invoices by branch office
- Updates contact information in GHL
- Handles pagination and rate limiting

#### `search_contact_by_id_cliente_dux()`
- Searches for contacts in GHL
- Matches by DUX client ID
- Handles API requests and responses
- Returns contact information

### Utility Functions

#### `setup_logging()`
- Configures logging system
- Sets up daily log rotation
- Configures log formats and levels
- Creates log directory structure

#### `send_error_email()`
- Sends error notifications
- Formats error messages
- Includes system information
- Handles SMTP connection

#### `log_api_request()`
- Logs API requests and responses
- Masks sensitive information
- Formats log messages
- Handles logging errors

#### `is_valid_email()`
- Validates email addresses
- Uses regex pattern matching
- Returns boolean result

## Error Handling

### Types of Errors Handled
1. API Connection Errors
2. Authentication Failures
3. Data Validation Errors
4. File System Errors
5. Network Timeouts
6. Rate Limiting Issues

### Error Recovery
- Automatic retries for transient errors
- Graceful degradation for non-critical errors
- Detailed error logging
- Email notifications for critical errors

## Best Practices

### Security
- API keys stored in environment variables
- Sensitive data masked in logs
- SSL/TLS for all connections
- Secure email transmission

### Performance
- Rate limiting implementation
- Efficient data processing
- Resource cleanup
- Memory management

### Maintenance
- Daily log rotation
- Error tracking
- Performance monitoring
- Regular updates

## Troubleshooting

### Common Issues
1. Authentication Failures
   - Check credentials in .env file
   - Verify API key validity
   - Check network connectivity

2. API Rate Limiting
   - Check log files for rate limit errors
   - Adjust request timing
   - Contact API provider if needed

3. File System Errors
   - Verify log directory permissions
   - Check disk space
   - Ensure file access rights

### Debugging
1. Check daily log files
2. Review error notifications
3. Verify environment variables
4. Test API connectivity
5. Monitor system resources

## Contributing

### Development
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Testing
1. Test in development environment
2. Verify error handling
3. Check log output
4. Validate API integration

## Support
[Email me](mailto:email@domain.com)