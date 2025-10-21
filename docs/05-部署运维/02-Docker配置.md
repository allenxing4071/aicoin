# Docker配置

**文档编号**: AICOIN-OPS-002  
**文档版本**: v1.0.0  
**创建日期**: 2025-10-22

---

## 1. docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: aicoin-postgres
    environment:
      POSTGRES_DB: aicoin
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: aicoin-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  backend:
    build: ./backend
    container_name: aicoin-backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD}@postgres:5432/aicoin
      REDIS_URL: redis://redis:6379
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
      HYPERLIQUID_API_KEY: ${HYPERLIQUID_API_KEY}
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    restart: unless-stopped

  celery_worker:
    build: ./backend
    container_name: aicoin-celery-worker
    command: celery -A app.core.celery_app worker -l info
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD}@postgres:5432/aicoin
      REDIS_URL: redis://redis:6379
    depends_on:
      - redis
      - postgres
    restart: unless-stopped

  celery_beat:
    build: ./backend
    container_name: aicoin-celery-beat
    command: celery -A app.core.celery_app beat -l info
    environment:
      REDIS_URL: redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: aicoin-frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

---

## 2. backend/Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 3. frontend/Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

CMD ["npm", "start"]
```

---

## 4. 常用命令

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 重启服务
docker-compose restart backend

# 停止所有服务
docker-compose down

# 清理卷
docker-compose down -v
```

---

**文档结束**

