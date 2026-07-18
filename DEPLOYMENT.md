# Deployment Guide - ONE FOR ALL

This guide covers deployment of the ONE FOR ALL application to various platforms.

## Pre-Deployment Checklist

- [ ] Update `SECRET_KEY` in `.env` with a strong, random value
- [ ] Ensure all API keys are set in `.env` (GOOGLE_API_KEY, GOOGLE_AI_API_KEY)
- [ ] Test the application locally with `FLASK_ENV=production`
- [ ] Verify all database migrations are complete
- [ ] Review security settings in `config.py`
- [ ] Ensure `.env` is not committed to version control (check `.gitignore`)
- [ ] Update logs directory permissions if deploying to shared hosting

## Local Development

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=development
# or on Windows:
set FLASK_ENV=development

# Run development server
python app.py
```

## Production Deployment

### Using Gunicorn (Recommended)

1. **Install production dependencies:**
   ```bash
   pip install gunicorn
   ```

2. **Create a `.env` file in production:**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

3. **Run with Gunicorn:**
   ```bash
   export FLASK_ENV=production
   gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
   ```
   
   - `-w 4`: Number of worker processes (adjust based on CPU cores)
   - `-b 0.0.0.0:8000`: Bind to all interfaces on port 8000
   - `wsgi:app`: WSGI module and application object

### Using Systemd Service (Linux)

1. **Create a systemd service file** at `/etc/systemd/system/oneforall.service`:
   ```ini
   [Unit]
   Description=ONE FOR ALL Flask Application
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/ONE FOR ALL
   Environment="FLASK_ENV=production"
   Environment="FLASK_HOST=127.0.0.1"
   Environment="FLASK_PORT=8000"
   ExecStart=/path/to/ONE FOR ALL/.venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 wsgi:app

   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and start the service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable oneforall
   sudo systemctl start oneforall
   sudo systemctl status oneforall
   ```

### Using Nginx as Reverse Proxy

**Create an Nginx configuration** at `/etc/nginx/sites-available/oneforall`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/ONE FOR ALL/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/oneforall /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Using Docker

**Create a Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production
ENV FLASK_HOST=0.0.0.0

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "wsgi:app"]
```

**Build and run:**
```bash
docker build -t oneforall .
docker run -p 8000:8000 --env-file .env oneforall
```

### Deploying to Heroku

1. **Install Heroku CLI** from https://devcenter.heroku.com/articles/heroku-cli

2. **Login and create an app:**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secure-key
   heroku config:set GOOGLE_API_KEY=your-key
   heroku config:set GOOGLE_AI_API_KEY=your-key
   ```

4. **Deploy:**
   ```bash
   git push heroku main
   ```

### Deploying to PythonAnywhere

1. Upload your code to PythonAnywhere
2. Create a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Configure a WSGI file pointing to `wsgi:app`
5. Set environment variables in the web app settings
6. Reload the web app

## Database Migrations

For SQLite (current setup), the database is automatically created on first run.

If migrating to PostgreSQL/MySQL in the future:
1. Update `config.py` with the new DATABASE_URL
2. Use Alembic for migrations: `pip install alembic`
3. Initialize: `alembic init migrations`
4. Create migration: `alembic revision --autogenerate -m "description"`
5. Apply: `alembic upgrade head`

## SSL/HTTPS Setup

### Using Let's Encrypt with Nginx

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Update Nginx to redirect HTTP to HTTPS

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # ... rest of your Nginx config
}
```

## Monitoring and Logging

1. **Check logs:**
   ```bash
   tail -f logs/app.log
   ```

2. **Monitor Gunicorn workers:**
   ```bash
   ps aux | grep gunicorn
   ```

3. **Set up log rotation** using logrotate:
   ```
   /path/to/ONE FOR ALL/logs/app.log {
       daily
       rotate 14
       compress
       delaycompress
       notifempty
       create 0640 www-data www-data
       sharedscripts
   }
   ```

## Performance Optimization

1. **Enable gzip compression** in Nginx:
   ```nginx
   gzip on;
   gzip_types text/css application/javascript text/plain;
   gzip_min_length 1000;
   ```

2. **Enable caching** for static files (configured in Nginx config above)

3. **Adjust worker processes** based on CPU cores:
   ```bash
   # For an 8-core CPU, use 8 workers
   gunicorn -w 8 wsgi:app
   ```

4. **Use connection pooling** for databases (if applicable)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check if Gunicorn is running: `systemctl status oneforall` |
| Database locked | Ensure only one process accesses SQLite at a time |
| High memory usage | Reduce worker count or add more memory |
| Slow responses | Check logs, optimize database queries, enable caching |
| Static files not loading | Verify paths in Nginx config, ensure correct permissions |

## Security Best Practices

1. ✅ Use strong SECRET_KEY (minimum 32 characters)
2. ✅ Always use HTTPS in production
3. ✅ Keep dependencies updated: `pip list --outdated`
4. ✅ Run as non-root user (e.g., www-data)
5. ✅ Restrict file permissions on sensitive files
6. ✅ Use environment variables for secrets, never commit .env
7. ✅ Enable security headers (already configured in `app.py`)
8. ✅ Regular backups of SQLite database

## Support and Documentation

- Flask Documentation: https://flask.palletsprojects.com/
- Gunicorn Documentation: https://gunicorn.org/
- Nginx Documentation: https://nginx.org/en/docs/
