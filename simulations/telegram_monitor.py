#!/usr/bin/env python3
"""
Telegram connectivity monitor for @AzikielBot
Basic connectivity testing and state tracking for automated fallback system.
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
LOG_FILE = '/home/ubuntu/.openclaw/logs/telegram-monitor.log'
STATE_FILE = '/home/ubuntu/.openclaw/workspace/memory/telegram_state.json'

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('telegram_monitor')

class TelegramMonitor:
    """Monitor Telegram connectivity and rate limits"""
    
    STATES = {
        'NORMAL': 'primary provider (Anthropic) active',
        'DEGRADED': 'fallback provider (Open Router) active',
        'RECOVERY': 'testing primary provider after issue',
        'FAILED': 'both providers unavailable'
    }
    
    def __init__(self):
        self.state_file = Path(STATE_FILE)
        self.current_state = self.load_state()
        logger.info(f"Telegram monitor initialized. Current state: {self.current_state}")
        
    def load_state(self):
        """Load current state from file or return default"""
        default_state = {
            'state': 'NORMAL',
            'last_check': datetime.now().isoformat(),
            'rate_limit_detected': False,
            'rate_limit_since': None,
            'fallback_active': False,
            'checks': {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'rate_limit_count': 0
            },
            'provider': 'anthropic/claude-sonnet-4-6',
            'fallback_provider': 'openrouter/anthropic-claude-sonnet-4-6'
        }
        
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                # Update with any missing keys from default
                for key, value in default_state.items():
                    if key not in state:
                        state[key] = value
                return state
            except Exception as e:
                logger.error(f"Error loading state: {e}")
                return default_state
        return default_state
    
    def save_state(self):
        """Save current state to file"""
        try:
            self.current_state['last_check'] = datetime.now().isoformat()
            with open(self.state_file, 'w') as f:
                json.dump(self.current_state, f, indent=2)
            logger.debug(f"State saved: {self.current_state['state']}")
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def check_rate_limits(self):
        """Check system logs for Telegram rate limit errors"""
        log_files = [
            '/home/ubuntu/.openclaw/logs/openclaw.log',
            '/var/log/syslog'
        ]
        
        rate_limit_indicators = [
            'rate limit reached',
            'rate limit exceeded',
            '429 Too Many Requests',
            'FloodWaitError'
        ]
        
        rate_limit_detected = False
        detection_time = None
        
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    # Check last 100 lines for rate limits
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-100:]
                    
                    for line in lines:
                        if any(indicator in line.lower() for indicator in rate_limit_indicators):
                            rate_limit_detected = True
                            # Extract timestamp if possible
                            if not detection_time:
                                detection_time = datetime.now().isoformat()
                            logger.warning(f"Rate limit detected in {log_file}: {line.strip()}")
                except Exception as e:
                    logger.error(f"Error reading {log_file}: {e}")
        
        # Also check for the rate limit detection file
        rate_limit_file = '/tmp/rate-limit-detected.txt'
        if os.path.exists(rate_limit_file):
            rate_limit_detected = True
            if not detection_time:
                detection_time = datetime.fromtimestamp(
                    os.path.getmtime(rate_limit_file)
                ).isoformat()
            logger.warning(f"Rate limit detection file exists: {rate_limit_file}")
        
        return rate_limit_detected, detection_time
    
    def check_connectivity(self):
        """Basic connectivity check - placeholder for actual Telegram API test"""
        # This is a placeholder - actual implementation would use Telegram API
        # For now, we simulate connectivity checks
        
        # Check if gateway is responding
        gateway_check = self.check_gateway_health()
        
        # Check recent error logs
        error_check = self.check_recent_errors()
        
        # For @AzikielBot specifically, we would need API access
        # This is a placeholder for future implementation
        
        return gateway_check and error_check
    
    def check_gateway_health(self):
        """Check if OpenClaw gateway is responding"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 18789))
            sock.close()
            return result == 0
        except Exception as e:
            logger.error(f"Gateway health check failed: {e}")
            return False
    
    def check_recent_errors(self):
        """Check for recent error patterns in logs"""
        error_patterns = [
            'connection refused',
            'timeout',
            'network error',
            'failed to send'
        ]
        
        # Check last 50 lines of openclaw log
        log_file = '/home/ubuntu/.openclaw/logs/openclaw.log'
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()[-50:]
                
                error_count = 0
                for line in lines:
                    if any(pattern in line.lower() for pattern in error_patterns):
                        error_count += 1
                
                return error_count < 3  # Allow some errors
            except Exception as e:
                logger.error(f"Error reading log file: {e}")
        
        return True  # Assume OK if can't check
    
    def update_state_based_on_checks(self, rate_limit_detected, connectivity_ok):
        """Update state machine based on check results"""
        previous_state = self.current_state['state']
        
        # Update check counters
        self.current_state['checks']['total'] += 1
        if connectivity_ok:
            self.current_state['checks']['successful'] += 1
        else:
            self.current_state['checks']['failed'] += 1
        
        if rate_limit_detected:
            self.current_state['checks']['rate_limit_count'] += 1
            self.current_state['rate_limit_detected'] = True
            if not self.current_state['rate_limit_since']:
                self.current_state['rate_limit_since'] = datetime.now().isoformat()
            
            # Transition to DEGRADED state if rate limit detected
            if self.current_state['state'] == 'NORMAL':
                self.current_state['state'] = 'DEGRADED'
                self.current_state['fallback_active'] = True
                self.current_state['provider'] = self.current_state['fallback_provider']
                logger.warning(f"State transition: NORMAL → DEGRADED (rate limit detected)")
                self.notify_state_change(previous_state, 'DEGRADED', 'rate limit detected')
        
        elif not connectivity_ok:
            # Connectivity issues
            if self.current_state['state'] == 'NORMAL':
                self.current_state['state'] = 'DEGRADED'
                self.current_state['fallback_active'] = True
                self.current_state['provider'] = self.current_state['fallback_provider']
                logger.warning(f"State transition: NORMAL → DEGRADED (connectivity issues)")
                self.notify_state_change(previous_state, 'DEGRADED', 'connectivity issues')
        
        else:
            # Everything OK
            if self.current_state['state'] == 'DEGRADED':
                # Check if we should attempt recovery
                # After 1 hour in DEGRADED, try RECOVERY
                if self.current_state['rate_limit_since']:
                    limit_time = datetime.fromisoformat(self.current_state['rate_limit_since'])
                    if datetime.now() - limit_time > timedelta(hours=1):
                        self.current_state['state'] = 'RECOVERY'
                        logger.info(f"State transition: DEGRADED → RECOVERY (testing primary provider)")
                        self.notify_state_change(previous_state, 'RECOVERY', 'testing recovery')
            
            elif self.current_state['state'] == 'RECOVERY':
                # If still OK after recovery test, return to NORMAL
                self.current_state['state'] = 'NORMAL'
                self.current_state['fallback_active'] = False
                self.current_state['rate_limit_detected'] = False
                self.current_state['rate_limit_since'] = None
                self.current_state['provider'] = 'anthropic/claude-sonnet-4-6'
                logger.info(f"State transition: RECOVERY → NORMAL (recovery successful)")
                self.notify_state_change(previous_state, 'NORMAL', 'recovery successful')
        
        self.save_state()
    
    def notify_state_change(self, old_state, new_state, reason):
        """Log state change (could be extended to send notifications)"""
        message = f"Telegram monitor state change: {old_state} → {new_state} ({reason})"
        logger.info(message)
        
        # In future: send Telegram notification, email, etc.
        # For now, just log
        
        # Also update HEARTBEAT.md if needed
        self.update_heartbeat_reference(new_state, reason)
    
    def update_heartbeat_reference(self, state, reason):
        """Update HEARTBEAT.md with current Telegram state"""
        heartbeat_file = '/home/ubuntu/.openclaw/workspace/HEARTBEAT.md'
        if os.path.exists(heartbeat_file):
            try:
                with open(heartbeat_file, 'r') as f:
                    content = f.read()
                
                # Look for Telegram Rate Limit Monitoring section
                if '### Telegram Rate Limit Monitoring' in content:
                    # Update the status line
                    lines = content.split('\n')
                    updated = False
                    
                    for i, line in enumerate(lines):
                        if 'Current status:' in line and 'Telegram' in lines[i-1] or lines[i-1].startswith('### Telegram'):
                            lines[i] = f"Current status: {state} ({reason}) - {datetime.now().strftime('%d-%m-%Y %H:%M UTC')}"
                            updated = True
                            break
                    
                    if updated:
                        with open(heartbeat_file, 'w') as f:
                            f.write('\n'.join(lines))
                        logger.debug(f"Updated HEARTBEAT.md with state: {state}")
            except Exception as e:
                logger.error(f"Error updating HEARTBEAT.md: {e}")
    
    def run_check(self):
        """Run a complete monitoring check"""
        logger.info("Starting Telegram monitoring check")
        
        # Check for rate limits
        rate_limit_detected, detection_time = self.check_rate_limits()
        
        # Check connectivity
        connectivity_ok = self.check_connectivity()
        
        # Update state based on checks
        self.update_state_based_on_checks(rate_limit_detected, connectivity_ok)
        
        # Log summary
        logger.info(f"Check complete: rate_limit={rate_limit_detected}, connectivity={connectivity_ok}, state={self.current_state['state']}")
        
        return {
            'rate_limit_detected': rate_limit_detected,
            'connectivity_ok': connectivity_ok,
            'state': self.current_state['state'],
            'provider': self.current_state['provider']
        }

def main():
    """Main function for command-line usage"""
    monitor = TelegramMonitor()
    result = monitor.run_check()
    
    # Print summary for command-line
    print(f"Telegram Monitor Results:")
    print(f"  State: {result['state']}")
    print(f"  Provider: {result['provider']}")
    print(f"  Rate limit detected: {result['rate_limit_detected']}")
    print(f"  Connectivity OK: {result['connectivity_ok']}")
    print(f"  Details in log: {LOG_FILE}")
    print(f"  State file: {STATE_FILE}")
    
    # Return exit code based on state
    if result['state'] == 'FAILED':
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())