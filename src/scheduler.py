#!/usr/bin/env python3
import schedule
import time
import yaml
import logging
from datetime import datetime
from password_checker import PasswordChecker
from notification_sender import NotificationSender

class PasswordReminderScheduler:
    def __init__(self, config_path: str = 'config.yml'):
        self.config_path = config_path
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Setup logging
        self.setup_logging()
        
        # Initialize components
        self.password_checker = PasswordChecker(config_path)
        self.notification_sender = NotificationSender(config_path)
    
    def setup_logging(self):
        """Configure logging"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', 'logs/password_reminders.log')
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def run_password_check(self):
        """Main function to check passwords and send notifications"""
        logging.info("Starting password expiration check...")
        
        try:
            # Connect to Active Directory
            if not self.password_checker.connect():
                logging.error("Failed to connect to Active Directory")
                return
            
            # Get users with expiring passwords
            users_to_notify = self.password_checker.get_users_with_expiring_passwords()
            
            if users_to_notify:
                logging.info(f"Found {len(users_to_notify)} users with expiring passwords")
                
                # Send notifications
                self.notification_sender.send_all_notifications(users_to_notify)
                
                # Log summary
                for user in users_to_notify:
                    logging.info(
                        f"Notified {user['username']} ({user['display_name']}) - "
                        f"{user['days_until_expiration']} days remaining"
                    )
            else:
                logging.info("No users found with expiring passwords")
            
            # Disconnect from AD
            self.password_checker.disconnect()
            
        except Exception as e:
            logging.error(f"Error during password check: {e}")
        
        logging.info("Password expiration check completed")
    
    def start_scheduler(self):
        """Start the scheduled task"""
        run_time = self.config['schedule']['run_time']
        
        # Schedule daily run
        schedule.every().day.at(run_time).do(self.run_password_check)
        
        logging.info(f"Password reminder bot started. Scheduled to run daily at {run_time}")
        
        # Run once immediately for testing
        logging.info("Running initial check...")
        self.run_password_check()
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main entry point"""
    scheduler = PasswordReminderScheduler()
    
    try:
        scheduler.start_scheduler()
    except KeyboardInterrupt:
        logging.info("Password reminder bot stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
