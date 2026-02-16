# Deployment Guide

This guide covers deploying the Document Generation System to production environments.

## Prerequisites

- Python 3.8+
- LaTeX distribution installed and in PATH
- Tesseract OCR installed (for image processing)
- Google Gemini API credentials

## Environment Setup

### 1. Configure Environment Variables

Create a `.env` file in the `docgen/` directory:

```bash
cp docgen/.env.example docgen/.env
```

Edit `.env` with your configuration:

```env
GEMINI_API_KEY=your_api_key_here
OUTPUT_DIR=/var/lib/docgen/output
LOG_LEVEL=INFO
LOG_FILE=/var/log/docgen/docgen.log
API_RETRIES=5
CLEANUP_OLD_SESSIONS_DAYS=7
```

### 2. Install Dependencies

For production, only install required packages:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r docgen/requirements.txt
```

## Deployment Options

### Option 1: Docker Deployment

#### Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-extra \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY docgen/ /app/docgen/

# Install Python dependencies
RUN pip install --no-cache-dir -r docgen/requirements.txt

# Create output directory
RUN mkdir -p /app/generated_documents

# Set environment
ENV LOG_FILE=/var/log/docgen/docgen.log
ENV OUTPUT_DIR=/app/generated_documents

ENTRYPOINT ["python", "docgen/main.py"]
```

#### Build and Run Docker Image

```bash
# Build
docker build -t docgen:latest .

# Run
docker run -e GEMINI_API_KEY="your_key" \
           -v /output:/app/generated_documents \
           -v /logs:/var/log/docgen \
           docgen:latest --help
```

### Option 2: Systemd Service (Linux)

#### Create Service File

Create `/etc/systemd/system/docgen-api.service`:

```ini
[Unit]
Description=Document Generation Service
After=network.target

[Service]
Type=simple
User=docgen
WorkingDirectory=/opt/docgen
Environment="PATH=/opt/docgen/venv/bin"
EnvironmentFile=/etc/docgen/.env
ExecStart=/opt/docgen/venv/bin/python /opt/docgen/docgen/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Enable Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable docgen-api
sudo systemctl start docgen-api
sudo systemctl status docgen-api
```

### Option 3: Cloud Deployment

#### AWS Lambda

1. Create Lambda function with Python 3.10 runtime
2. Configure Lambda Layer for dependencies:

```bash
pip install -r requirements.txt -t python/lib/python3.10/site-packages/
zip -r lambda-layer.zip python/
# Upload as Lambda Layer
```

3. Use handler:

```python
def lambda_handler(event, context):
    from docgen.app import generate_document
    
    result = generate_document(
        event['input_path'],
        event['fields']
    )
    
    return {
        'statusCode': 200,
        'body': {
            'doc_type': result[0],
            'output_path': result[1]
        }
    }
```

#### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/docgen
gcloud run deploy docgen \
    --image gcr.io/PROJECT_ID/docgen \
    --memory 2Gi \
    --timeout 3600 \
    --set-env-vars GEMINI_API_KEY=your_key
```

#### Azure Container Instances

```bash
az container create \
    --resource-group myResourceGroup \
    --name docgen \
    --image your-registry.azurecr.io/docgen:latest \
    --environment-variables GEMINI_API_KEY=your_key \
    --memory 2 \
    --cpu 1
```

## Performance Optimization

### 1. Configure LaTeX Caching

LaTeX files can be cached in production:

```python
# In config_manager.py
LATEX_CACHE_DIR = "/tmp/latex_cache"
MAX_CACHE_SIZE_MB = 1000
```

### 2. Output Directory Setup

Configure persistent storage:

```bash
# Create output directory with proper permissions
sudo mkdir -p /var/lib/docgen/output
sudo chown docgen:docgen /var/lib/docgen/output
sudo chmod 750 /var/lib/docgen/output
```

### 3. Log Rotation

Set up logrotate:

Create `/etc/logrotate.d/docgen`:

```
/var/log/docgen/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 docgen docgen
    sharedscripts
    postrotate
        systemctl reload docgen-api > /dev/null 2>&1 || true
    endscript
}
```

## Monitoring and Logging

### Centralized Logging

Configure to send logs to ELK Stack or external service:

```python
# Update logging_config.json
{
    "handlers": {
        "syslog": {
            "class": "logging.handlers.SysLogHandler",
            "address": "/dev/log",
            "formatter": "standard"
        }
    }
}
```

### Health Checks

Create health check endpoint:

```python
# In main.py
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }
```

### Metrics Collection

Use Prometheus for metrics:

```python
from prometheus_client import Counter, Histogram, start_http_server
import time

documents_generated = Counter('documents_generated_total', 'Total documents generated')
generation_time = Histogram('generation_time_seconds', 'Time to generate document')

@generation_time.time()
def generate_document(...):
    # Generate document
    documents_generated.inc()
```

## Backup and Recovery

### 1. Regular Backups

```bash
# Backup script
#!/bin/bash
OUTPUT_DIR=/var/lib/docgen/output
BACKUP_DIR=/backups/docgen
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

tar -czf $BACKUP_DIR/docgen_$TIMESTAMP.tar.gz $OUTPUT_DIR/
# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete
```

### 2. Disaster Recovery

```bash
# Restore from backup
tar -xzf /backups/docgen/docgen_20240216_120000.tar.gz -C /
systemctl restart docgen-api
```

## Security Hardening

### 1. API Key Management

- Use secrets manager (AWS Secrets Manager, Azure Key Vault)
- Rotate keys regularly
- Never commit keys to version control

### 2. Rate Limiting

```python
# In config_manager
API_RATE_LIMIT_PER_MINUTE = 60
API_RATE_LIMIT_PER_DAY = 10000
```

### 3. Input Validation

- Always validate file types
- Sanitize user inputs
- Set maximum file sizes

### 4. Access Control

```bash
# Restrict file permissions
chmod 750 /opt/docgen
chmod 640 /etc/docgen/.env
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "pdflatex not found" | Install texlive: `sudo apt-get install texlive-latex-extra` |
| "Tesseract not found" | Install OCR: `sudo apt-get install tesseract-ocr` |
| "Permission denied" | Check file/directory permissions and user ownership |
| "API rate limit" | Increase retries in config or add back-off logic |
| "Out of memory" | Increase container memory or reduce batch size |

### Monitoring Commands

```bash
# Check service status
systemctl status docgen-api

# View recent logs
journalctl -u docgen-api -n 50

# Monitor resource usage
docker stats docgen

# Check API health
curl http://localhost:8000/health
```

## Performance Benchmarks

Typical performance metrics:

- **Document extraction**: 100-500ms (depends on file size)
- **Document classification**: 1-3s (API call)
- **PDF generation**: 500ms-2s (LaTeX compilation)
- **Total per document**: 2-5s

## Upgrading

### Deployment Upgrade

```bash
# Pull updates
git pull origin main

# Install new dependencies
pip install -r docgen/requirements.txt

# Run tests
make test

# Restart service
systemctl restart docgen-api
```

### Zero-Downtime Deployment

Use load balancer with multiple instances:

1. Start new version on secondary instance
2. Run health checks
3. Switch traffic to new instance
4. Stop old version

## Production Checklist

- [ ] Environment variables configured
- [ ] LaTeX and Tesseract installed
- [ ] Backup strategy in place
- [ ] Logging configured
- [ ] Monitoring enabled
- [ ] Security hardened
- [ ] Health checks implemented
- [ ] Rate limiting configured
- [ ] API keys secured
- [ ] Documentation updated
- [ ] Team trained on deployment
- [ ] Disaster recovery plan documented

## Support

For production issues:

1. Check logs: `journalctl -u docgen-api`
2. Review error messages in application logs
3. Consult DEPLOYMENT.md troubleshooting section
4. Contact development team

## References

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS Lambda Deployment](https://docs.aws.amazon.com/lambda/)
- [Google Cloud Run](https://cloud.google.com/run/docs)
