# Architecture Documentation

## Overview

IntelliLift AI Dashboard یک سیستم توزیع‌شده با معماری microservices است که برای پردازش real-time داده‌های سنسور و ارائه تحلیل‌های هوشمند طراحی شده است.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Web UI     │  │  Mobile App  │  │  API Client  │     │
│  │  (Next.js)   │  │   (Future)   │  │   (Future)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    API Gateway                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  FastAPI     │  │  Auth        │  │  Rate Limit  │     │
│  │  Backend     │  │  Middleware  │  │  Middleware  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│   Services   │ │  Services  │ │  Services  │
│   Layer      │ │   Layer    │ │   Layer    │
└──────────────┘ └────────────┘ └────────────┘
```

### Component Architecture

#### 1. Data Ingestion Layer

**Components:**
- MQTT Client
- OPC-UA Client
- REST API Handler
- Kafka Producer

**Responsibilities:**
- دریافت داده از منابع مختلف
- اعتبارسنجی اولیه
- ارسال به Kafka

#### 2. Data Processing Layer

**Components:**
- Kafka Consumer
- Stream Processor
- Feature Engineer
- Data Validator
- Database Writer

**Responsibilities:**
- پردازش real-time داده‌ها
- استخراج ویژگی‌ها
- اعتبارسنجی و پاکسازی
- ذخیره در دیتابیس

#### 3. ML/AI Layer

**Components:**
- Anomaly Detection Service
- Predictive Maintenance Service
- Model Server
- Training Pipeline

**Responsibilities:**
- تشخیص ناهنجاری‌ها
- پیش‌بینی خرابی
- سرویس‌دهی مدل‌ها
- آموزش مدل‌ها

#### 4. Application Layer

**Components:**
- FastAPI Backend
- Next.js Frontend
- Alert System
- Notification Service

**Responsibilities:**
- ارائه API
- رابط کاربری
- مدیریت alerts
- ارسال notifications

#### 5. Storage Layer

**Components:**
- TimescaleDB (Time-series data)
- Redis (Caching)
- Kafka (Message streaming)
- S3 (Data lake - future)

**Responsibilities:**
- ذخیره داده‌های time-series
- Caching
- Message queuing
- Long-term storage

## Data Flow

### Real-time Data Flow

```
Sensor → MQTT/OPC-UA → Kafka → Stream Processor → Feature Engineer → TimescaleDB
                                                                    ↓
                                                              ML Services
                                                                    ↓
                                                              Alert System
```

### Batch Processing Flow

```
Historical Data → Batch Processor → Feature Store → ML Training → Model Registry
```

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Query, Zustand
- **Visualization**: Recharts, Leaflet
- **Forms**: React Hook Form, Zod

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic
- **Authentication**: JWT
- **Task Queue**: Celery (future)

### Data Processing
- **Streaming**: Apache Kafka
- **Processing**: Custom stream processor
- **Feature Engineering**: Pandas, NumPy
- **Validation**: Great Expectations, Pandera

### ML/AI
- **ML Framework**: Scikit-learn, TensorFlow, PyTorch
- **MLOps**: MLflow
- **Feature Store**: Feast (future)
- **Model Serving**: Custom model server

### Infrastructure
- **Database**: PostgreSQL 15+ with TimescaleDB
- **Cache**: Redis 7+
- **Message Queue**: Apache Kafka
- **Containerization**: Docker, Docker Compose
- **Monitoring**: Prometheus, Grafana
- **CI/CD**: GitHub Actions

## Security Architecture

### Authentication & Authorization

```
User → Login → JWT Token → API Request → Auth Middleware → RBAC Check → Resource
```

### Security Layers

1. **Network Layer**: TLS/SSL encryption
2. **Application Layer**: JWT authentication
3. **Data Layer**: Encryption at rest
4. **Audit Layer**: Comprehensive logging

## Scalability

### Horizontal Scaling

- **Stateless Services**: API services can scale horizontally
- **Database**: Read replicas for TimescaleDB
- **Cache**: Redis cluster
- **Message Queue**: Kafka cluster

### Vertical Scaling

- **Database**: Optimized queries, indexing
- **Processing**: Parallel processing
- **ML Services**: GPU acceleration (future)

## Performance Optimization

### Caching Strategy

- **API Responses**: Redis cache with TTL
- **Database Queries**: Query result caching
- **Static Assets**: CDN (future)

### Database Optimization

- **Indexing**: Strategic indexes on time-series data
- **Partitioning**: TimescaleDB hypertables
- **Compression**: Automatic compression policies

### Frontend Optimization

- **Code Splitting**: Next.js automatic code splitting
- **Image Optimization**: Next.js Image component
- **SSR/SSG**: Server-side rendering where applicable

## Monitoring & Observability

### Metrics Collection

- **Application Metrics**: Prometheus
- **Business Metrics**: Custom metrics
- **System Metrics**: System resources

### Logging

- **Structured Logging**: Structured logs with context
- **Log Aggregation**: Centralized logging (future)
- **Audit Logging**: All security events

### Tracing

- **Distributed Tracing**: Request tracing across services
- **Performance Monitoring**: Response time tracking

## Deployment Architecture

### Development

```
Local Machine → Docker Compose → All Services
```

### Production

```
Load Balancer → API Gateway → Application Services → Database Cluster
                                      ↓
                              Monitoring Stack
```

## Future Enhancements

1. **Microservices**: Split into separate microservices
2. **Kubernetes**: Container orchestration
3. **Service Mesh**: Istio or Linkerd
4. **Event Sourcing**: Event-driven architecture
5. **CQRS**: Command Query Responsibility Segregation

