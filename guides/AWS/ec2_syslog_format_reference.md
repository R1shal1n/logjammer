# AWS EC2 System Logs Format Reference

## Overview
Linux system logs from EC2 instances (/var/log/syslog, /var/log/auth.log, /var/log/secure).

## Format
**Type**: Text (syslog format)  
**File Extension**: `.log`

## Example
```
Nov  3 15:30:00 web-server-1 sshd[1234]: Accepted publickey for admin from 203.0.113.5 port 54321 ssh2
Nov  3 15:30:05 web-server-1 sudo: admin : TTY=pts/0 ; PWD=/home/admin ; USER=root ; COMMAND=/bin/bash
Nov  3 15:30:10 web-server-1 kernel: [UFW BLOCK] IN=eth0 SRC=198.51.100.5 DST=10.0.1.5 PROTO=TCP DPT=22
```

## Log Types
- **SSH**: Login success/failure
- **sudo**: Privileged command execution
- **kernel**: Firewall blocks, security events
- **systemd**: Service start/stop
- **cron**: Scheduled job execution

## Attack Indicators
- Multiple SSH failures: Brute force
- sudo permission denied: Privilege escalation
- Kernel module loading: Rootkit installation
- Hidden processes: Process hiding
- Unauthorized user creation

## MITRE ATT&CK
- T1110: Brute Force (SSH failures)
- T1548: Abuse Elevation Control Mechanism (sudo abuse)
- T1014: Rootkit
