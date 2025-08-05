# Scripts Directory

This directory contains all development, testing, and debugging scripts for the EmbeddedChat project.

## Directory Structure

### 📁 `test/`
Contains all testing scripts and files:
- `test_*.py` - Unit and integration tests
- `*_test.py` - Various test implementations
- `demo_*.py` - Demo and showcase scripts
- `final_*.py` - Final testing implementations
- `basic_*.py` - Basic functionality tests
- `complete_*.py` - Complete workflow tests
- `simple_*.py` - Simple test cases
- Email testing scripts
- Workflow testing scripts

### 📁 `debug/`
Contains all debugging and troubleshooting scripts:
- `debug_*.py` - Debug implementations
- `quick_*.py` - Quick debugging scripts
- `fix_*.py` - Bug fix testing scripts
- `localStorage*.js` - Frontend debugging tools
- `debug-*.js` - JavaScript debugging utilities
- `*.log` - Debug log files

### 📁 `check/`
Contains all system checking and validation scripts:
- `check_*.py` - System status checking scripts
- Backend component verification
- Database connectivity checks
- API endpoint validation
- Configuration verification

### 📁 `setup/`
Contains all setup and configuration scripts:
- `setup_*.py` - System setup scripts
- Database initialization
- OAuth configuration
- Email setup
- Google Services configuration

## Usage

### Running Tests
```bash
# Run specific test
python scripts/test/test_workflow.py

# Run email tests
python scripts/test/test_email_automation.py
```

### Debug Scripts
```bash
# Debug workflow execution
python scripts/debug/debug_workflow_execution.py

# Quick debug check
python scripts/debug/quick_debug_flow.py
```

### System Checks
```bash
# Check backend status
python scripts/check/check_backend_status.py

# Check database connection
python scripts/check/check_database.py
```

### Setup Scripts
```bash
# Setup email configuration
python scripts/setup/setup_email.py

# Setup Google Sheets
python scripts/setup/setup_google_sheets.py
```

## Note

These scripts are development utilities and should not be included in production deployments. They are maintained here for:

- Development testing
- System debugging
- Configuration verification
- Quick prototyping
- Issue troubleshooting

## Maintenance

Scripts in this directory may contain:
- Hardcoded test data
- Development-only configurations
- Experimental features
- Legacy implementations

Please review and update scripts as needed when making system changes.
