# S3 Server Access Logs Format Reference

Complete specification for AWS S3 Server Access Logs based on AWS S3 User Guide.

## Overview

S3 Server Access Logs provide detailed records for requests made to an S3 bucket. Each log record represents one request and consists of **newline-delimited**, **space-delimited** fields.

## Log Structure

- **Format**: Space-delimited text
- **Record**: One request per line
- **Missing data**: Fields can be `-` when data is unknown, unavailable, or not applicable
- **Quotes**: Some fields are enclosed in double quotes (Request-URI, Referer, User-Agent)

## Complete Field List (26 Fields in Order)

| # | Field Name | Description | Example |
|---|------------|-------------|---------|
| 1 | **Bucket Owner** | Canonical user ID of bucket owner | `79a59df900b949e55d96a1e698fbacedfd6e09d98eacf8f8d5218e7cd47ef2be` |
| 2 | **Bucket** | Bucket name that processed the request | `amzn-s3-demo-bucket1` |
| 3 | **Time** | Request time (UTC): `[%d/%b/%Y:%H:%M:%S %z]` | `[06/Feb/2019:00:00:38 +0000]` |
| 4 | **Remote IP** | Apparent IP address of requester | `192.0.2.3` |
| 5 | **Requester** | Canonical user ID, IAM user, or `-` for unauthenticated | `79a59df...` or `arn:aws:sts::123456789012:assumed-role/roleName/test` |
| 6 | **Request ID** | Unique request identifier | `3E57427F3EXAMPLE` |
| 7 | **Operation** | Operation type (see Operation Types below) | `REST.GET.OBJECT` |
| 8 | **Key** | Object key (URL encoded), or `-` | `/photos/2019/08/puppy.jpg` |
| 9 | **Request-URI** | Request-URI from HTTP request **(quoted)** | `"GET /bucket?versioning HTTP/1.1"` |
| 10 | **HTTP Status** | Numeric HTTP status code | `200`, `404`, `403` |
| 11 | **Error Code** | S3 error code, or `-` if no error | `NoSuchBucket`, `AccessDenied`, `-` |
| 12 | **Bytes Sent** | Response bytes sent (excluding HTTP overhead), or `-` | `2662992`, `-` |
| 13 | **Object Size** | Total object size in bytes | `3462992`, `-` |
| 14 | **Total Time** | Milliseconds - request receipt to last response byte | `70` |
| 15 | **Turn-Around Time** | Milliseconds - last request byte to first response byte | `10` |
| 16 | **Referer** | HTTP Referer header **(quoted)** | `"http://www.example.com/webservices"`, `"-"` |
| 17 | **User-Agent** | HTTP User-Agent header **(quoted)** | `"S3Console/0.4"`, `"curl/7.15.1"` |
| 18 | **Version Id** | Version ID in request, or `-` | `3HL4kqtJvjVBH40Nrjfkd`, `-` |
| 19 | **Host Id** | x-amz-id-2 / S3 extended request ID | `s9lzHYrFp76ZVxRcpX9+5cjAnEH2ROuNkd2BHfIa6UkFVdtjf5m...` |
| 20 | **Signature Version** | Signature version: `SigV2`, `SigV4`, or `-` | `SigV4` |
| 21 | **Cipher Suite** | TLS cipher for HTTPS, or `-` for HTTP | `ECDHE-RSA-AES128-GCM-SHA256`, `-` |
| 22 | **Authentication Type** | `AuthHeader`, `QueryString`, or `-` | `AuthHeader` |
| 23 | **Host Header** | Endpoint used to connect | `bucket.s3.us-west-1.amazonaws.com` |
| 24 | **TLS Version** | TLS version: `TLSv1.1`, `TLSv1.2`, `TLSv1.3`, or `-` | `TLSv1.2` |
| 25 | **Access Point ARN** | Access point ARN, or `-` | `arn:aws:s3:us-west-1:123456789012:accesspoint/example-AP` |
| 26 | **aclRequired** | Whether ACL required for authorization: `Yes` or `-` | `Yes`, `-` |

## Common Operation Types

### Object Operations
- `REST.GET.OBJECT` - Get object
- `REST.PUT.OBJECT` - Put/upload object
- `REST.DELETE.OBJECT` - Delete object
- `REST.HEAD.OBJECT` - Head object (metadata only)
- `REST.POST.OBJECT` - POST upload
- `REST.COPY.OBJECT_GET` - Copy operation (source)
- `REST.COPY.OBJECT_PUT` - Copy operation (destination)

### Bucket Operations
- `REST.GET.BUCKET` - List objects in bucket
- `REST.GET.VERSIONING` - Get bucket versioning status
- `REST.GET.LOGGING_STATUS` - Get bucket logging configuration
- `REST.GET.BUCKETPOLICY` - Get bucket policy
- `REST.PUT.BUCKETPOLICY` - Put bucket policy
- `REST.DELETE.BUCKETPOLICY` - Delete bucket policy
- `REST.GET.ACL` - Get ACL
- `REST.PUT.ACL` - Put ACL

### Special Operations
- `S3.COMPUTE.OBJECT.CHECKSUM` - Compute checksum
- `BATCH.DELETE.OBJECT` - Batch delete
- `WEBSITE.GET.OBJECT` - Website endpoint access

## Example Log Records

### Example 1: GET VERSIONING
```
79a59df900b949e55d96a1e698fbacedfd6e09d98eacf8f8d5218e7cd47ef2be amzn-s3-demo-bucket1 [06/Feb/2019:00:00:38 +0000] 192.0.2.3 79a59df900b949e55d96a1e698fbacedfd6e09d98eacf8f8d5218e7cd47ef2be 3E57427F3EXAMPLE REST.GET.VERSIONING - "GET /amzn-s3-demo-bucket1?versioning HTTP/1.1" 200 - 113 - 7 - "-" "S3Console/0.4" - s9lzHYrFp76ZVxRcpX9+5cjAnEH2ROuNkd2BHfIa6UkFVdtjf5mKR3/eTPFvsiP/XV/VLi31234= SigV4 ECDHE-RSA-AES128-GCM-SHA256 AuthHeader amzn-s3-demo-bucket1.s3.us-west-1.amazonaws.com TLSV1.2 arn:aws:s3:us-west-1:123456789012:accesspoint/example-AP Yes
```

### Example 2: GET BUCKET POLICY (Error)
```
79a59df900b949e55d96a1e698fbacedfd6e09d98eacf8f8d5218e7cd47ef2be amzn-s3-demo-bucket1 [06/Feb/2019:00:00:38 +0000] 192.0.2.3 79a59df900b949e55d96a1e698fbacedfd6e09d98eacf8f8d5218e7cd47ef2be A1206F460EXAMPLE REST.GET.BUCKETPOLICY - "GET /amzn-s3-demo-bucket1?policy HTTP/1.1" 404 NoSuchBucketPolicy 297 - 38 - "-" "S3Console/0.4" - BNaBsXZQQDbssi6xMBdBU2sLt+Yf5kZDmeBUP35sFoKa3sLLeMC78iwEIWxs99CRUrbS4n11234= SigV4 ECDHE-RSA-AES128-GCM-SHA256 AuthHeader amzn-s3-demo-bucket1.s3.us-west-1.amazonaws.com TLSV1.2 - Yes
```

### Example 3: PUT OBJECT
```
79a59df900b949e55d96a1e698fbacedfd6e09d98eacf8f8d5218e7cd47ef2be amzn-s3-demo-bucket1 [06/Feb/2019:00:01:57 +0000] 192.0.2.3 79a59df900b949e55d96a1e698fbacedfd6e09d98eacf8f8d5218e7cd47ef2be DD6CC733AEXAMPLE REST.PUT.OBJECT s3-dg.pdf "PUT /amzn-s3-demo-bucket1/s3-dg.pdf HTTP/1.1" 200 - - 4406583 41754 28 "-" "S3Console/0.4" - 10S62Zv81kBW7BB6SX4XJ48o6kpcl6LPwEoizZQQxJd5qDSCTLX0TgS37kYUBKQW3+bPdrg1234= SigV4 ECDHE-RSA-AES128-SHA AuthHeader amzn-s3-demo-bucket1.s3.us-west-1.amazonaws.com TLSV1.2 - Yes
```

### Example 4: COMPUTE CHECKSUM
```
7cd47ef2be amzn-s3-demo-bucket [06/Feb/2019:00:00:38 +0000] 192.0.2.3 79a59df900b949e55d96a1e698fbacedfd6e09d98eacf8f8d5218e7cd47ef2be e5042925-b524-4b3b-a869-f3881e78ff3a S3.COMPUTE.OBJECT.CHECKSUM example-object - - - - 1048576 - - - - -bPf7qjG4XwYdPgDQTl72GW/uotRhdPz2UryEyAFLDSRmKrakUkJCYLtAw6fdANcrsUYc1M/kIulXM1u5vZQT5g== - - - - - -
```

### Example 5: Unauthenticated Request (403)
```
79a59df900b949e55d96a1e698fbacedfd6e09d98eacf8f8d5218e7cd47ef2be my-bucket [01/Jan/2023:12:00:00 +0000] 203.0.113.42 - A1B2C3D4EXAMPLE REST.GET.OBJECT confidential/data.csv "GET /my-bucket/confidential/data.csv HTTP/1.1" 403 AccessDenied - - 15 8 "-" "curl/7.68.0" - xyz123HOSTID456== - - - my-bucket.s3.amazonaws.com - - -
```

## Common HTTP Status Codes

| Code | Meaning | Common Scenarios |
|------|---------|------------------|
| 200 | OK | Successful GET/PUT/DELETE |
| 204 | No Content | Successful DELETE |
| 403 | Forbidden | Access Denied, insufficient permissions |
| 404 | Not Found | NoSuchBucket, NoSuchKey |
| 500 | Internal Error | S3 internal error |
| 503 | Service Unavailable | SlowDown, temporary unavailability |

## Common Error Codes

- `AccessDenied` - Insufficient permissions
- `NoSuchBucket` - Bucket doesn't exist
- `NoSuchKey` - Object doesn't exist
- `NoSuchBucketPolicy` - No bucket policy set
- `InvalidArgument` - Invalid request parameter
- `SignatureDoesNotMatch` - Authentication failure

## Requester Field Formats

### IAM User
```
arn:aws:iam::123456789012:user/username
```

### Assumed Role
```
arn:aws:sts::123456789012:assumed-role/roleName/session-name
```

### Canonical User ID
```
79a59df900b949e55d96a1e698fbacedfd6e09d98eacf8f8d5218e7cd47ef2be
```

### Unauthenticated
```
-
```

## Special Behaviors

### Copy Operations
COPY operations generate **two log records**:
1. `REST.COPY.OBJECT_GET` - Source object access
2. `REST.COPY.OBJECT_PUT` - Destination object creation

### Custom Query Parameters
Parameters beginning with `x-` are included in Request-URI but ignored by S3:
```
GET /bucket/object?x-user=john&x-dept=engineering HTTP/1.1
```

### Quoted Fields
Three fields are **always quoted** with double quotes:
1. Request-URI
2. Referer
3. User-Agent

### Field Extensibility
AWS may add new fields **at the end** of log records in future. Parsers should handle trailing fields gracefully.

## Best Practices for Parsing

1. **Split by space** - But account for quoted fields
2. **Handle missing values** - Fields can be `-`
3. **Decode URLs** - Key field may be URL-encoded
4. **Quote handling** - Request-URI, Referer, User-Agent are quoted
5. **Future fields** - Don't assume exactly 26 fields (may expand)

## Log Delivery

- **Best-effort delivery** - Logs may be delayed or duplicated
- **Delivery time** - Usually within a few hours
- **Not real-time** - Not suitable for real-time monitoring
- **Completeness** - Rarely, log records may be lost

## Implementation Notes

1. Each log record is **newline-delimited** (one request per line)
2. Fields are **space-delimited**
3. Quoted fields contain internal spaces
4. Missing data represented as `-`
5. Time format is fixed: `[%d/%b/%Y:%H:%M:%S %z]`
6. All times in UTC
7. Bytes values can be `-` when not applicable
8. Request ID is unique per request
9. Host ID is the extended request ID (x-amz-id-2)
