# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

تمام API endpoints (به جز `/auth/login` و `/auth/register`) نیاز به authentication دارند.

### Authentication Header

```
Authorization: Bearer <access_token>
```

### Getting Access Token

```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## API Endpoints

### Authentication

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user&password=pass
```

#### Register (Admin Only)
```http
POST /api/v1/auth/register
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "New User",
  "role": "operator"
}
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "<refresh_token>"
}
```

#### Change Password
```http
POST /api/v1/auth/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_password": "oldpass",
  "new_password": "NewSecurePass123!",
  "confirm_password": "NewSecurePass123!"
}
```

### Wells

#### List Wells
```http
GET /api/v1/wells?page=1&page_size=10&is_active=true
Authorization: Bearer <token>
```

#### Get Well by ID
```http
GET /api/v1/wells/{well_id}
Authorization: Bearer <token>
```

#### Create Well
```http
POST /api/v1/wells
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Well 1",
  "location": "Location 1",
  "latitude": 30.0,
  "longitude": 50.0,
  "well_type": "ESP",
  "is_active": true
}
```

#### Update Well
```http
PUT /api/v1/wells/{well_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Well Name",
  "is_active": false
}
```

#### Delete Well
```http
DELETE /api/v1/wells/{well_id}
Authorization: Bearer <token>
```

### Sensors

#### List Sensors
```http
GET /api/v1/sensors?well_id={well_id}&page=1&page_size=10
Authorization: Bearer <token>
```

#### Get Sensor by ID
```http
GET /api/v1/sensors/{sensor_id}
Authorization: Bearer <token>
```

#### Create Sensor
```http
POST /api/v1/sensors
Authorization: Bearer <token>
Content-Type: application/json

{
  "well_id": "well-1",
  "sensor_type": "temperature",
  "name": "Temperature Sensor 1",
  "unit": "Celsius",
  "min_value": 0.0,
  "max_value": 100.0,
  "is_active": true
}
```

#### Get Sensor Readings
```http
GET /api/v1/sensors/{sensor_id}/readings?hours=24&limit=1000
Authorization: Bearer <token>
```

#### Get Real-time Data
```http
GET /api/v1/sensors/realtime?well_id={well_id}
Authorization: Bearer <token>
```

### Analytics

#### Get KPIs
```http
GET /api/v1/analytics/kpis?well_id={well_id}&hours=24
Authorization: Bearer <token>
```

#### Get Trends
```http
GET /api/v1/analytics/trends?well_id={well_id}&metric=temperature&hours=24
Authorization: Bearer <token>
```

#### Get Comparison
```http
GET /api/v1/analytics/comparison?well_ids=well-1&well_ids=well-2&metric=temperature
Authorization: Bearer <token>
```

#### Get Performance Metrics
```http
GET /api/v1/analytics/performance?well_id={well_id}
Authorization: Bearer <token>
```

### ML Predictions

#### Get Predictions
```http
GET /api/v1/ml/predictions?well_id={well_id}&model_type=anomaly_detection
Authorization: Bearer <token>
```

#### Create Prediction
```http
POST /api/v1/ml/predictions
Authorization: Bearer <token>
Content-Type: application/json

{
  "well_id": "well-1",
  "model_type": "anomaly_detection",
  "prediction": {
    "anomaly_score": 0.85,
    "is_anomaly": true
  }
}
```

#### Anomaly Detection
```http
POST /api/v1/ml/anomaly-detection
Authorization: Bearer <token>
Content-Type: application/json

{
  "well_id": "well-1",
  "sensor_type": "temperature",
  "hours": 24
}
```

### Alerts

#### List Alerts
```http
GET /api/v1/alerts?status=active&severity=critical&page=1&page_size=20
Authorization: Bearer <token>
```

#### Create Alert
```http
POST /api/v1/alerts
Authorization: Bearer <token>
Content-Type: application/json

{
  "well_id": "well-1",
  "sensor_id": "sensor-1",
  "severity": "critical",
  "alert_type": "threshold_exceeded",
  "message": "Temperature exceeded threshold",
  "value": 150.0,
  "threshold": 100.0
}
```

#### Resolve Alert
```http
POST /api/v1/alerts/{alert_id}/resolve
Authorization: Bearer <token>
Content-Type: application/json

{
  "resolution_notes": "Issue resolved"
}
```

### Monitoring

#### Health Check
```http
GET /api/v1/monitoring/health
```

#### Health Summary
```http
GET /api/v1/monitoring/health/summary
Authorization: Bearer <token>
```

#### Metrics Summary
```http
GET /api/v1/monitoring/metrics/summary
Authorization: Bearer <token>
```

#### Prometheus Metrics
```http
GET /api/v1/monitoring/metrics
Authorization: Bearer <admin_token>
```

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message"
}
```

### HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Success, no content
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## Pagination

تمام endpoints که لیست برمی‌گردانند از pagination پشتیبانی می‌کنند.

### Query Parameters

- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 100)

### Response Format

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "pages": 10
}
```

## Rate Limiting

- **Default**: 100 requests per minute per IP
- **Header**: `X-RateLimit-Remaining` shows remaining requests

## Interactive API Documentation

برای مستندات تعاملی و تست API:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Examples

### cURL Examples

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=pass"

# Get Wells
curl -X GET "http://localhost:8000/api/v1/wells" \
  -H "Authorization: Bearer <token>"

# Create Well
curl -X POST "http://localhost:8000/api/v1/wells" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Well 1",
    "location": "Location 1",
    "latitude": 30.0,
    "longitude": 50.0,
    "well_type": "ESP"
  }'
```

### Python Examples

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={"username": "user", "password": "pass"}
)
token = response.json()["access_token"]

# Get Wells
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/v1/wells",
    headers=headers
)
wells = response.json()
```

### JavaScript Examples

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=user&password=pass'
});
const { access_token } = await loginResponse.json();

// Get Wells
const wellsResponse = await fetch('http://localhost:8000/api/v1/wells', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const wells = await wellsResponse.json();
```

