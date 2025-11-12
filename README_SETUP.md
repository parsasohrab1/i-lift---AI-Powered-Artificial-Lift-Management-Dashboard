# راهنمای راه‌اندازی پروژه

## پیش‌نیازها

- Node.js 20+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (با TimescaleDB)

## نصب و راه‌اندازی

### 1. نصب وابستگی‌ها

```bash
# نصب وابستگی‌های اصلی
npm run install:all

# یا به صورت جداگانه:
npm install
cd frontend && npm install
cd ../backend && pip install -r requirements.txt
cd ../data-processing && pip install -r requirements.txt
cd ../ml-services && pip install -r requirements.txt
```

### 2. راه‌اندازی با Docker

```bash
# ساخت و راه‌اندازی تمام سرویس‌ها
docker-compose up -d

# یا فقط ساخت
docker-compose build
```

### 3. راه‌اندازی دستی

#### Backend API
```bash
cd backend
cp .env.example .env
# ویرایش .env با تنظیمات مناسب
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm run dev
```

### 4. تنظیمات پایگاه داده

```bash
# اجرای migrations
cd backend
alembic upgrade head

# یا با Docker
docker-compose exec backend alembic upgrade head
```

## ساختار پروژه

```
i-lift---AI-Powered-Artificial-Lift-Management-Dashboard/
├── frontend/                 # Next.js Frontend
│   ├── src/
│   │   ├── app/            # Next.js App Router
│   │   ├── components/     # React Components
│   │   ├── lib/           # Utilities
│   │   └── types/         # TypeScript Types
│   └── package.json
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/           # API Routes
│   │   ├── core/          # Core Config
│   │   ├── models/        # Database Models
│   │   ├── schemas/       # Pydantic Schemas
│   │   └── services/      # Business Logic
│   └── requirements.txt
├── data-processing/         # Data Processing Services
│   └── synthetic_data_generator.py
├── ml-services/            # ML/AI Services
│   ├── anomaly_detection.py
│   └── predictive_maintenance.py
├── monitoring/             # Monitoring Configs
│   └── prometheus.yml
├── docker-compose.yml
└── package.json
```

## دستورات مفید

```bash
# اجرای توسعه
npm run dev

# ساخت پروژه
npm run build

# تست
npm run test

# Linting
npm run lint

# Docker
npm run docker:build
npm run docker:up
npm run docker:down
```

## پورت‌ها

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9090
- MLflow: http://localhost:5000

## نکات مهم

1. فایل `.env` را در backend تنظیم کنید
2. پایگاه داده باید TimescaleDB extension داشته باشد
3. برای تولید داده‌های سنتتیک از `data-processing/synthetic_data_generator.py` استفاده کنید

