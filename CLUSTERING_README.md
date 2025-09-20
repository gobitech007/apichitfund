# MyChitFund API Clustering Guide

This guide explains how to run the MyChitFund API with multiple workers for high concurrency and production deployment.

## 🚀 Quick Start

### Development (Single Process)
```bash
# Method 1: Using the development script
python start_dev.py

# Method 2: Using the cluster manager
python cluster.py --mode dev

# Method 3: Direct uvicorn
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Production (Multiple Workers)
```bash
# Method 1: Using the production script
python start_prod.py

# Method 2: Using the cluster manager
python cluster.py --mode prod --workers auto

# Method 3: Direct gunicorn
gunicorn app:app -c gunicorn.conf.py
```

## 📋 Available Deployment Modes

### 1. Development Mode
- **Single process** with auto-reload
- **Best for**: Development and debugging
- **Command**: `python cluster.py --mode dev`

### 2. Production Mode (Gunicorn)
- **Multiple workers** managed by Gunicorn
- **Best for**: Production deployment
- **Command**: `python cluster.py --mode prod`

### 3. Uvicorn Cluster Mode
- **Multiple Uvicorn processes** on different ports
- **Best for**: Custom load balancing setups
- **Command**: `python cluster.py --mode uvicorn --workers 4`

### 4. Gunicorn Mode
- **Gunicorn with Uvicorn workers**
- **Best for**: Standard production deployment
- **Command**: `python cluster.py --mode gunicorn --workers 8`

## ⚙️ Worker Configuration

### Automatic Worker Count
```bash
# Auto mode: (CPU cores × 2) + 1
python cluster.py --workers auto

# CPU mode: One worker per CPU core
python cluster.py --workers cpu

# Light mode: Minimal workers (2)
python cluster.py --workers light

# Heavy mode: Maximum workers (CPU cores × 4)
python cluster.py --workers heavy

# Custom count: Specific number of workers
python cluster.py --workers 6
```

### Manual Configuration
Edit `gunicorn.conf.py` to customize:
```python
workers = 8  # Number of worker processes
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
timeout = 30
```

## 🐳 Docker Deployment

### Build and Run
```bash
# Build the image
docker build -t mychitfund-api .

# Run with default configuration
docker run -p 8000:8000 mychitfund-api

# Run with custom worker count
docker run -p 8000:8000 -e WORKERS=8 mychitfund-api

# Run with environment variables
docker run -p 8000:8000 \
  -e DEBUG=false \
  -e ALLOWED_ORIGINS=http://localhost:3000 \
  mychitfund-api
```

### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - WORKERS=8
      - ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
    restart: unless-stopped
```

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode |
| `WORKERS` | `auto` | Number of worker processes |
| `ALLOWED_ORIGINS` | `localhost origins` | CORS allowed origins |
| `TRUSTED_HOSTS` | `localhost,127.0.0.1` | Trusted host names |
| `DATABASE_URL` | - | Database connection string |

## 📊 Monitoring and Health Checks

### Health Check Endpoints
- **Health**: `GET /health` - Basic health status
- **Readiness**: `GET /ready` - Application readiness
- **Metrics**: `GET /metrics` - Application metrics (if enabled)

### Monitoring Workers
```bash
# Monitor workers and auto-restart
python cluster.py --mode prod --monitor

# Check worker status
ps aux | grep gunicorn
ps aux | grep uvicorn
```

### Log Monitoring
```bash
# View logs in real-time
tail -f /var/log/mychitfund-api.log

# View Gunicorn logs
journalctl -u mychitfund-api -f
```

## 🔒 Security Considerations

### Production Security
1. **Non-root user**: Docker runs as non-root user
2. **Trusted hosts**: Configure `TRUSTED_HOSTS` environment variable
3. **CORS origins**: Restrict `ALLOWED_ORIGINS` to your domains
4. **HTTPS**: Use reverse proxy (Nginx) for SSL termination
5. **Rate limiting**: Implement rate limiting middleware

### Reverse Proxy Configuration (Nginx)
```nginx
upstream mychitfund_api {
    server 127.0.0.1:8000;
    # Add more servers for load balancing
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://mychitfund_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🚀 Performance Tuning

### Worker Optimization
- **CPU-bound tasks**: Workers = CPU cores
- **I/O-bound tasks**: Workers = (CPU cores × 2) + 1
- **Mixed workload**: Start with auto mode and adjust based on monitoring

### Database Connections
- **Connection pooling**: Configure SQLAlchemy pool size
- **Pool size**: `pool_size = workers × 2`
- **Max overflow**: `max_overflow = pool_size × 2`

### Memory Management
- **Max requests**: Restart workers after N requests to prevent memory leaks
- **Memory monitoring**: Monitor worker memory usage
- **Garbage collection**: Tune Python GC settings if needed

## 🛠️ Troubleshooting

### Common Issues

#### Workers Not Starting
```bash
# Check if port is available
netstat -tulpn | grep :8000

# Check Gunicorn installation
pip install gunicorn

# Check configuration
python -c "import gunicorn.conf; print('Config OK')"
```

#### High Memory Usage
```bash
# Monitor worker memory
ps aux --sort=-%mem | grep -E "(gunicorn|uvicorn)"

# Reduce max_requests in gunicorn.conf.py
max_requests = 500
max_requests_jitter = 50
```

#### Database Connection Issues
```bash
# Check database connectivity
python -c "from database import engine; print(engine.execute('SELECT 1').scalar())"

# Increase connection pool
# In database.py: engine = create_engine(url, pool_size=20, max_overflow=40)
```

### Performance Testing
```bash
# Install testing tools
pip install locust httpx

# Basic load test
python -c "
import httpx
import asyncio
import time

async def test_endpoint():
    async with httpx.AsyncClient() as client:
        start = time.time()
        tasks = [client.get('http://localhost:8000/health') for _ in range(100)]
        responses = await asyncio.gather(*tasks)
        end = time.time()
        print(f'100 requests in {end-start:.2f}s')
        print(f'Success rate: {sum(1 for r in responses if r.status_code == 200)/100*100}%')

asyncio.run(test_endpoint())
"
```

## 📈 Scaling Strategies

### Horizontal Scaling
1. **Multiple instances**: Run multiple API instances behind load balancer
2. **Container orchestration**: Use Kubernetes or Docker Swarm
3. **Database scaling**: Read replicas, connection pooling
4. **Caching**: Redis for session storage and caching

### Vertical Scaling
1. **Increase workers**: More workers per instance
2. **Larger instances**: More CPU and memory
3. **SSD storage**: Faster disk I/O
4. **Network optimization**: Higher bandwidth

## 🔄 Deployment Pipeline

### CI/CD Integration
```yaml
# GitHub Actions example
name: Deploy API
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and deploy
        run: |
          docker build -t mychitfund-api .
          docker run -d -p 8000:8000 mychitfund-api
```

### Blue-Green Deployment
1. **Deploy new version** to green environment
2. **Health check** green environment
3. **Switch traffic** from blue to green
4. **Keep blue** as rollback option

This clustering setup provides a robust, scalable foundation for your MyChitFund API that can handle high concurrent loads while maintaining reliability and performance.