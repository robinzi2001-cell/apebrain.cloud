# 🚀 APEBRAIN.CLOUD - Komplette Deployment-Anleitung

## Inhaltsverzeichnis

1. [Voraussetzungen](#voraussetzungen)
2. [Server-Setup](#server-setup)
3. [DNS-Konfiguration](#dns-konfiguration)
4. [Automatisches Deployment](#automatisches-deployment)
5. [Manuelles Deployment](#manuelles-deployment)
6. [SSL-Konfiguration](#ssl-konfiguration)
7. [Verifizierung](#verifizierung)
8. [Post-Deployment](#post-deployment)

---

## Voraussetzungen

### Was Sie brauchen:

1. **Hostinger VPS** oder ähnlicher Server
   - OS: Ubuntu 24.04 LTS
   - RAM: Mindestens 2GB
   - Disk: Mindestens 20GB
   - Root-Zugriff via SSH

2. **Domain**
   - Registriert bei einem Domain-Provider
   - Zugriff auf DNS-Einstellungen

3. **GitHub Repository**
   - Ihr Code muss in einem GitHub-Repo liegen
   - Repository: `robinzi2001-cell/apebrain.cloud` (oder Ihr Repo)

4. **API Keys** (siehe README.md)
   - Gemini API Key
   - Pexels API Key
   - PayPal Credentials
   - Gmail App-Passwort
   - Google OAuth Credentials

---

## Server-Setup

### Schritt 1: SSH-Verbindung

```bash
ssh root@YOUR_SERVER_IP
```

Beispiel:
```bash
ssh root@72.61.177.155
```

Bei der ersten Verbindung:
- Fingerprint-Warnung: `yes` eingeben
- Passwort eingeben

### Schritt 2: System aktualisieren

```bash
apt update && apt upgrade -y
```

⏱️ Dauer: 2-5 Minuten

### Schritt 3: Grundlegende Tools installieren

```bash
apt install -y curl wget git ufw fail2ban htop vim nano
```

---

## DNS-Konfiguration

### Bei Ihrem Domain-Provider

Erstellen Sie folgende DNS-Records:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | YOUR_SERVER_IP | Auto |
| A | www | YOUR_SERVER_IP | Auto |

**Beispiel für apebrain.cloud:**
```
A    @      72.61.177.155    Auto
A    www    72.61.177.155    Auto
```

### DNS Propagation prüfen

⏱️ Wartezeit: 5-60 Minuten

```bash
# Von Ihrem lokalen Computer:
ping apebrain.cloud
nslookup apebrain.cloud
```

✅ Wenn die IP-Adresse Ihres Servers zurückgegeben wird → DNS funktioniert!

---

## Automatisches Deployment

### Option A: 1-Schritt-Installation (Empfohlen)

```bash
# Auf Ihrem Server:
cd ~
wget https://raw.githubusercontent.com/robinzi2001-cell/apebrain.cloud/main/setup-server.sh
chmod +x setup-server.sh
./setup-server.sh
```

**Das Script macht alles automatisch:**
- ✅ Installiert Node.js, Python, MongoDB, Nginx, PM2
- ✅ Konfiguriert Firewall
- ✅ Klont GitHub Repository
- ✅ Installiert Dependencies
- ✅ Baut Frontend
- ✅ Konfiguriert Nginx
- ✅ Startet Backend mit PM2
- ✅ Richtet SSL ein (fragt nach Domain)

⏱️ Gesamtdauer: 10-15 Minuten

### Option B: Schrittweise Installation

Folgen Sie der [Manuellen Deployment](#manuelles-deployment) Anleitung unten.

---

## Manuelles Deployment

### Schritt 1: Software installieren

#### Node.js & Yarn
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
npm install -g yarn
node --version  # Sollte v20.x anzeigen
```

#### Python 3.12
```bash
apt install -y python3 python3-pip python3-venv python3-dev build-essential
python3 --version  # Sollte 3.12.x anzeigen
```

#### MongoDB 7.0
```bash
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
  gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] \
  https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
  tee /etc/apt/sources.list.d/mongodb-org-7.0.list

apt update
apt install -y mongodb-org
systemctl start mongod
systemctl enable mongod
systemctl status mongod  # Sollte "active (running)" zeigen
```

#### Nginx
```bash
apt install -y nginx
systemctl status nginx  # Sollte "active (running)" zeigen
```

#### Certbot (SSL)
```bash
apt install -y certbot python3-certbot-nginx
```

#### PM2
```bash
npm install -g pm2
pm2 --version
```

### Schritt 2: Firewall konfigurieren

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
ufw status  # Status prüfen
```

### Schritt 3: Repository klonen

```bash
mkdir -p /var/www/apebrain
cd /var/www/apebrain
git clone https://github.com/robinzi2001-cell/apebrain.cloud.git .
```

### Schritt 4: Backend konfigurieren

```bash
cd /var/www/apebrain/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### .env Datei erstellen
```bash
nano .env
```

Inhalt (mit Ihren echten Werten):
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="apebrain_blog"
CORS_ORIGINS="https://apebrain.cloud,https://www.apebrain.cloud"
FRONTEND_URL="https://apebrain.cloud"
JWT_SECRET_KEY="GENERATE_WITH_openssl_rand_hex_32"

GEMINI_API_KEY="YOUR_GEMINI_KEY"
EMERGENT_LLM_KEY="YOUR_EMERGENT_KEY"
PEXELS_API_KEY="YOUR_PEXELS_KEY"

ADMIN_USERNAME="admin"
ADMIN_PASSWORD="YOUR_SECURE_PASSWORD"

PAYPAL_MODE="sandbox"
PAYPAL_CLIENT_ID="YOUR_PAYPAL_ID"
PAYPAL_CLIENT_SECRET="YOUR_PAYPAL_SECRET"

SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="YOUR_GMAIL_APP_PASSWORD"
NOTIFICATION_EMAIL="your-email@gmail.com"

GOOGLE_CLIENT_ID="YOUR_GOOGLE_CLIENT_ID"
GOOGLE_CLIENT_SECRET="YOUR_GOOGLE_SECRET"
```

Speichern: `CTRL+X`, dann `Y`, dann `Enter`

```bash
deactivate  # Virtual Environment verlassen
```

### Schritt 5: Frontend konfigurieren

```bash
cd /var/www/apebrain/frontend
yarn install
```

#### .env Datei erstellen
```bash
cat > .env << EOF
REACT_APP_BACKEND_URL=https://apebrain.cloud
EOF
```

#### Frontend bauen
```bash
yarn build
```

⏱️ Dauer: 3-5 Minuten

### Schritt 6: Nginx konfigurieren

```bash
nano /etc/nginx/sites-available/apebrain
```

Inhalt:
```nginx
server {
    listen 80;
    server_name apebrain.cloud www.apebrain.cloud;

    root /var/www/apebrain/frontend/build;
    index index.html;

    # React Router Support
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API Proxy
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
    }

    # Static Files Caching
    location /static {
        alias /var/www/apebrain/frontend/build/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Speichern: `CTRL+X`, dann `Y`, dann `Enter`

#### Site aktivieren
```bash
ln -sf /etc/nginx/sites-available/apebrain /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t  # Konfiguration testen
systemctl reload nginx
```

### Schritt 7: Backend mit PM2 starten

```bash
cd /var/www/apebrain/backend
```

#### PM2 Ecosystem File erstellen
```bash
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'apebrain-backend',
    script: 'venv/bin/uvicorn',
    args: 'server:app --host 0.0.0.0 --port 8001',
    cwd: '/var/www/apebrain/backend',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    }
  }]
};
EOF
```

#### Backend starten
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup systemd -u root --hp /root
```

---

## SSL-Konfiguration

### Let's Encrypt SSL (kostenlos)

```bash
certbot --nginx -d apebrain.cloud -d www.apebrain.cloud
```

**Folgen Sie den Prompts:**
1. Email-Adresse eingeben
2. Terms akzeptieren: `Y`
3. Email-Liste (optional): `N`
4. Redirect wählen: `2` (HTTPS Redirect)

✅ SSL wird automatisch konfiguriert und alle 90 Tage erneuert!

### Manuelle SSL-Erneuerung testen
```bash
certbot renew --dry-run
```

---

## Verifizierung

### 1. Services Status prüfen

```bash
# Backend
pm2 status
pm2 logs apebrain-backend

# Nginx
systemctl status nginx

# MongoDB
systemctl status mongod
```

Alle sollten "active (running)" zeigen.

### 2. Website testen

Öffnen Sie in Ihrem Browser:
- **https://apebrain.cloud**
- **https://www.apebrain.cloud**

✅ Sie sollten die Landing Page sehen!

### 3. API testen

```bash
# Auf dem Server:
curl https://apebrain.cloud/api/products
```

Sollte JSON mit Produkten zurückgeben.

### 4. Admin-Panel testen

1. Gehen Sie zu: `https://apebrain.cloud/admin`
2. Login mit:
   - Username: `admin`
   - Passwort: `[Ihr ADMIN_PASSWORD aus .env]`

✅ Sie sollten das Admin-Dashboard sehen!

---

## Post-Deployment

### Sicherheit härten

#### 1. SSH Key Authentication einrichten

**Auf Ihrem lokalen Computer:**
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
ssh-copy-id root@72.61.177.155
```

**Auf dem Server:**
```bash
nano /etc/ssh/sshd_config
```

Ändern:
```
PasswordAuthentication no
PermitRootLogin prohibit-password
```

```bash
systemctl restart sshd
```

#### 2. Fail2Ban konfigurieren

```bash
apt install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

### Monitoring einrichten

#### PM2 Web Dashboard (optional)
```bash
pm2 install pm2-server-monit
```

#### Uptime Monitoring (optional)
Verwenden Sie Services wie:
- UptimeRobot (kostenlos)
- Pingdom
- StatusCake

### Backups einrichten

#### MongoDB Backup Script
```bash
mkdir -p /backups/mongodb

cat > /root/backup-mongo.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mongodump --out /backups/mongodb/backup_$DATE
find /backups/mongodb -type d -mtime +7 -exec rm -rf {} +
EOF

chmod +x /root/backup-mongo.sh
```

#### Cronjob für tägliche Backups
```bash
crontab -e
```

Hinzufügen:
```
0 2 * * * /root/backup-mongo.sh
```

---

## Updates deployen

### Automatisch (empfohlen)

```bash
cd /var/www/apebrain
./update-app.sh
```

### Manuell

```bash
cd /var/www/apebrain
git pull origin main

# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
pm2 restart apebrain-backend

# Frontend
cd ../frontend
yarn install
yarn build
systemctl reload nginx
```

---

## Checkliste

### Pre-Deployment
- [ ] VPS mit Ubuntu 24.04 bereit
- [ ] Domain registriert
- [ ] DNS A-Records gesetzt
- [ ] GitHub Repo zugänglich
- [ ] Alle API Keys bereit

### Deployment
- [ ] Server-Software installiert
- [ ] Firewall konfiguriert
- [ ] Repository geklont
- [ ] Backend konfiguriert & .env erstellt
- [ ] Frontend gebaut
- [ ] Nginx konfiguriert
- [ ] PM2 Backend gestartet
- [ ] SSL installiert

### Post-Deployment
- [ ] Website erreichbar (HTTPS)
- [ ] Admin-Panel funktioniert
- [ ] API funktioniert
- [ ] SSH Keys eingerichtet
- [ ] Backups konfiguriert
- [ ] Monitoring eingerichtet

---

## Nützliche Befehle

### Services verwalten
```bash
pm2 restart apebrain-backend
pm2 logs apebrain-backend
pm2 monit

systemctl restart nginx
systemctl reload nginx
systemctl status nginx

systemctl restart mongod
systemctl status mongod
```

### Logs anzeigen
```bash
pm2 logs apebrain-backend --lines 100
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
tail -f /var/log/mongodb/mongod.log
```

### System-Ressourcen
```bash
htop
df -h
free -h
du -sh /var/www/apebrain
```

---

## Support

Bei Problemen:
1. Siehe [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
2. Logs überprüfen (siehe oben)
3. GitHub Issues: https://github.com/robinzi2001-cell/apebrain.cloud/issues

---

**Viel Erfolg mit Ihrem Deployment! 🚀🍄🧠**