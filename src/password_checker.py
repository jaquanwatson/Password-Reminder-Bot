import ldap
import yaml
from datetime import datetime, timedelta
from typing import List, Dict
import logging

class PasswordChecker:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.ad_config = self.config['active_directory']
        self.connection = None
    
    def connect(self) -> bool:
        """Connect to Active Directory"""
        try:
            self.connection = ldap.initialize(self.ad_config['server'])
            self.connection.protocol_version = ldap.VERSION3
            self.connection.set_option(ldap.OPT_REFERRALS, 0)
            
            bind_dn = self.ad_config['bind_user']
            bind_password = self.ad_config['bind_password']
            
            self.connection.simple_bind_s(bind_dn, bind_password)
            logging.info("Successfully connected to Active Directory")
            return True
            
        except ldap.LDAPError as e:
            logging.error(f"Failed to connect to AD: {e}")
            return False
    
    def get_users_with_expiring_passwords(self) -> List[Dict]:
        """Get users whose passwords are expiring soon"""
        if not self.connection:
            return []
        
        users_to_notify = []
        warning_days = self.config['reminders']['warning_days']
        
        try:
            # Search for all users
            search_filter = "(&(objectCategory=person)(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"
            attributes = [
                'sAMAccountName', 'displayName', 'mail', 'pwdLastSet',
                'maxPwdAge', 'userAccountControl'
            ]
            
            result = self.connection.search_s(
                self.ad_config['base_dn'],
                ldap.SCOPE_SUBTREE,
                search_filter,
                attributes
            )
            
            for dn, attrs in result:
                if not attrs:
                    continue
                
                username = attrs.get('sAMAccountName', [b''])[0].decode('utf-8')
                display_name = attrs.get('displayName', [b''])[0].decode('utf-8')
                email = attrs.get('mail', [b''])[0].decode('utf-8')
                
                if not email:
                    continue
                
                # Calculate password expiration
                pwd_last_set = attrs.get('pwdLastSet', [b'0'])[0]
                if pwd_last_set == b'0':
                    continue
                
                # Convert Windows FILETIME to datetime
                pwd_last_set_int = int(pwd_last_set.decode('utf-8'))
                if pwd_last_set_int == 0:
                    continue
                
                # Windows FILETIME epoch starts at 1601-01-01
                pwd_last_set_date = datetime(1601, 1, 1) + timedelta(microseconds=pwd_last_set_int/10)
                
                # Get domain password policy (default 42 days)
                max_pwd_age_days = 42  # You might want to query this from domain policy
                
                expiration_date = pwd_last_set_date + timedelta(days=max_pwd_age_days)
                days_until_expiration = (expiration_date - datetime.now()).days
                
                # Check if user needs notification
                if days_until_expiration in warning_days:
                    users_to_notify.append({
                        'username': username,
                        'display_name': display_name,
                        'email': email,
                        'days_until_expiration': days_until_expiration,
                        'expiration_date': expiration_date,
                        'last_set_date': pwd_last_set_date
                    })
                    
        except ldap.LDAPError as e:
            logging.error(f"Error searching for users: {e}")
        
        return users_to_notify
    
    def disconnect(self):
        """Disconnect from Active Directory"""
        if self.connection:
            self.connection.unbind_s()
            self.connection = None
