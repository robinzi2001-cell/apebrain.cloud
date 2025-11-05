# 🛠️ Known Issues & Fixes

Dokumentation der häufigsten Probleme und Lösungen beim Deployment.

---

## 🔴 Problem 1: Backend startet nicht - "SyntaxError: Unexpected identifier 'uvicorn'"

### Symptom:
```
PM2 Status: errored
Logs: SyntaxError: Unexpected identifier 'uvicorn'
```

### Ursache:
PM2 versucht Python-Code als Node.js zu interpretieren (falsche `ecosystem.config.js`).

### Lösung:
```bash
cd /var/www/apebrain/backend

cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'apebrain-backend',
    script: './venv/bin/python',
    args: '-m uvicorn server:app --host 0.0.0.0 --port 8001 --workers 2',
    cwd: '/var/www/apebrain/backend',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      PYTHONUNBUFFERED: '1'
    },
    error_file: '/var/log/apebrain-backend-error.log',
    out_file: '/var/log/apebrain-backend-out.log',
    log_file: '/var/log/apebrain-backend-combined.log',
    time: true
  }]
};
EOF

pm2 restart apebrain-backend
```

**Fix ist bereits im ULTIMATE-SETUP.sh enthalten!** ✅

---

## 🔴 Problem 2: PayPal Config Error - "Configuration Mode Invalid"

### Symptom:
```
InvalidConfig: ('Configuration Mode Invalid', 'Received: "sandbox"', 'Required: live or sandbox')
```

### Ursache:
Anführungszeichen in `.env` Datei werden mitgelesen: `PAYPAL_MODE="live"` → wird zu `"live"` statt `live`

### Lösung:
**Alle Werte in `.env` OHNE Anführungszeichen schreiben!**

```env
# ❌ FALSCH:
PAYPAL_MODE="live"
ADMIN_PASSWORD="test123"

# ✅ RICHTIG:
PAYPAL_MODE=live
ADMIN_PASSWORD=test123
```

**Komplett korrigierte .env:**
```bash
nano /var/www/apebrain/backend/.env
```

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=apebrain_blog
CORS_ORIGINS=*
JWT_SECRET_KEY=your-secret-key
FRONTEND_URL=https://yourdomain.com

ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-password

GEMINI_API_KEY=AIzaSy...
PEXELS_API_KEY=yXxO4WF...

PAYPAL_MODE=live
PAYPAL_CLIENT_ID=AWjyyJV...
PAYPAL_CLIENT_SECRET=EFD-znj...

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
NOTIFICATION_EMAIL=your-email@gmail.com

GOOGLE_CLIENT_ID=843038928917-...apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...
```

Dann Backend neu starten:
```bash
pm2 restart apebrain-backend
```

**Fix ist in .env.example und README dokumentiert!** ✅

---

## 🔴 Problem 3: Frontend zeigt 404 - Nginx lädt nicht

### Symptom:
```
curl http://localhost
HTTP/1.1 404 Not Found
```

Frontend-Build existiert aber Nginx liefert 404.

### Ursache:
Fehlende `listen` Directive in Nginx-Config.

### Lösung:
```bash
cat > /etc/nginx/sites-available/apebrain << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name apebrain.cloud www.apebrain.cloud;

    root /var/www/apebrain/frontend/build;
    index index.html;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;

    # React Router
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Static Files
    location /static {
        alias /var/www/apebrain/frontend/build/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    access_log /var/log/nginx/apebrain-access.log;
    error_log /var/log/nginx/apebrain-error.log;
}
EOF

# Test & Reload
nginx -t
systemctl reload nginx
```

**Fix ist bereits im ULTIMATE-SETUP.sh enthalten!** ✅

---

## 🔴 Problem 4: emergentintegrations Installation schlägt fehl

### Symptom:
```
ERROR: Could not find a version that satisfies the requirement emergentintegrations==0.1.0
```

### Ursache:
Package benötigt speziellen PyPI Index.

### Lösung:
```bash
cd /var/www/apebrain/backend
source venv/bin/activate
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
pip install -r requirements.txt
deactivate
```

**Fix ist bereits im ULTIMATE-SETUP.sh enthalten!** ✅

---

## 🔴 Problem 5: Frontend Build fehlt nach Installation

### Symptom:
```
ls /var/www/apebrain/frontend/build
No such file or directory
```

### Lösung:
```bash
cd /var/www/apebrain/frontend
yarn install
yarn build
systemctl reload nginx
```

---

## 🔴 Problem 6: MongoDB verbindet nicht

### Symptom:
```
Backend Logs: Connection refused mongodb://localhost:27017
```

### Lösung:
```bash
# MongoDB Status
systemctl status mongod

# Falls nicht läuft:
systemctl start mongod
systemctl enable mongod

# Backend neu starten
pm2 restart apebrain-backend
```

---

## 🔴 Problem 7: Port 8001 bereits belegt

### Symptom:
```
ERROR: Address already in use
```

### Lösung:
```bash
# Prozess finden
lsof -i :8001

# Prozess beenden (PID ersetzen!)
kill -9 PID

# PM2 neu starten
pm2 restart apebrain-backend
```

---

## 🔴 Problem 8: SSL-Zertifikat schlägt fehl

### Symptom:
```
certbot: DNS resolution failed
```

### Ursache:
DNS zeigt noch nicht auf Server-IP.

### Lösung:
```bash
# DNS prüfen
ping apebrain.cloud

# Falls falsch: DNS-Provider prüfen und A-Records korrigieren
# Warte 5-60 Minuten für DNS-Propagation

# Danach erneut versuchen:
certbot --nginx -d apebrain.cloud -d www.apebrain.cloud
```

---

## ✅ Schnelle Diagnose-Befehle

```bash
# Health Check
/root/apebrain-health.sh

# Debug Info
/root/apebrain-debug.sh

# Backend Logs
pm2 logs apebrain-backend --lines 50

# Nginx Logs
tail -50 /var/log/nginx/apebrain-error.log

# MongoDB Logs
journalctl -xeu mongod --no-pager | tail -50

# Alle Services Status
systemctl status mongod nginx
pm2 status
```

---

## 📞 Support

Bei persistenten Problemen:
1. Logs sammeln: `/root/apebrain-debug.sh > debug-output.txt`
2. Problem dokumentieren
3. Setup-Log prüfen: `cat /root/apebrain-setup.log`

---

**🍄🧠 Stand: November 2025**
