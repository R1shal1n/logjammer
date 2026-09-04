# AWS GuardDuty Findings Format Reference

Complete specification for AWS GuardDuty findings based on AWS GuardDuty documentation.

## Overview

GuardDuty is a threat detection service that continuously monitors for malicious activity and unauthorized behavior. Findings are generated when GuardDuty detects potential security issues.

## Format

- **Format**: JSON (one finding per JSON object)
- **Delivery**: EventBridge, S3, CloudWatch Events, or exported JSONL
- **Schema Version**: Currently 2.0
- **Finding Lifecycle**: Active findings updated as new occurrences detected

## Complete Finding Structure

### Top-Level Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| **schemaVersion** | String | Schema version (e.g., "2.0") | Yes |
| **accountId** | String | AWS account ID | Yes |
| **region** | String | AWS region where finding was generated | Yes |
| **partition** | String | AWS partition (aws, aws-cn, aws-us-gov) | Yes |
| **id** | String | Unique identifier for the finding | Yes |
| **arn** | String | ARN of the finding | Yes |
| **type** | String | Finding type (see Finding Types below) | Yes |
| **resource** | Object | Affected resource details | Yes |
| **service** | Object | Service and action information | Yes |
| **severity** | Number | Severity score (0.1 to 8.9) | Yes |
| **createdAt** | String | ISO 8601 timestamp when finding was created | Yes |
| **updatedAt** | String | ISO 8601 timestamp when finding was last updated | Yes |
| **title** | String | Short description of the finding | Yes |
| **description** | String | Detailed description of the finding | Yes |

### Severity Levels

| Severity Score | Level | Description |
|----------------|-------|-------------|
| 0.1 - 3.9 | Low | Suspicious activity that may indicate reconnaissance |
| 4.0 - 6.9 | Medium | Suspicious activity with moderate risk |
| 7.0 - 8.9 | High | Compromised resource or credentialed access from unusual location |

### Resource Object

The `resource` object structure varies by resource type:

#### AccessKey Resource
```json
{
  "resourceType": "AccessKey",
  "accessKeyDetails": {
    "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
    "principalId": "AIDACKCEVSQ6C2EXAMPLE",
    "userName": "user-name",
    "userType": "IAMUser"
  }
}
```

**userType values:**
- `IAMUser`
- `AssumedRole`
- `FederatedUser`
- `Root`
- `AWSService`
- `AWSAccount`

#### Instance Resource
```json
{
  "resourceType": "Instance",
  "instanceDetails": {
    "instanceId": "i-99999999",
    "instanceType": "t3.medium",
    "instanceState": "running",
    "launchTime": "2024-01-01T00:00:00.000Z",
    "platform": "Linux/UNIX",
    "productCodes": [],
    "iamInstanceProfile": {
      "arn": "arn:aws:iam::123456789012:instance-profile/role-name",
      "id": "AIPAI6EXAMPLE"
    },
    "networkInterfaces": [
      {
        "ipv6Addresses": [],
        "networkInterfaceId": "eni-12345678",
        "privateDnsName": "ip-10-0-0-1.ec2.internal",
        "privateIpAddress": "10.0.0.1",
        "privateIpAddresses": [
          {
            "privateDnsName": "ip-10-0-0-1.ec2.internal",
            "privateIpAddress": "10.0.0.1"
          }
        ],
        "publicDnsName": "ec2-1-2-3-4.compute-1.amazonaws.com",
        "publicIp": "1.2.3.4",
        "securityGroups": [
          {
            "groupId": "sg-12345678",
            "groupName": "default"
          }
        ],
        "subnetId": "subnet-12345678",
        "vpcId": "vpc-12345678"
      }
    ],
    "tags": [
      {
        "key": "Name",
        "value": "web-server"
      }
    ]
  }
}
```

#### S3Bucket Resource
```json
{
  "resourceType": "S3Bucket",
  "s3BucketDetails": [
    {
      "arn": "arn:aws:s3:::bucket-name",
      "name": "bucket-name",
      "type": "Destination",
      "createdAt": "2024-01-01T00:00:00.000Z",
      "owner": {
        "id": "AIDAI23HXH7EXAMPLE"
      },
      "tags": [
        {
          "key": "Environment",
          "value": "Production"
        }
      ],
      "defaultServerSideEncryption": {
        "encryptionType": "AES256"
      },
      "publicAccess": {
        "permissionConfiguration": {
          "bucketLevelPermissions": {
            "accessControlList": {
              "allowsPublicReadAccess": false,
              "allowsPublicWriteAccess": false
            },
            "bucketPolicy": {
              "allowsPublicReadAccess": false,
              "allowsPublicWriteAccess": false
            },
            "blockPublicAccess": {
              "ignorePublicAcls": true,
              "restrictPublicBuckets": true,
              "blockPublicAcls": true,
              "blockPublicPolicy": true
            }
          }
        }
      }
    }
  ]
}
```

### Service Object

```json
{
  "service": {
    "serviceName": "guardduty",
    "detectorId": "12abc34d567e8fa901bc2d34e56789f0",
    "action": {
      "actionType": "AWS_API_CALL",
      "awsApiCallAction": {
        "api": "ListBuckets",
        "serviceName": "s3.amazonaws.com",
        "callerType": "Remote IP",
        "remoteIpDetails": {
          "ipAddressV4": "198.51.100.0",
          "organization": {
            "asn": "16509",
            "asnOrg": "AMAZON-02",
            "isp": "Amazon.com",
            "org": "Amazon.com"
          },
          "country": {
            "countryCode": "US",
            "countryName": "United States"
          },
          "city": {
            "cityName": "Seattle"
          },
          "geoLocation": {
            "lat": 47.6062,
            "lon": -122.3321
          }
        },
        "domainDetails": {
          "domain": "example.com"
        },
        "affectedResources": {
          "AWS::S3::Bucket": "arn:aws:s3:::bucket-name"
        }
      }
    },
    "resourceRole": "TARGET",
    "additionalInfo": {
      "recentApiCalls": [
        {
          "api": "GetObject",
          "count": 5
        }
      ],
      "sample": true,
      "unusual": true
    },
    "eventFirstSeen": "2024-01-01T00:00:00.000Z",
    "eventLastSeen": "2024-01-01T01:00:00.000Z",
    "archived": false,
    "count": 5
  }
}
```

#### Action Types

| actionType | Description | Details Object |
|------------|-------------|----------------|
| **AWS_API_CALL** | AWS API call activity | `awsApiCallAction` |
| **NETWORK_CONNECTION** | Network connection | `networkConnectionAction` |
| **PORT_PROBE** | Port scanning activity | `portProbeAction` |
| **DNS_REQUEST** | DNS query | `dnsRequestAction` |
| **KUBERNETES_API_CALL** | EKS API call | `kubernetesApiCallAction` |

#### Network Connection Action
```json
{
  "actionType": "NETWORK_CONNECTION",
  "networkConnectionAction": {
    "blocked": false,
    "connectionDirection": "OUTBOUND",
    "localPortDetails": {
      "port": 54321,
      "portName": "Unknown"
    },
    "protocol": "TCP",
    "localIpDetails": {
      "ipAddressV4": "10.0.0.1"
    },
    "remoteIpDetails": {
      "ipAddressV4": "198.51.100.0",
      "organization": {
        "asn": "0",
        "asnOrg": "Unknown",
        "isp": "Unknown",
        "org": "Unknown"
      },
      "country": {
        "countryName": "Unknown"
      },
      "city": {
        "cityName": "Unknown"
      },
      "geoLocation": {
        "lat": 0.0,
        "lon": 0.0
      }
    },
    "remotePortDetails": {
      "port": 4444,
      "portName": "Unknown"
    }
  }
}
```

#### Port Probe Action
```json
{
  "actionType": "PORT_PROBE",
  "portProbeAction": {
    "blocked": false,
    "portProbeDetails": [
      {
        "localPortDetails": {
          "port": 22,
          "portName": "SSH"
        },
        "localIpDetails": {
          "ipAddressV4": "10.0.0.1"
        },
        "remoteIpDetails": {
          "ipAddressV4": "198.51.100.0",
          "organization": {
            "asn": "0",
            "asnOrg": "Unknown",
            "isp": "Unknown",
            "org": "Unknown"
          },
          "country": {
            "countryName": "Unknown"
          }
        }
      }
    ]
  }
}
```

## Common Finding Types

### Reconnaissance

| Finding Type | Severity | Description |
|--------------|----------|-------------|
| **Recon:IAMUser/ResourcePermissions** | 5.0 | IAM principal probing resource permissions |
| **Recon:IAMUser/MaliciousIPCaller** | 5.0 | API calls from known malicious IP |
| **Recon:EC2/PortProbeUnprotectedPort** | 5.0 | EC2 instance port being probed |
| **Recon:EC2/Portscan** | 5.0 | EC2 instance performing port scan |

### Initial Access

| Finding Type | Severity | Description |
|--------------|----------|-------------|
| **UnauthorizedAccess:IAMUser/ConsoleLoginSuccess.B** | 5.0 | Successful login from unusual location |
| **UnauthorizedAccess:IAMUser/MaliciousIPCaller.Custom** | 5.0 | API call from malicious IP |
| **UnauthorizedAccess:IAMUser/TorIPCaller** | 5.0 | API call from Tor exit node |
| **UnauthorizedAccess:EC2/SSHBruteForce** | 5.0 | SSH brute force attack |

### Privilege Escalation

| Finding Type | Severity | Description |
|--------------|----------|-------------|
| **PrivilegeEscalation:IAMUser/AdministrativePermissions** | 8.0 | User granted admin permissions |
| **PrivilegeEscalation:IAMUser/AnomalousBehavior** | 5.0 | Unusual privilege escalation activity |

### Defense Evasion

| Finding Type | Severity | Description |
|--------------|----------|-------------|
| **Stealth:IAMUser/CloudTrailLoggingDisabled** | 8.0 | CloudTrail logging disabled |
| **Stealth:IAMUser/PasswordPolicyChange** | 5.0 | Password policy weakened |
| **Stealth:S3/ServerAccessLoggingDisabled** | 5.0 | S3 access logging disabled |

### Credential Access

| Finding Type | Severity | Description |
|--------------|----------|-------------|
| **CredentialAccess:IAMUser/AnomalousBehavior** | 5.0 | Unusual credential access |

### Discovery

| Finding Type | Severity | Description |
|--------------|----------|-------------|
| **Discovery:S3/BucketEnumeration.Unusual** | 5.0 | Unusual S3 bucket enumeration |
| **Discovery:S3/TorIPCaller** | 5.0 | S3 API from Tor exit node |

### Exfiltration

| Finding Type | Severity | Description |
|--------------|----------|-------------|
| **Exfiltration:S3/ObjectRead.Unusual** | 8.0 | Unusual S3 object read activity |
| **Exfiltration:S3/MaliciousIPCaller** | 8.0 | S3 access from malicious IP |

### Impact

| Finding Type | Severity | Description |
|--------------|----------|-------------|
| **Impact:S3/MaliciousIPCaller** | 8.0 | S3 API from malicious IP (destructive) |
| **Impact:EC2/MaliciousIPCaller** | 8.0 | EC2 API from malicious IP (destructive) |
| **Impact:IAMUser/AnomalousBehavior** | 5.0 | Unusual destructive behavior |

### Command and Control

| Finding Type | Severity | Description |
|--------------|----------|-------------|
| **Backdoor:EC2/C&CActivity.B** | 8.0 | EC2 communicating with C2 server |
| **Backdoor:EC2/DenialOfService.Dns** | 8.0 | EC2 performing DNS DDoS |
| **Backdoor:EC2/Spambot** | 5.0 | EC2 sending spam |

### Cryptocurrency Mining

| Finding Type | Severity | Description |
|--------------|----------|-------------|
| **CryptoCurrency:EC2/BitcoinTool.B** | 8.0 | EC2 communicating with Bitcoin mining pool |
| **CryptoCurrency:Runtime/BitcoinTool.B** | 8.0 | Container communicating with mining pool |

### Trojan

| Finding Type | Severity | Description |
|--------------|----------|-------------|
| **Trojan:EC2/BlackholeTraffic** | 8.0 | EC2 attempting to reach blackhole IP |
| **Trojan:EC2/DropPoint** | 8.0 | EC2 making requests to known drop point |
| **Trojan:EC2/DGADomainRequest.B** | 8.0 | EC2 querying DGA domain |

## Example Findings

### Example 1: Console Login from Unusual Location
```json
{
  "schemaVersion": "2.0",
  "accountId": "123456789012",
  "region": "us-east-1",
  "partition": "aws",
  "id": "eeb88ab56556eb7771b266670dddee5a",
  "arn": "arn:aws:guardduty:us-east-1:123456789012:detector/12abc34d56789e0/finding/eeb88ab56556eb7771b266670dddee5a",
  "type": "UnauthorizedAccess:IAMUser/ConsoleLoginSuccess.B",
  "resource": {
    "resourceType": "AccessKey",
    "accessKeyDetails": {
      "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
      "principalId": "AIDACKCEVSQ6C2EXAMPLE",
      "userName": "admin-user",
      "userType": "IAMUser"
    }
  },
  "service": {
    "serviceName": "guardduty",
    "detectorId": "12abc34d56789e0",
    "action": {
      "actionType": "AWS_API_CALL",
      "awsApiCallAction": {
        "api": "ConsoleLogin",
        "serviceName": "signin.amazonaws.com",
        "callerType": "Remote IP",
        "remoteIpDetails": {
          "ipAddressV4": "198.51.100.0",
          "organization": {
            "asn": "0",
            "asnOrg": "Unknown",
            "isp": "Unknown",
            "org": "Unknown"
          },
          "country": {
            "countryName": "Russia"
          },
          "city": {
            "cityName": "Moscow"
          },
          "geoLocation": {
            "lat": 55.7558,
            "lon": 37.6173
          }
        }
      }
    },
    "resourceRole": "TARGET",
    "additionalInfo": {},
    "eventFirstSeen": "2024-01-01T10:00:00Z",
    "eventLastSeen": "2024-01-01T10:00:00Z",
    "archived": false,
    "count": 1
  },
  "severity": 5.0,
  "createdAt": "2024-01-01T10:01:00Z",
  "updatedAt": "2024-01-01T10:01:00Z",
  "title": "Console login from an unusual location",
  "description": "An AWS console login was successful from principal admin-user from an unusual location."
}
```

### Example 2: EC2 Communicating with C2 Server
```json
{
  "schemaVersion": "2.0",
  "accountId": "123456789012",
  "region": "us-east-1",
  "partition": "aws",
  "id": "92b8899377b9a6ed989bexample12345",
  "arn": "arn:aws:guardduty:us-east-1:123456789012:detector/12abc34d56789e0/finding/92b8899377b9a6ed989bexample12345",
  "type": "Backdoor:EC2/C&CActivity.B",
  "resource": {
    "resourceType": "Instance",
    "instanceDetails": {
      "instanceId": "i-99999999",
      "instanceType": "t3.medium",
      "launchTime": "2024-01-01T00:00:00.000Z",
      "networkInterfaces": [
        {
          "privateIpAddress": "10.0.0.1",
          "publicIp": "1.2.3.4",
          "subnetId": "subnet-12345678",
          "vpcId": "vpc-12345678"
        }
      ]
    }
  },
  "service": {
    "serviceName": "guardduty",
    "detectorId": "12abc34d56789e0",
    "action": {
      "actionType": "NETWORK_CONNECTION",
      "networkConnectionAction": {
        "blocked": false,
        "connectionDirection": "OUTBOUND",
        "localPortDetails": {
          "port": 54321,
          "portName": "Unknown"
        },
        "protocol": "TCP",
        "remoteIpDetails": {
          "ipAddressV4": "198.51.100.0",
          "organization": {
            "asn": "0",
            "asnOrg": "Unknown",
            "isp": "Unknown",
            "org": "Unknown"
          },
          "country": {
            "countryName": "Unknown"
          },
          "city": {
            "cityName": "Unknown"
          },
          "geoLocation": {
            "lat": 0.0,
            "lon": 0.0
          }
        },
        "remotePortDetails": {
          "port": 4444,
          "portName": "Unknown"
        }
      }
    },
    "resourceRole": "ACTOR",
    "additionalInfo": {},
    "eventFirstSeen": "2024-01-01T12:00:00Z",
    "eventLastSeen": "2024-01-01T12:30:00Z",
    "archived": false,
    "count": 15
  },
  "severity": 8.0,
  "createdAt": "2024-01-01T12:01:00Z",
  "updatedAt": "2024-01-01T12:31:00Z",
  "title": "EC2 instance is communicating with a known Command & Control server",
  "description": "EC2 instance i-99999999 is communicating with IP 198.51.100.0 which is associated with known command and control activity."
}
```

### Example 3: Cryptocurrency Mining
```json
{
  "schemaVersion": "2.0",
  "accountId": "123456789012",
  "region": "us-west-2",
  "partition": "aws",
  "id": "crypto123example456",
  "arn": "arn:aws:guardduty:us-west-2:123456789012:detector/12abc34d56789e0/finding/crypto123example456",
  "type": "CryptoCurrency:EC2/BitcoinTool.B",
  "resource": {
    "resourceType": "Instance",
    "instanceDetails": {
      "instanceId": "i-88888888",
      "instanceType": "t3.medium",
      "networkInterfaces": [
        {
          "privateIpAddress": "10.0.1.5",
          "publicIp": "2.3.4.5"
        }
      ]
    }
  },
  "service": {
    "serviceName": "guardduty",
    "action": {
      "actionType": "NETWORK_CONNECTION",
      "networkConnectionAction": {
        "connectionDirection": "OUTBOUND",
        "protocol": "TCP",
        "remotePortDetails": {
          "port": 3333,
          "portName": "Bitcoin"
        }
      }
    },
    "eventFirstSeen": "2024-01-01T14:00:00Z",
    "eventLastSeen": "2024-01-01T16:00:00Z",
    "count": 120
  },
  "severity": 8.0,
  "createdAt": "2024-01-01T14:01:00Z",
  "updatedAt": "2024-01-01T16:01:00Z",
  "title": "EC2 instance is communicating with a known cryptocurrency mining pool",
  "description": "EC2 instance i-88888888 is communicating with a cryptocurrency mining pool."
}
```

## Important Notes

1. **Finding Lifecycle**: Findings remain active until archived or the issue is resolved
2. **Count Field**: Increments each time the same activity is detected
3. **Updated Timestamps**: `updatedAt` changes when finding count increases
4. **Sample Flag**: `additionalInfo.sample` indicates if this is a sample finding
5. **Archived**: Archived findings don't appear in active findings list
6. **Resource Role**:
   - `TARGET` - Resource is the target of the activity
   - `ACTOR` - Resource is performing the activity

## Integration

- **EventBridge**: Real-time finding delivery
- **S3 Export**: Batch export to S3 bucket
- **CloudWatch Events**: Legacy integration
- **Security Hub**: Automatic integration for centralized findings
- **Detective**: Cross-service investigation

## Best Practices

1. **Monitor High Severity**: Focus on 7.0+ findings first
2. **Automate Response**: Use EventBridge + Lambda for auto-remediation
3. **Suppress False Positives**: Use suppression rules for known good behavior
4. **Export to SIEM**: Regular S3 exports for long-term retention
5. **Correlate Findings**: Look for patterns across multiple finding types
