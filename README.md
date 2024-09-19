# Internet Connection Monitor

Created by Tatsu Ikeda, 2024

## Description

This Python script monitors your internet connection by pinging a specified server at regular intervals. It logs the connection status, sends email notifications when the connection is lost, and displays macOS notifications for status changes.

## Features

- Real-time connection status monitoring
- Email notifications on connection loss
- macOS desktop notifications for status changes (macOS only)
- Logging to both console and file
- Customizable check interval and target server
- Test email functionality

## Installation

1. Clone this repository or download the `internet_monitor.py` script.

2. It's recommended to use a virtual environment. Here's how to set it up:

   ```
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```
   pip install python-dotenv
   ```

   Note: The script will attempt to install `python-dotenv` automatically if it's not found.

## Configuration

1. Create a `.env` file in the same directory as the script with the following content:

   ```
   SMTP_SERVER=your_smtp_server
   SMTP_PORT=your_smtp_port
   SMTP_USERNAME=your_email@example.com
   SMTP_PASSWORD="your email password"
   RECIPIENT_EMAILS="email1@example.com, email2@example.com, email3@example.com"
   ```

   Replace the values with your actual SMTP server details and recipient email addresses. Note that:
   - The SMTP_PASSWORD is enclosed in double quotes, especially important if it contains special characters or spaces.
   - The RECIPIENT_EMAILS is enclosed in double quotes, with email addresses separated by commas and optional spaces after the commas.

2. Ensure the `.env` file has appropriate permissions to protect your sensitive information.

## Usage

1. Activate your virtual environment:

   ```
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

2. Run the script:

   ```
   python internet_monitor.py
   ```

3. Follow the prompts to enter the server to ping and the check interval.

4. To test the email functionality:

   ```
   python internet_monitor.py --test_email
   ```

## Logging

The script logs all activities to `~/internet_monitor.log`. You can review this file for a history of connection statuses and any issues that occurred.

## Platform-Specific Features

### macOS Notifications

On macOS systems, the script will attempt to display desktop notifications using the `osascript` command when the connection status changes. This feature is not available on non-macOS systems.

## License

This project is licensed under the MIT License.

Copyright (c) 2024 Tatsu Ikeda

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Troubleshooting

- If you're having issues with email notifications, ensure your SMTP settings are correct and that your email provider allows SMTP access for your account.
- For Gmail users, you may need to use an "App Password" instead of your regular password.
- If the script fails to run, ensure you're using Python 3.6 or later.
- Check the log file (`~/internet_monitor.log`) for any error messages or unexpected behavior.
- If you're not seeing macOS notifications:
  - Ensure you're running the script on a macOS system.
  - Check your macOS notification settings to allow notifications from the Terminal or your Python environment.
  - If you're running the script in a virtual environment, make sure it has the necessary permissions to send notifications.

## Contributing

While this is a personal project, suggestions and improvements are welcome. Please feel free to fork the repository and submit pull requests.