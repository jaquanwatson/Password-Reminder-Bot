# Password Reminder Bot

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Microsoft Teams](https://img.shields.io/badge/Microsoft%20Teams-Integration-purple)](https://docs.microsoft.com/en-us/microsoftteams/)
[![Azure Functions](https://img.shields.io/badge/Azure%20Functions-Serverless-orange)](https://azure.microsoft.com/en-us/services/functions/)

> Proactive password expiration notification system with Microsoft Teams integration for improved security compliance.

## Purpose

Automate password expiration notifications to improve security compliance and reduce helpdesk tickets. Integrates seamlessly with Microsoft Teams for instant, actionable notifications.

## Key Features

- **Proactive Notifications**: Alerts users before passwords expire
- **Microsoft Teams Integration**: Direct messages and channel notifications
- **Customizable Schedules**: Flexible notification timing (30, 14, 7, 1 days)
- **Multi-language Support**: Localized messages for global organizations
- **Compliance Reporting**: Track notification delivery and user responses
- **Self-service Links**: Direct links to password reset portals

## Quick Demo

![Password Bot Flow](https://via.placeholder.com/800x300/FF9800/ffffff?text=Password+Reminder+Bot+Flow)

**Sample Teams Message:**
Password Expiration Reminder

Hi John! Your password will expire in 7 days (January 15, 2025).

Reset your password now: [Self-Service Portal]
Need help? Contact IT: ext. 1234
Business hours: Mon-Fri 8AM-6PM EST

This is an automated message from IT Security.

code


## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- Azure subscription
- Microsoft Teams app registration
- Azure AD permissions:
  - `User.Read.All`
  - `Chat.Create`
  - `TeamsAppInstallation.ReadWriteForUser`

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/jaquanwatson/Password-Reminder-Bot.git
   cd Password-Reminder-Bot
Install dependencies

bash

pip install -r requirements.txt
Configure environment

bash

cp .env.example .env
# Edit .env with your configuration
Run locally

bash

python main.py
Azure Functions Deployment
Install Azure Functions Core Tools

bash

npm install -g azure-functions-core-tools@4
Deploy to Azure

bash

func azure functionapp publish your-function-app-name
Configuration
Environment Variables
bash

# Azure AD Configuration
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id

# Teams Bot Configuration
TEAMS_BOT_ID=your-bot-id
TEAMS_BOT_PASSWORD=your-bot-password

# Notification Settings
NOTIFICATION_DAYS=30,14,7,1
DEFAULT_LANGUAGE=en-US
HELPDESK_CONTACT=ext.1234
Notification Schedule
json

{
  "schedule": "0 0 9 * * *",
  "timezone": "Eastern Standard Time",
  "notifications": [
    {"days": 30, "message_type": "info"},
    {"days": 14, "message_type": "warning"},
    {"days": 7, "message_type": "urgent"},
    {"days": 1, "message_type": "critical"}
  ]
}
How It Works
mermaid

graph TD
    A[Azure Function Trigger] --> B[Query Azure AD]
    B --> C[Check Password Expiry]
    C --> D{Expiring Soon?}
    D -->|Yes| E[Generate Notification]
    D -->|No| F[Skip User]
    E --> G[Send Teams Message]
    G --> H[Log Notification]
    F --> I[Continue to Next User]
    H --> I
    I --> J{More Users?}
    J -->|Yes| C
    J -->|No| K[Generate Report]
Features in Detail
Smart Notifications
Escalating Urgency: Messages become more urgent as expiration approaches
Business Hours Only: Respects user time zones and working hours
Weekend Handling: Adjusts notifications for weekends and holidays
Duplicate Prevention: Tracks sent notifications to avoid spam
Teams Integration
Direct Messages: Personal notifications to individual users
Channel Notifications: Summary reports to IT teams
Interactive Cards: Rich formatting with action buttons
Status Updates: Real-time delivery confirmations
Compliance & Reporting
Delivery Tracking: Monitor notification success rates
User Response Tracking: Track password reset completions
Compliance Reports: Generate reports for security audits
Exception Handling: Manage service accounts and exemptions
Sample Reports
Daily Notification Summary
code

Password Reminder Bot - Daily Report
Date: January 8, 2025
=====================================

Notifications Sent: 47
- 30-day reminders: 12
- 14-day reminders: 15
- 7-day reminders: 18
- 1-day reminders: 2

Delivery Status:
- Successfully delivered: 45 (96%)
- Failed deliveries: 2 (4%)

User Actions:
- Passwords reset: 23 (49%)
- Pending action: 24 (51%)

Failed Deliveries:
- user1@company.com (Teams not installed)
- user2@company.com (Account disabled)
Security Considerations
Secure Storage: Credentials stored in Azure Key Vault
Least Privilege: Minimal required permissions
Audit Logging: All actions logged for security review
Data Privacy: No password data stored or transmitted
Encryption: All communications encrypted in transit
Multi-language Support
Currently supported languages:

English (en-US)
Spanish (es-ES)
French (fr-FR)
German (de-DE)
Add new languages by creating message templates in /locales/

Advanced Features
Custom Message Templates
python

# Custom message for executives
executive_template = {
    "title": "Executive Password Reminder",
    "message": "Your password expires in {days} days. For immediate assistance, contact your dedicated IT support.",
    "priority": "high"
}
Integration with Other Systems
ServiceNow: Create tickets for non-responsive users
Slack: Cross-platform notification support
Email: Fallback notifications via Exchange
SMS: Critical notifications via Twilio
## Contributing
We welcome contributions! Please see our Contributing Guidelines.

Development Setup
bash

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Code formatting
black .
flake8 .
## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Author & Support
Jaquan Watson - Cloud & Systems Engineer

Email: jqwatson96@gmail.com

LinkedIn: jaquanwatson

GitHub: @jaquanwatson

Acknowledgments

Microsoft Teams Platform team

Azure Functions community

Python-Teams SDK contributors

⭐ Star this repo if it helped you! ⭐

Built with ❤️ for better IT security