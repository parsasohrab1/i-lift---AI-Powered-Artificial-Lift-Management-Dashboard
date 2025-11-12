# Security و Compliance

راهنمای کامل Security و Compliance features

## Overview

سیستم Security و Compliance شامل:
- **Audit Logging**: ثبت تمام فعالیت‌های امنیتی
- **Encryption**: رمزنگاری داده‌های حساس
- **Security Policies**: مدیریت سیاست‌های امنیتی
- **Compliance Reporting**: گزارش‌های compliance
- **Access Control**: کنترل دسترسی پیشرفته

## Audit Logging

### Event Types

سیستم تمام eventهای زیر را ثبت می‌کند:

#### Authentication Events:
- `login`: ورود موفق
- `logout`: خروج
- `login_failed`: ورود ناموفق
- `password_change`: تغییر رمز عبور
- `token_refresh`: تمدید token

#### Data Access Events:
- `data_view`: مشاهده داده
- `data_create`: ایجاد داده
- `data_update`: به‌روزرسانی داده
- `data_delete`: حذف داده
- `data_export`: export داده

#### User Management Events:
- `user_create`: ایجاد کاربر
- `user_update`: به‌روزرسانی کاربر
- `user_delete`: حذف کاربر
- `role_change`: تغییر نقش

#### Security Events:
- `permission_denied`: دسترسی رد شده
- `unauthorized_access`: دسترسی غیرمجاز
- `suspicious_activity`: فعالیت مشکوک

### Audit Log Schema

```sql
CREATE TABLE audit_logs (
    audit_id UUID PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    user_id VARCHAR(50),
    username VARCHAR(100),
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    action VARCHAR(100),
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    success BOOLEAN DEFAULT TRUE,
    timestamp TIMESTAMPTZ NOT NULL
);
```

## Security Policies

### Password Policy

- **Min Length**: حداقل 8 کاراکتر
- **Require Uppercase**: نیاز به حروف بزرگ
- **Require Lowercase**: نیاز به حروف کوچک
- **Require Numbers**: نیاز به اعداد
- **Require Special Chars**: نیاز به کاراکترهای خاص
- **Max Age**: 90 روز
- **History Count**: 5 رمز عبور قبلی

### Session Policy

- **Timeout**: 30 دقیقه
- **Max Concurrent Sessions**: 5
- **Require HTTPS**: بله
- **Same Site**: Strict

### Data Retention Policy

- **Sensor Data**: 365 روز
- **Audit Logs**: 2555 روز (7 سال)
- **Alerts**: 180 روز
- **ML Predictions**: 365 روز

### Access Control Policy

- **Require MFA**: خیر (قابل تنظیم)
- **IP Whitelist**: لیست IPهای مجاز
- **IP Blacklist**: لیست IPهای غیرمجاز
- **Rate Limit**: 100 request per minute

## Encryption

### Encryption Service

- **Algorithm**: Fernet (symmetric encryption)
- **Key Management**: از environment variable یا generate
- **Sensitive Fields**: password, token, secret, api_key, credential

### Usage

```python
from app.services.encryption_service import EncryptionService

encryption = EncryptionService()

# Encrypt
encrypted = encryption.encrypt("sensitive_data")

# Decrypt
decrypted = encryption.decrypt(encrypted)

# Encrypt dictionary
encrypted_dict = encryption.encrypt_dict({
    "password": "secret123",
    "api_key": "key123"
})
```

## Compliance Reporting

### Report Types

1. **Full Report**: گزارش کامل با تمام sections
2. **Summary Report**: خلاصه گزارش
3. **Detailed Report**: گزارش تفصیلی

### Report Sections

1. **Audit Logs Summary**
   - Total events
   - Successful/Failed events
   - Event types distribution
   - Top users

2. **User Activity**
   - Active users
   - User actions
   - Last activity

3. **Security Events**
   - Failed logins
   - Permission denials
   - Unauthorized access
   - Suspicious activity

4. **Data Access**
   - Data operations
   - Data exports
   - Export users

5. **Alerts Summary**
   - Total alerts
   - Resolved/Unresolved
   - Severity distribution

6. **Compliance Status**
   - Password policy compliance
   - Session management compliance
   - Audit logging compliance
   - Encryption compliance

## API Endpoints

### Compliance

#### GET `/api/v1/compliance/report`
Generate compliance report (admin only)

**Query Parameters:**
- `start_date` (optional): Start date
- `end_date` (optional): End date
- `days` (default: 30): Number of days
- `report_type` (default: "full"): full, summary, detailed
- `format` (default: "json"): json, csv

#### GET `/api/v1/compliance/audit-logs`
Get audit logs (admin only)

**Query Parameters:**
- `user_id` (optional): Filter by user
- `event_type` (optional): Filter by event type
- `resource_type` (optional): Filter by resource
- `start_time` (optional): Start time
- `end_time` (optional): End time
- `limit` (default: 100)
- `offset` (default: 0)

#### GET `/api/v1/compliance/user-activity/{user_id}`
Get user activity summary (admin only)

**Query Parameters:**
- `days` (default: 30): Number of days

#### GET `/api/v1/compliance/suspicious-activity`
Detect suspicious activity (admin only)

**Query Parameters:**
- `user_id` (optional): Filter by user
- `hours` (default: 24): Time window

#### GET `/api/v1/compliance/security-policies`
Get security policies (admin only)

**Query Parameters:**
- `policy_type` (optional): Filter by policy type

#### PUT `/api/v1/compliance/security-policies/{policy_type}`
Update security policy (admin only)

## Security Headers

تمام responses شامل security headers زیر هستند:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`

## Rate Limiting

- **Default**: 100 requests per minute per IP
- **Configurable**: از طریق security policy
- **Implementation**: RateLimitMiddleware

## Best Practices

1. **Audit Logging**: تمام actions مهم را log کنید
2. **Password Policy**: از password policy قوی استفاده کنید
3. **Encryption**: داده‌های حساس را encrypt کنید
4. **Session Management**: session timeout را تنظیم کنید
5. **Compliance Reports**: به صورت منظم گزارش‌ها را بررسی کنید
6. **Suspicious Activity**: فعالیت‌های مشکوک را monitor کنید

## Compliance Standards

سیستم برای compliance با استانداردهای زیر طراحی شده:

- **GDPR**: Data protection و privacy
- **SOC 2**: Security controls
- **ISO 27001**: Information security
- **NIST**: Cybersecurity framework

## Data Retention

سیاست‌های retention برای انواع داده:

- **Sensor Data**: 1 year
- **Audit Logs**: 7 years (compliance requirement)
- **Alerts**: 6 months
- **ML Predictions**: 1 year

## Security Monitoring

### Suspicious Activity Detection

سیستم به صورت خودکار موارد زیر را detect می‌کند:

1. **Multiple Failed Logins**: بیش از 5 بار در 24 ساعت
2. **Excessive Permission Denials**: بیش از 10 بار در 24 ساعت
3. **Unusual Activity Volume**: بیش از 1000 event در 24 ساعت

### Alerts

برای هر suspicious activity یک alert ایجاد می‌شود.

## Integration

### با Authentication:
- Login/logout events logged
- Failed login attempts tracked
- Password changes audited

### با Data Access:
- All data operations logged
- Export operations tracked
- Permission denials recorded

### با User Management:
- User creation/deletion logged
- Role changes audited
- User updates tracked

