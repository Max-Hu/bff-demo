# CI/CD Scan API Server

This project provides a secure API layer to trigger and monitor Jenkins pipelines related to software scanning tasks (such as FOSS, SAST, DAST), receive callback results, and store scan outcomes into a backend system (Oracle DB). It is designed to support extensibility, observability, and integration with modern UI dashboards.

## 🚀 Features

- **RESTful API**: Clean, documented API endpoints for scan management
- **Jenkins Integration**: Seamless integration with Jenkins pipelines
- **Database Storage**: Oracle database for storing scan results and logs
- **Security**: API key authentication for all endpoints
- **Monitoring**: Health checks and comprehensive logging
- **Containerization**: Docker support for easy deployment
- **Testing**: Comprehensive test suite with pytest

## 📋 Prerequisites

- Python 3.11+
- Oracle Database (or Oracle Express Edition)
- Jenkins Server
- Docker & Docker Compose (for containerized deployment)

## 🛠️ Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bff
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   python -m app.main
   ```

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Access the application**
   - API Server: http://localhost:8000
   - Jenkins: http://localhost:8080
   - API Documentation: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | Secret API key for authentication | `your-secret-api-key-here` |
| `JENKINS_URL` | Jenkins server URL | `http://localhost:8080` |
| `JENKINS_USERNAME` | Jenkins username | - |
| `JENKINS_PASSWORD` | Jenkins password | - |
| `JENKINS_TOKEN` | Jenkins API token | - |
| `ORACLE_HOST` | Oracle database host | `localhost` |
| `ORACLE_PORT` | Oracle database port | `1521` |
| `ORACLE_SERVICE` | Oracle service name | `XE` |
| `ORACLE_USERNAME` | Oracle username | `scan_user` |
| `ORACLE_PASSWORD` | Oracle password | `scan_password` |

## 📡 API Endpoints

### Authentication
All endpoints require API key authentication via the `Authorization: Bearer <api-key>` header.

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/scan/trigger` | Trigger a Jenkins scan job |
| `GET` | `/api/scan/status` | Get build status |
| `GET` | `/api/scan/log` | Get build logs |
| `POST` | `/api/scan/callback` | Jenkins callback endpoint |
| `GET` | `/api/scan/result` | Get final scan result |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | API documentation |

### Example Usage

#### Trigger a Scan
```bash
curl -X POST "http://localhost:8000/api/scan/trigger" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "job_name": "ci-nexus-scan",
    "parameters": {
      "nexusURL": "https://nexus.company.com/artifact/projectX/1.0.0"
    }
  }'
```

#### Get Build Status
```bash
curl -X GET "http://localhost:8000/api/scan/status?job_name=ci-nexus-scan&build_number=123" \
  -H "Authorization: Bearer your-api-key"
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest tests/ --cov=app --cov-report=html
```

## 📊 Database Schema

The application creates two main tables:

### scan_results
- `id`: Primary key
- `job_name`: Jenkins job name
- `build_number`: Build number
- `status`: Build status
- `results`: JSON results data
- `timestamp`: Result timestamp
- `created_at`: Record creation time

### scan_logs
- `id`: Primary key
- `job_name`: Jenkins job name
- `build_number`: Build number
- `log_content`: Build log content
- `timestamp`: Log timestamp

## 🔒 Security

- **API Key Authentication**: All endpoints require valid API key
- **Input Validation**: All inputs are validated using Pydantic models
- **Error Handling**: Comprehensive error handling without information leakage
- **Logging**: Secure logging without sensitive data exposure

## 📈 Monitoring

- **Health Check**: `/health` endpoint for monitoring
- **Logging**: Structured logging with configurable levels
- **Metrics**: Built-in FastAPI metrics (can be extended)

## 🚀 Deployment

### Production Deployment

1. **Set up Oracle Database**
   ```sql
   CREATE USER scan_user IDENTIFIED BY scan_password;
   GRANT CONNECT, RESOURCE TO scan_user;
   ```

2. **Configure Jenkins**
   - Set up scan jobs
   - Configure webhook callbacks to `/api/scan/callback`

3. **Deploy with Docker**
   ```bash
   docker build -t cicd-scan-api .
   docker run -d -p 8000:8000 --env-file .env cicd-scan-api
   ```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs for debugging information 