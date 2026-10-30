# IntelliLift AI Dashboard

**AI-Powered Artificial Lift Management Dashboard**

A comprehensive system for monitoring, analyzing and optimizing Artificial Lift systems in the oil and gas industry using artificial intelligence and machine learning.

## 📋 Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation and Setup](#installation-and-setup)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

## ✨ Features

### 🔄 Real-time Data Processing
- **Data Ingestion**: Support for MQTT, OPC-UA, REST API
- **Stream Processing**: Real-time processing with Apache Kafka
- **Data Validation**: Automatic data validation and cleaning
- **Feature Engineering**: Automatic feature extraction

### 🤖 Machine Learning & AI
- **Anomaly Detection**: Anomaly detection with Isolation Forest
- **Predictive Maintenance**: Equipment failure prediction
- **Failure Prediction**: Failure time prediction
- **Optimization Recommendations**: Optimization recommendations

### 📊 Analytics & Visualization
- **Real-time Dashboard**: Real-time dashboard with latency under 3 seconds
- **Historical Analysis**: Historical trend analysis
- **Geographic Mapping**: Geographic mapping of wells
- **Custom KPIs**: Configurable KPI widgets

### 🔔 Alerting & Notifications
- **Multi-channel Alerts**: SMS, Email, In-app notifications
- **Alert Rules Engine**: Configurable rules engine
- **Severity Levels**: Different severity levels
- **Alert Resolution**: Tracking and resolving alerts

### 🔒 Security & Compliance
- **Authentication**: JWT-based authentication
- **RBAC**: Role-Based Access Control
- **Audit Logging**: Logging all activities
- **Data Encryption**: Encryption of sensitive data
- **Compliance Reports**: Compliance reports

### 📈 Monitoring & Observability
- **Prometheus Metrics**: Metrics collection
- **Health Checks**: Service health checks
- **System Monitoring**: System resource monitoring
- **Distributed Tracing**: Request tracing

## 🏗️ System Architecture

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

## 🚀 Installation and Setup

### Prerequisites

- **Node.js** 20+
- **Python** 3.11+
- **Docker** & Docker Compose
- **PostgreSQL** 15+ (with the TimescaleDB extension)
- **Redis** 7+
- **Kafka** (optional for production)

### Quick Installation

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

For the complete installation guide, see [README_SETUP.md](README_SETUP.md).

## 📁 Project Structure

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

## 📚 Documentation

### Main Documentation

- **[Setup Guide](README_SETUP.md)** - Installation and setup guide
- **[Architecture Documentation](docs/ARCHITECTURE.md)** - System architecture
- **[API Documentation](docs/API.md)** - Complete API documentation
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Deployment guide
- **[User Guide](docs/USER_GUIDE.md)** - User guide

### Backend Documentation

- **[Authentication](backend/README_AUTH.md)** - Authentication system
- **[Data Ingestion](backend/README_INGESTION.md)** - Data ingestion
- **[Data Processing](backend/README_PROCESSING.md)** - Data processing
- **[Alerts & Notifications](backend/README_ALERTS_NOTIFICATIONS.md)** - Alert system
- **[Security & Compliance](backend/README_SECURITY_COMPLIANCE.md)** - Security and compliance
- **[Monitoring](backend/README_MONITORING.md)** - Monitoring
- **[Testing](backend/README_TESTING.md)** - Tests

### API Documentation

- **[Data API](backend/README_API_DATA.md)** - Data API
- **[Analytics API](backend/README_API_ANALYTICS.md)** - Analytics API
- **[ML API](backend/README_API_ML.md)** - Machine learning API
- **[Alerts API](backend/README_API_ALERTS.md)** - Alerts API

## 💻 Development

### Setting Up the Development Environment

```bash
# Install dependencies
npm run install:all

# Start development servers
npm run dev

# Backend will run on http://localhost:8000
# Frontend will run on http://localhost:3000
```

### Useful Commands

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

## 🧪 Testing

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

For more information, see [Testing Documentation](backend/README_TESTING.md).

## 🚢 Deployment

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

For the complete production deployment guide, see [Deployment Guide](docs/DEPLOYMENT.md).

## 🤝 Contributing

We welcome your contributions! Please see the [Contributing Guide](docs/CONTRIBUTING.md).

### Contribution Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📊 Technologies

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

For support and questions:
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: [Full Documentation](docs/)
- **Email**: support@example.com

---

**Made with ❤️ for the Oil & Gas Industry**


## Articles

See [docs/ARTICLE.md](docs/ARTICLE.md) for the article prepared from this product (in preparation) and [docs/TRL.md](docs/TRL.md) for its TRL 4 evidence.
