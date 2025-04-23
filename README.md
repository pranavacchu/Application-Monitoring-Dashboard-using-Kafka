# Application Monitoring Dashboard

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A comprehensive log analytics and monitoring platform built using modern cloud-native technologies. This solution collects, processes, and visualizes logs and metrics from various services to provide real-time insights into application performance.

## 📋 Overview

This platform integrates several open-source components to create a robust monitoring solution:

- **API Server**: Flask-based REST API that generates sample logs and metrics
- **Kafka**: Real-time message streaming for log data
- **Log Consumer**: Processes log streams from Kafka and forwards them to storage
- **MySQL**: Persistent storage for structured log data
- **Prometheus**: Time-series database for metrics collection and storage
- **Loki**: Scalable log aggregation system
- **Grafana**: Visualization platform for metrics and logs

## 🏗️ Architecture

```
┌─────────────┐     ┌───────┐     ┌───────────────┐     ┌─────────┐
│  API Server │────▶│ Kafka │────▶│ Log Consumer  │────▶│ MySQL   │
└─────────────┘     └───────┘     └───────────────┘     └─────────┘
       │                                                     │
       ▼                                                     ▼
┌─────────────┐     ┌───────┐     ┌───────────────┐     ┌─────────┐
│ Prometheus  │◀───▶│ Loki  │◀───▶│    Grafana    │◀───▶│ Browser │
└─────────────┘     └───────┘     └───────────────┘     └─────────┘
```

## ⚙️ Prerequisites

- Docker Engine v20.10.0+
- Docker Compose v2.0.0+
- Windows Subsystem for Linux (WSL) if running on Windows
- Curl (for testing API endpoints)
- 4GB+ RAM available for Docker

## 🚀 Setup and Deployment

### 1. Clone the repository

```bash
git clone <repository-url>
cd Application-Monitoring-Dashboard
```

### 2. Deploy the stack

```bash
docker-compose up -d
```

### 3. Verify services status

```bash
docker-compose ps
```

All services should show a "running" state. Allow a few minutes for all services to initialize properly.

## 🧪 System Verification

### API Health Check

```bash
curl http://localhost:5000/api/health
# Expected response: {"status":"healthy","timestamp":"2023-xx-xx xx:xx:xx"}
```

### Test Data Generation

```bash
# Create test user
curl -X POST -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com"}' \
  http://localhost:5000/api/users

# Retrieve users
curl http://localhost:5000/api/users
```

## 🔗 Accessing Services

| Service    | URL                   | Default Credentials |
|------------|----------------------|---------------------|
| Grafana    | http://localhost:3000 | admin / admin       |
| Prometheus | http://localhost:9090 | N/A                 |
| API Server | http://localhost:5000 | N/A                 |

## 💾 Data Persistence

The platform utilizes Docker named volumes for data persistence:

| Volume Name      | Purpose                                |
|------------------|----------------------------------------|
| `mysql_data`     | MySQL database files                   |
| `grafana_data`   | Grafana dashboards and configurations  |
| `loki_data`      | Loki log storage                       |
| `loki_wal`       | Loki write-ahead log                   |
| `prometheus_data`| Prometheus metrics storage             |

## 📊 Grafana Dashboard Configuration

### 1. Initial Configuration

1. Navigate to [Grafana](http://localhost:3000) in your browser
2. Login with default credentials (admin/admin)
3. Change the password when prompted

### 2. Data Source Configuration

#### Prometheus Data Source

1. Navigate to Configuration → Data Sources → Add data source
2. Select "Prometheus"
3. Configure:
   - Name: `Prometheus`
   - URL: `http://prometheus:9090`
4. Click "Save & Test"

#### MySQL Data Source

1. Navigate to Configuration → Data Sources → Add data source
2. Select "MySQL"
3. Configure:
   - Name: `MySQL`
   - Host: `mysql:3306`
   - Database: `log_analytics`
   - User: `root`
   - Password: `rootpassword`
4. Click "Save & Test"

#### Loki Data Source

1. Navigate to Configuration → Data Sources → Add data source
2. Select "Loki"
3. Configure:
   - Name: `Loki`
   - URL: `http://loki:3100`
4. Click "Save & Test"

### 3. Dashboard Creation

#### Key Performance Metrics Dashboard

1. Import a new dashboard (+ → Import)
2. Upload the provided `kpi_dashboard.json` file or use dashboard ID `12345`
3. Select appropriate data sources

#### Custom Dashboard Creation

For manual dashboard creation:

1. Create a new dashboard (+ → Dashboard)
2. Add panels for:
   - Request count per endpoint (Prometheus)
   - 95th percentile response time (Prometheus)
   - Error rates (Prometheus)
   - Real-time logs (Loki)
3. Configure auto-refresh (5s recommended)
4. Save with appropriate name and tags

## 🔧 Troubleshooting

### Common Issues

| Issue | Resolution |
|-------|------------|
| Service fails to start | Check logs: `docker-compose logs <service-name>` |
| Cannot connect to services | Ensure ports aren't being used by other applications |
| High memory usage | Increase Docker memory allocation in Docker Desktop settings |

### Recovery Procedures

```bash
# Restart a specific service
docker-compose restart <service-name>

# Rebuild a service after code changes
docker-compose up -d --build <service-name>

# Complete system reset (Warning: Deletes all data)
docker-compose down -v
docker-compose up -d
```

## 🛠️ Development

### Local Development Setup

1. Create virtual environment: `python -m venv venv`
2. Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`

### Code Quality Guidelines

- Follow PEP 8 for Python code
- Use meaningful commit messages
- Write tests for new features

## 📝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

© 2024 Application Monitoring Dashboard Team