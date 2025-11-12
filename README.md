# IntelliLift AI Dashboard

**AI-Powered Artificial Lift Management Dashboard**

یک سیستم جامع برای مانیتورینگ، تحلیل و بهینه‌سازی سیستم‌های Artificial Lift در صنعت نفت و گاز با استفاده از هوش مصنوعی و یادگیری ماشین.

## 📋 فهرست مطالب

- [ویژگی‌ها](#ویژگی‌ها)
- [معماری سیستم](#معماری-سیستم)
- [نصب و راه‌اندازی](#نصب-و-راه‌اندازی)
- [ساختار پروژه](#ساختار-پروژه)
- [مستندات](#مستندات)
- [توسعه](#توسعه)
- [تست](#تست)
- [استقرار](#استقرار)
- [مشارکت](#مشارکت)

## ✨ ویژگی‌ها

### 🔄 Real-time Data Processing
- **Data Ingestion**: پشتیبانی از MQTT, OPC-UA, REST API
- **Stream Processing**: پردازش real-time با Apache Kafka
- **Data Validation**: اعتبارسنجی و پاکسازی خودکار داده‌ها
- **Feature Engineering**: استخراج ویژگی‌های خودکار

### 🤖 Machine Learning & AI
- **Anomaly Detection**: تشخیص ناهنجاری‌ها با Isolation Forest
- **Predictive Maintenance**: پیش‌بینی خرابی تجهیزات
- **Failure Prediction**: پیش‌بینی زمان خرابی
- **Optimization Recommendations**: توصیه‌های بهینه‌سازی

### 📊 Analytics & Visualization
- **Real-time Dashboard**: داشبورد real-time با latency کمتر از 3 ثانیه
- **Historical Analysis**: تحلیل روندهای تاریخی
- **Geographic Mapping**: نقشه‌برداری جغرافیایی چاه‌ها
- **Custom KPIs**: ویجت‌های KPI قابل تنظیم

### 🔔 Alerting & Notifications
- **Multi-channel Alerts**: SMS, Email, In-app notifications
- **Alert Rules Engine**: موتور قوانین قابل تنظیم
- **Severity Levels**: سطوح مختلف severity
- **Alert Resolution**: ردیابی و حل alerts

### 🔒 Security & Compliance
- **Authentication**: JWT-based authentication
- **RBAC**: Role-Based Access Control
- **Audit Logging**: ثبت تمام فعالیت‌ها
- **Data Encryption**: رمزنگاری داده‌های حساس
- **Compliance Reports**: گزارش‌های compliance

### 📈 Monitoring & Observability
- **Prometheus Metrics**: جمع‌آوری metrics
- **Health Checks**: بررسی سلامت سرویس‌ها
- **System Monitoring**: مانیتورینگ منابع سیستم
- **Distributed Tracing**: ردیابی درخواست‌ها

## 🏗️ معماری سیستم

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Sources Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  MQTT   │  │ OPC-UA   │  │   REST   │  │  Files   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  Ingestion Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  Kafka   │  │ Validator │  │ Enricher │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                 Processing Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Stream  │  │ Feature  │  │   ML     │  │ Analytics│   │
│  │ Processor│  │ Engineer │  │ Pipeline │  │  Engine  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Storage Layer                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │TimescaleDB│ │  Redis   │  │  Kafka   │  │   S3     │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                Application Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  FastAPI │  │  Next.js  │  │  Alert   │  │  Report  │   │
│  │  Backend │  │ Frontend  │  │  System  │  │ Generator│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها

- **Node.js** 20+
- **Python** 3.11+
- **Docker** & Docker Compose
- **PostgreSQL** 15+ (با TimescaleDB extension)
- **Redis** 7+
- **Kafka** (اختیاری برای production)

### نصب سریع

```bash
# Clone repository
git clone <repository-url>
cd i-lift---AI-Powered-Artificial-Lift-Management-Dashboard

# Install all dependencies
npm run install:all

# Start with Docker
docker-compose up -d

# Or start manually
npm run dev
```

برای راهنمای کامل نصب، به [README_SETUP.md](README_SETUP.md) مراجعه کنید.

## 📁 ساختار پروژه

```
i-lift---AI-Powered-Artificial-Lift-Management-Dashboard/
├── frontend/                 # Next.js Frontend Application
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # Utilities and helpers
│   │   └── types/           # TypeScript type definitions
│   └── package.json
│
├── backend/                  # FastAPI Backend Application
│   ├── app/
│   │   ├── api/             # API routes and endpoints
│   │   ├── core/            # Core configuration
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic services
│   │   └── utils/           # Utility functions
│   ├── tests/               # Test suite
│   ├── database/            # Database migrations
│   └── requirements.txt
│
├── data-processing/          # Data Processing Services
│   ├── synthetic_data_generator.py
│   └── requirements.txt
│
├── ml-services/             # ML/AI Services
│   ├── anomaly_detection.py
│   ├── predictive_maintenance.py
│   ├── model_server.py
│   └── requirements.txt
│
├── monitoring/              # Monitoring Configuration
│   └── prometheus.yml
│
├── docker-compose.yml       # Docker Compose configuration
├── Makefile                 # Make commands
└── package.json            # Root package.json
```

## 📚 مستندات

### مستندات اصلی

- **[Setup Guide](README_SETUP.md)** - راهنمای نصب و راه‌اندازی
- **[Architecture Documentation](docs/ARCHITECTURE.md)** - معماری سیستم
- **[API Documentation](docs/API.md)** - مستندات کامل API
- **[Deployment Guide](docs/DEPLOYMENT.md)** - راهنمای استقرار
- **[User Guide](docs/USER_GUIDE.md)** - راهنمای کاربر

### مستندات Backend

- **[Authentication](backend/README_AUTH.md)** - سیستم احراز هویت
- **[Data Ingestion](backend/README_INGESTION.md)** - دریافت داده
- **[Data Processing](backend/README_PROCESSING.md)** - پردازش داده
- **[Alerts & Notifications](backend/README_ALERTS_NOTIFICATIONS.md)** - سیستم هشدار
- **[Security & Compliance](backend/README_SECURITY_COMPLIANCE.md)** - امنیت و compliance
- **[Monitoring](backend/README_MONITORING.md)** - مانیتورینگ
- **[Testing](backend/README_TESTING.md)** - تست‌ها

### مستندات API

- **[Data API](backend/README_API_DATA.md)** - API داده‌ها
- **[Analytics API](backend/README_API_ANALYTICS.md)** - API تحلیل‌ها
- **[ML API](backend/README_API_ML.md)** - API یادگیری ماشین
- **[Alerts API](backend/README_API_ALERTS.md)** - API هشدارها

## 💻 توسعه

### راه‌اندازی محیط توسعه

```bash
# Install dependencies
npm run install:all

# Start development servers
npm run dev

# Backend will run on http://localhost:8000
# Frontend will run on http://localhost:3000
```

### دستورات مفید

```bash
# Development
npm run dev              # Start all services
npm run dev:frontend     # Start frontend only
npm run dev:backend      # Start backend only

# Build
npm run build            # Build all projects
npm run build:frontend   # Build frontend
npm run build:backend    # Build backend

# Testing
npm run test             # Run all tests
npm run test:frontend    # Run frontend tests
npm run test:backend     # Run backend tests

# Linting
npm run lint             # Run all linters
npm run lint:frontend    # Lint frontend
npm run lint:backend     # Lint backend

# Docker
npm run docker:build     # Build Docker images
npm run docker:up        # Start Docker containers
npm run docker:down      # Stop Docker containers
```

## 🧪 تست

### Backend Tests

```bash
cd backend
pytest                    # Run all tests
pytest --cov=app         # Run with coverage
pytest tests/test_auth.py # Run specific test file
```

### Frontend Tests

```bash
cd frontend
npm test                  # Run all tests
npm test -- --coverage   # Run with coverage
npm test -- --watch      # Watch mode
```

برای اطلاعات بیشتر، به [Testing Documentation](backend/README_TESTING.md) مراجعه کنید.

## 🚢 استقرار

### Docker Deployment

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Production Deployment

برای راهنمای کامل استقرار در production، به [Deployment Guide](docs/DEPLOYMENT.md) مراجعه کنید.

## 🤝 مشارکت

ما از مشارکت شما استقبال می‌کنیم! لطفاً به [Contributing Guide](docs/CONTRIBUTING.md) مراجعه کنید.

### فرآیند مشارکت

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📊 تکنولوژی‌ها

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **React Query** - Data fetching
- **Leaflet** - Maps

### Backend
- **FastAPI** - Python web framework
- **SQLAlchemy** - ORM
- **TimescaleDB** - Time-series database
- **Redis** - Caching
- **Kafka** - Message streaming
- **Pydantic** - Data validation

### ML/AI
- **Scikit-learn** - Machine learning
- **TensorFlow** - Deep learning
- **XGBoost** - Gradient boosting
- **MLflow** - ML lifecycle management

### Infrastructure
- **Docker** - Containerization
- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **GitHub Actions** - CI/CD

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **AI Systems Architect** - Initial work

## 🙏 Acknowledgments

- TimescaleDB team for excellent time-series database
- FastAPI team for the amazing framework
- Next.js team for the powerful React framework

## 📞 Support

برای پشتیبانی و سوالات:
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: [Full Documentation](docs/)
- **Email**: support@example.com

---

**Made with ❤️ for the Oil & Gas Industry**
