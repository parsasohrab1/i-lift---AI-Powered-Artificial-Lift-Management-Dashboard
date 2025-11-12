# راهنمای Authentication و RBAC

## سیستم احراز هویت

این پروژه از JWT (JSON Web Tokens) برای احراز هویت استفاده می‌کند.

### ویژگی‌ها

- **JWT Access Tokens**: برای دسترسی به API (30 دقیقه اعتبار)
- **Refresh Tokens**: برای تمدید access token (30 روز اعتبار)
- **Session Management**: مدیریت session‌ها در پایگاه داده
- **Password Hashing**: استفاده از bcrypt برای hash کردن رمز عبور

## نقش‌ها (Roles)

1. **FIELD_OPERATOR**: اپراتور میدان
   - مشاهده داده‌های سنسور
   - مشاهده چاه‌ها
   - مشاهده هشدارها
   - مشاهده داشبورد

2. **PRODUCTION_ENGINEER**: مهندس تولید
   - تمام دسترسی‌های FIELD_OPERATOR
   - ایجاد و ویرایش داده‌های سنسور
   - مدیریت چاه‌ها
   - مشاهده و تحلیل داده‌ها
   - مدیریت هشدارها

3. **DATA_SCIENTIST**: دانشمند داده
   - مشاهده داده‌ها
   - تحلیل و گزارش‌گیری
   - مشاهده و ایجاد پیش‌بینی‌های ML
   - آموزش مدل‌ها

4. **OPERATIONS_MANAGER**: مدیر عملیات
   - تمام دسترسی‌های PRODUCTION_ENGINEER
   - مشاهده کاربران
   - مدیریت هشدارها

5. **ADMIN**: مدیر سیستم
   - دسترسی کامل به تمام بخش‌ها
   - مدیریت کاربران
   - تنظیمات سیستم

## API Endpoints

### Authentication

- `POST /api/v1/auth/login` - ورود به سیستم
- `POST /api/v1/auth/register` - ثبت کاربر جدید (فقط admin)
- `POST /api/v1/auth/refresh` - تمدید token
- `POST /api/v1/auth/logout` - خروج از سیستم
- `GET /api/v1/auth/me` - اطلاعات کاربر فعلی
- `PUT /api/v1/auth/me` - به‌روزرسانی اطلاعات کاربر
- `POST /api/v1/auth/change-password` - تغییر رمز عبور

### User Management (Admin Only)

- `GET /api/v1/users` - لیست کاربران
- `GET /api/v1/users/{user_id}` - اطلاعات کاربر
- `POST /api/v1/users` - ایجاد کاربر جدید
- `PUT /api/v1/users/{user_id}` - به‌روزرسانی کاربر
- `DELETE /api/v1/users/{user_id}` - حذف کاربر

## استفاده

### 1. ایجاد کاربر Admin

```bash
cd backend
python scripts/create_admin.py --username admin --email admin@ilift.local --password YourSecurePassword
```

### 2. ورود به سیستم

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=YourSecurePassword"
```

پاسخ:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. استفاده از Token

```bash
curl -X GET "http://localhost:8000/api/v1/sensors" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. تمدید Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

## Permissions

هر endpoint نیاز به permission خاصی دارد. برای مثال:

```python
from app.core.dependencies import get_current_active_user
from app.core.permissions import Permission, has_permission

@router.get("/sensors")
async def get_sensors(
    current_user: User = Depends(get_current_active_user)
):
    if not has_permission(current_user.role, Permission.VIEW_SENSOR_DATA):
        raise HTTPException(status_code=403, detail="Permission denied")
    # ...
```

## Security Features

- **Security Headers**: اضافه شدن headerهای امنیتی به تمام پاسخ‌ها
- **CORS**: پیکربندی CORS برای frontend
- **Rate Limiting**: محدودیت تعداد درخواست‌ها
- **Password Hashing**: استفاده از bcrypt
- **Token Expiration**: انقضای خودکار token‌ها
- **Session Management**: مدیریت session در پایگاه داده

## نکات امنیتی

1. **SECRET_KEY**: حتماً در production تغییر دهید
2. **Password Policy**: رمز عبور باید حداقل 8 کاراکتر باشد
3. **HTTPS**: در production حتماً از HTTPS استفاده کنید
4. **Token Storage**: token‌ها را در localStorage یا cookie امن ذخیره کنید
5. **Refresh Token Rotation**: در صورت نیاز می‌توانید refresh token rotation را فعال کنید

