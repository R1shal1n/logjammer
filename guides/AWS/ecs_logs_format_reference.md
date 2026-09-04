# AWS ECS/EKS Container Logs Format Reference

## Overview
Container lifecycle events, application logs, and security events from ECS/EKS clusters.

## Format
**Type**: JSON  
**File Extension**: `.jsonl`

## Example - Container Event
```json
{
  "timestamp": "2025-11-03T15:30:00Z",
  "level": "INFO",
  "source": "ecs-agent",
  "cluster": "production-cluster",
  "service": "web-service",
  "taskId": "abc12345",
  "event": "CONTAINER_STARTED",
  "message": "Container web-service-container started successfully"
}
```

## Event Types
- CONTAINER_STARTED/STOPPED
- HEALTH_CHECK_FAILED
- OOM_KILLED (Out of memory)
- PRIVILEGED_CONTAINER (Security concern)
- CONTAINER_ESCAPE_ATTEMPT
- REVERSE_SHELL_DETECTED

## Attack Indicators
- Privileged mode enabled
- Container escape attempts
- Crypto mining processes
- Reverse shell connections
- Unknown image registries

## MITRE ATT&CK
- T1611: Escape to Host
- T1610: Deploy Container
- T1496: Resource Hijacking
