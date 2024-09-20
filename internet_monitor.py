import sys
import os
import subprocess
import time
from datetime import datetime
import traceback
import argparse
import logging
from collections import deque

def install_dependencies():
    dependencies = ['python-dotenv']
    for package in dependencies:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} has been installed.")

# Install dependencies
install_dependencies()

# Now we can safely import from dotenv
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set up logging
LOG_FILE = os.path.join(os.path.expanduser("~"), "internet_monitor.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def get_env_value(key):
    value = os.getenv(key)
    if value and value.startswith('"') and value.endswith('"'):
        return value[1:-1]  # Remove surrounding quotes
    return value

# Load environment variables
print(f"Current working directory: {os.getcwd()}")
env_path = os.path.join(os.getcwd(), '.env')
print(f"Attempting to load .env file from: {env_path}")

if os.path.exists(env_path):
    print(".env file found")
    load_dotenv(env_path)
    with open(env_path, 'r') as f:
        print("Contents of .env file:")
        print(f.read())
else:
    print(".env file not found")

print("Environment variables after loading .env:")
for key in ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_USERNAME', 'RECIPIENT_EMAILS']:
    value = get_env_value(key)
    print(f"{key}={value}")

def send_notification(title: str, message: str):
    """Log notification instead of using macOS notifications"""
    logging.info(f"Notification: {title} - {message}")

def send_email(subject: str, body: str, to_email: str):
    msg = MIMEMultipart()
    msg['From'] = get_env_value('SMTP_USERNAME')
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(get_env_value('SMTP_SERVER'), int(get_env_value('SMTP_PORT'))) as server:
            server.starttls()
            server.login(get_env_value('SMTP_USERNAME'), get_env_value('SMTP_PASSWORD'))
            server.send_message(msg)
        logging.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

class ConnectionMonitor:
    def __init__(self, interval: int, host: str, to_emails: list):
        self.interval = interval
        self.host = host
        self.running = True
        self.to_emails = to_emails
        self.check_count = 0
        self.email_queue = deque()

    def run(self):
        last_status = None
        logging.info(f"Starting connection monitoring to {self.host} every {self.interval} seconds.")
        print("Press Ctrl+C to stop.\n")
        while self.running:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_status = self.check_connection()
            self.check_count += 1
            
            status_str = "Connected" if current_status else "Disconnected"
            logging.info(f"Status: {status_str} (Check #{self.check_count})")
            
            if current_status != last_status:
                self.log_status_change(current_status)
                if not current_status:
                    self.queue_email_notification()
                else:
                    self.send_queued_emails()
                last_status = current_status
            
            time.sleep(self.interval)

    def check_connection(self) -> bool:
        try:
            subprocess.run(["ping", "-c", "1", self.host], check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def log_status_change(self, status: bool):
        status_str = "Connected" if status else "Disconnected"
        logging.warning(f"Status change detected: {status_str}")
        send_notification("Internet Connection Status", status_str)

    def queue_email_notification(self):
        subject = "Internet Connection Lost"
        body = f"The internet connection was lost at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
        self.email_queue.append((subject, body))
        logging.info("Email notification queued.")

    def send_queued_emails(self):
        while self.email_queue:
            subject, body = self.email_queue.popleft()
            for email in self.to_emails:
                if send_email(subject, body, email):
                    logging.info(f"Queued email sent to {email}")
                else:
                    logging.error(f"Failed to send queued email to {email}")

    def stop(self):
        self.running = False
        logging.info("Monitoring stopped.")

def get_user_input(prompt, default):
    user_input = input(f"{prompt} (default: {default}): ").strip()
    return user_input if user_input else default

def test_email(recipient_emails):
    subject = "Internet Monitor Test Email"
    body = f"This is a test email from your Internet Monitor script. If you're receiving this, your email configuration is working correctly. Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    all_succeeded = True
    for email in recipient_emails:
        if not send_email(subject, body, email):
            all_succeeded = False
    
    return all_succeeded

def main():
    parser = argparse.ArgumentParser(description="Internet Connection Monitor")
    parser.add_argument("--test_email", action="store_true", help="Send a test email to all recipients in .env")
    args = parser.parse_args()

    logging.info("Application starting...")

    # Get raw RECIPIENT_EMAILS value
    raw_recipient_emails = get_env_value('RECIPIENT_EMAILS')
    logging.debug(f"Raw RECIPIENT_EMAILS value: {raw_recipient_emails}")

    # Get recipient emails from .env
    recipient_emails = raw_recipient_emails.split(',') if raw_recipient_emails else []
    recipient_emails = [email.strip() for email in recipient_emails if email.strip()]

    logging.info(f"Email notifications will be sent to: {', '.join(recipient_emails)}")

    if not recipient_emails:
        logging.error("No recipient emails specified in .env file. Please add RECIPIENT_EMAILS to your .env file.")
        sys.exit(1)

    if args.test_email:
        logging.info("Sending test email to all recipients...")
        if test_email(recipient_emails):
            logging.info("Test email sent successfully to all recipients.")
        else:
            logging.error("There was an issue sending the test email to one or more recipients. Please check your email configuration.")
        sys.exit(0)

    # Prompt for server and interval
    host = get_user_input("Enter the server to contact", "8.8.8.8")
    interval = int(get_user_input("Enter the number of seconds to wait between checks", "30"))

    try:
        monitor = ConnectionMonitor(interval=interval, host=host, to_emails=recipient_emails)
        monitor.run()
    except KeyboardInterrupt:
        logging.info("\nMonitoring stopped by user.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        logging.debug(traceback.format_exc())

if __name__ == "__main__":
    main()