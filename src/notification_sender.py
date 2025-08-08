import smtplib
import requests
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from typing import List, Dict
import logging
import pymsteams

class NotificationSender:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def send_email_notification(self, user: Dict) -> bool:
        """Send email notification to user"""
        if not self.config['notifications']['email']['enabled']:
            return True
        
        try:
            email_config = self.config['notifications']['email']
            
            # Load email template
            with open('templates/email_template.html', 'r') as f:
                template_content = f.read()
            
            template = Template(template_content)
            
            # Render email content
            html_content = template.render(
                user_name=user['display_name'],
                days_remaining=user['days_until_expiration'],
                expiration_date=user['expiration_date'].strftime('%B %d, %Y'),
                message=self.config['reminders']['messages'].get(
                    user['days_until_expiration'],
                    "Your password is expiring soon. Please change it."
                )
            )
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Password Expiration Reminder - {user['days_until_expiration']} days remaining"
            msg['From'] = email_config['from_address']
            msg['To'] = user['email']
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login
                server.login(email_config['username'], email_config['password'])
                server.send_message(msg)
            
            logging.info(f"Email sent to {user['email']}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email to {user['email']}: {e}")
            return False
    
    def send_teams_notification(self, users: List[Dict]) -> bool:
        """Send Teams notification with summary"""
        if not self.config['notifications']['teams']['enabled']:
            return True
        
        try:
            webhook_url = self.config['notifications']['teams']['webhook_url']
            
            # Create Teams card
            teams_card = pymsteams.connectorcard(webhook_url)
            teams_card.title("Password Expiration Alerts")
            teams_card.color("FF6B35")
            
            # Group users by days until expiration
            grouped_users = {}
            for user in users:
                days = user['days_until_expiration']
                if days not in grouped_users:
                    grouped_users[days] = []
                grouped_users[days].append(user)
            
            # Create sections for each group
            summary_text = f"**{len(users)} users** have passwords expiring soon:\n\n"
            
            for days in sorted(grouped_users.keys()):
                user_list = grouped_users[days]
                summary_text += f"**{days} day{'s' if days != 1 else ''} remaining:** {len(user_list)} user{'s' if len(user_list) != 1 else ''}\n"
                
                for user in user_list[:5]:  # Show first 5 users
                    summary_text += f"• {user['display_name']} ({user['username']})\n"
                
                if len(user_list) > 5:
                    summary_text += f"• ... and {len(user_list) - 5} more\n"
                
                summary_text += "\n"
            
            teams_card.text(summary_text)
            
            # Add action button
            teams_card.addLinkButton("View AD Users", "https://portal.azure.com")
            
            teams_card.send()
            logging.info("Teams notification sent successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send Teams notification: {e}")
            return False
    
    def send_slack_notification(self, users: List[Dict]) -> bool:
        """Send Slack notification with summary"""
        if not self.config['notifications']['slack']['enabled']:
            return True
        
        try:
            webhook_url = self.config['notifications']['slack']['webhook_url']
            
            # Create Slack message
            message = {
                "text": "Password Expiration Alerts",
                "attachments": [
                    {
                        "color": "warning",
                        "title": f"{len(users)} Users with Expiring Passwords",
                        "fields": []
                    }
                ]
            }
            
            # Group users by expiration days
            grouped_users = {}
            for user in users:
                days = user['days_until_expiration']
                if days not in grouped_users:
                    grouped_users[days] = []
                grouped_users[days].append(user)
            
            # Add fields for each group
            for days in sorted(grouped_users.keys()):
                user_list = grouped_users[days]
                user_names = [user['display_name'] for user in user_list[:10]]
                
                field_value = "\n".join(user_names)
                if len(user_list) > 10:
                    field_value += f"\n... and {len(user_list) - 10} more"
                
                message["attachments"][0]["fields"].append({
                    "title": f"{days} day{'s' if days != 1 else ''} remaining",
                    "value": field_value,
                    "short": True
                })
            
            response = requests.post(webhook_url, json=message)
            response.raise_for_status()
            
            logging.info("Slack notification sent successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send Slack notification: {e}")
            return False
    
    def send_all_notifications(self, users: List[Dict]):
        """Send notifications via all enabled channels"""
        if not users:
            logging.info("No users to notify")
            return
        
        # Send individual email notifications
        email_success_count = 0
        for user in users:
            if self.send_email_notification(user):
                email_success_count += 1
        
        logging.info(f"Sent {email_success_count}/{len(users)} email notifications")
        
        # Send Teams summary
        self.send_teams_notification(users)
        
        # Send Slack summary
        self.send_slack_notification(users)
