# AWS RDS/Aurora Database Logs Format Reference

## Overview

RDS/Aurora logs capture database operations, connections, queries, and errors. Essential for detecting SQL injection, privilege escalation, and data exfiltration.

## Format

**Type**: Text (syslog-style for PostgreSQL, custom for MySQL)
**File Extension**: `.log` or `.txt`
**Use Case**: Database security monitoring, query analysis, performance tuning

## PostgreSQL Format Example

```
2025-11-03 15:30:00 UTC:203.0.113.5(203.0.113.5):postgres@production:[1234]:LOG: connection authorized: user=app_user database=production SSL enabled (protocol=TLSv1.3, cipher=ECDHE-RSA-AES256-GCM-SHA384, compression=off)
2025-11-03 15:30:01 UTC:::@:[1234]:LOG: duration: 125.456 ms  statement: SELECT * FROM users WHERE id = 123
2025-11-03 15:30:05 UTC:::@:[1234]:ERROR: syntax error at or near "--" in query: SELECT * FROM users WHERE username = 'admin'--' AND password = 'x'
```

## MySQL Slow Query Format

```
# Time: 2025-11-03T15:30:00Z
# User@Host: app_user[app_user] @ [10.0.1.5]
# Query_time: 5.123456  Lock_time: 0.000123  Rows_sent: 50000  Rows_examined: 1000000
SET timestamp=1699027800;
SELECT * FROM credit_cards;
```

## Log Types

| Type | Description | Attack Indicator |
|------|-------------|------------------|
| Connection | Login success/failure | Brute force attempts |
| Query | SQL statement execution | SQL injection, data exfiltration |
| Error | Database errors | Privilege escalation attempts |
| Slow Query | Long-running queries | Large data dumps |
| Audit | pgAudit events (JSON) | Unauthorized table access |

## Attack Patterns

### SQL Injection
```
ERROR: syntax error: SELECT * FROM users WHERE id = 1 OR 1=1--
ERROR: syntax error: SELECT * FROM products WHERE id = 1; DROP TABLE users;--
```

### Data Exfiltration
```
LOG: duration: 25000.123 ms  statement: SELECT * FROM credit_cards INTO OUTFILE '/tmp/cards.csv'
LOG: duration: 30000.456 ms  statement: SELECT * FROM customers LIMIT 100000
```

### Privilege Escalation
```
ERROR: permission denied: must be superuser to execute: GRANT ALL PRIVILEGES ON *.* TO 'app_user'@'%'
ERROR: permission denied: must be owner of table users to execute DROP TABLE
```

## MITRE ATT&CK Mapping

| Pattern | MITRE Technique |
|---------|-----------------|
| SQL Injection | T1190 - Exploit Public-Facing Application |
| Large Data Dump | T1530 - Data from Cloud Storage |
| GRANT/CREATE USER | T1098 - Account Manipulation |

## References

- [RDS PostgreSQL Logs](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.Concepts.PostgreSQL.html)
- [RDS MySQL Logs](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.MySQL.LogFileSize.html)
