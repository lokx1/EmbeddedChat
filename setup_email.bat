@echo off
echo ================================================================
echo 📧 EMAIL SETUP - EmbeddedChat System
echo ================================================================
echo.

echo 🔧 Installing required packages...
pip install aiosmtplib pydantic[email]

echo.
echo 📝 Running email setup guide...
python setup_email.py

echo.
echo ✅ Email setup complete!
pause
