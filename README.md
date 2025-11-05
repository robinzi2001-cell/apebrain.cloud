# 🍄🧠 APEBRAIN.CLOUD

**Stoned Ape Theory Blog & E-Commerce Platform**

Eine Full-Stack Webanwendung mit AI-gestützter Content-Generierung, integriertem E-Commerce-Shop und Admin-Panel. Optimiert für Ubuntu 24.04 Server (Hostinger VPS).

---

## ✨ Features

### 🎨 Frontend
- **Dark Mystical Design** - Stoned Ape Theory Theme mit Fliegenpilz-Rot Akzenten
- **Landing Page** - 🍄 + 🧠 Icon, Terence McKenna Zitate, Stoned Ape Theory Erklärung
- **Blog System** - Knowledge Portal mit 6 Kategorien, Newsletter-Integration
- **E-Commerce Shop** - Sacred Shop mit PayPal-Integration, Warenkorb, Bestellverwaltung
- **Responsive Design** - React 19 + Tailwind CSS + Shadcn UI

### 🔧 Backend
- **FastAPI** - Moderne Python API mit automatischer OpenAPI-Dokumentation
- **MongoDB** - NoSQL-Datenbank für flexible Datenspeicherung
- **AI Blog-Generierung** - Gemini AI für automatische Content-Erstellung
- **Pexels Integration** - Automatische Bildsuche für Blog-Posts
- **PayPal LIVE Integration** - Sichere Zahlungsabwicklung
- **Email-System** - Gmail SMTP für Benachrichtigungen
- **Google OAuth** - Social Login für Kunden

### 👤 Admin Panel
- Blog-Post Management (Erstellen, Bearbeiten, Löschen)
- Produkt-Verwaltung
- Coupon-System
- Bestellverwaltung
- AI-gestützte Content-Generierung

### 🔐 Authentifizierung
- Admin Login (Email/Password)
- Kunden-Accounts (Email/Password + Google OAuth)
- JWT-basierte Authentifizierung

---

## 🚀 Schnellstart-Deployment (Ubuntu 24.04)

### Voraussetzungen

1. **Ubuntu 24.04 Server** (z.B. Hostinger VPS)
2. **Root-Zugriff** via SSH
3. **Domain konfiguriert** mit DNS A-Records:
   ```
   A-Record: yourdomain.com → SERVER-IP
   A-Record: www.yourdomain.com → SERVER-IP
   ```
4. **API Keys bereit** (siehe unten)

---

### 🎯 One-Command Installation

```bash
# 1. SSH Login auf deinen Server
ssh root@DEINE-SERVER-IP

# 2. Setup-Script herunterladen
wget https://raw.githubusercontent.com/robinzi2001-cell/apebrain.cloud/main/ULTIMATE-SETUP.sh

# 3. Script bearbeiten (Domain anpassen)
nano ULTIMATE-SETUP.sh
# Ändere: DOMAIN="apebrain.cloud" → DOMAIN="deine-domain.com"

# 4. Ausführbar machen
chmod +x ULTIMATE-SETUP.sh

# 5. Installation starten (dauert 15-20 Min)
./ULTIMATE-SETUP.sh
```

**Das Script installiert automatisch:**
- ✅ System-Updates & Firewall
- ✅ Node.js 20, Python 3.12, MongoDB 7.0, Nginx
- ✅ GitHub Repository klonen
- ✅ Backend & Frontend Dependencies
- ✅ PM2 Backend-Server
- ✅ Nginx Reverse Proxy
- ✅ SSL-Zertifikat (optional)
- ✅ Management-Scripts

---

## 🔑 API Keys Konfiguration

### Benötigte API Keys beschaffen

1. **Gemini AI** (Blog-Generierung)
   - 🔗 https://makersuite.google.com/app/apikey
   - ✅ Kostenlos verfügbar

2. **Pexels API** (Bilder)
   - 🔗 https://www.pexels.com/api/
   - ✅ Kostenlos verfügbar

3. **PayPal** (Zahlungen)
   - 🔗 https://developer.paypal.com/
   - Sandbox (Test) & Live Credentials

4. **Gmail App Password** (Email-Versand)
   - 🔗 https://myaccount.google.com/apppasswords
   - ⚠️ **Nicht** normales Gmail-Passwort! App-spezifisches Passwort erstellen!

5. **Google OAuth** (Social Login)
   - 🔗 https://console.cloud.google.com/apis/credentials
   - OAuth 2.0 Client ID erstellen
   - Authorized redirect URI: `https://yourdomain.com/auth/google/callback`

---

### .env Datei erstellen

**Nach der Installation wird das Setup-Script dich automatisch fragen, ob du die .env Datei konfigurieren möchtest.**

**Option A - Interaktiv während Installation:**
Das Script öffnet automatisch den Editor nach der Installation.

**Option B - Manuell später:**
```bash
# Vorlage kopieren
cp /var/www/apebrain/backend/.env.example /var/www/apebrain/backend/.env

# Bearbeiten
nano /var/www/apebrain/backend/.env
```

---

### 📄 .env Beispiel-Datei

```env
# ============================================
# DATABASE
# ============================================
MONGO_URL="mongodb://localhost:27017"
DB_NAME="apebrain_blog"

# ============================================
# SECURITY & CORS
# ============================================
JWT_SECRET_KEY="your-random-secret-key-here"
FRONTEND_URL="https://yourdomain.com"
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"

# ============================================
# ADMIN ACCOUNT (ÄNDERN!)
# ============================================
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="your-secure-password-123"

# ============================================
# AI INTEGRATION
# ============================================
GEMINI_API_KEY="AIzaSy..."
EMERGENT_LLM_KEY="sk-emergent-..."  # Optional

# ============================================
# IMAGE API
# ============================================
PEXELS_API_KEY="yXxO4WF..."

# ============================================
# PAYMENT PROCESSING
# ============================================
PAYPAL_MODE="live"  # oder "sandbox" für Tests
PAYPAL_CLIENT_ID="AWjyyJV..."
PAYPAL_CLIENT_SECRET="EFD-znj..."

# ============================================
# EMAIL CONFIGURATION
# ============================================
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="xxxx xxxx xxxx xxxx"  # Gmail App Password!
NOTIFICATION_EMAIL="your-email@gmail.com"

# ============================================
# GOOGLE OAUTH
# ============================================
GOOGLE_CLIENT_ID="843038928917-....apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="GOCSPX-..."
```

**Speichern:** `Strg+X` → `Y` → `Enter`

---

### Backend starten

```bash
# Nach .env Konfiguration:
cd /var/www/apebrain/backend
pm2 start ecosystem.config.js
pm2 save

# Status prüfen
pm2 status

# Logs ansehen
pm2 logs apebrain-backend
```

---

## 🔧 Management & Wartung

### Nützliche Befehle

```bash
# System-Status prüfen
/root/apebrain-health.sh

# Ausführliche Debug-Info
/root/apebrain-debug.sh

# Backend Logs live ansehen
pm2 logs apebrain-backend

# Backend neu starten
pm2 restart apebrain-backend

# Nginx neu laden
systemctl reload nginx

# MongoDB Status
systemctl status mongod

# App Updates von GitHub
/root/apebrain-update.sh
```

### SSL-Zertifikat manuell einrichten

```bash
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Logs durchsuchen

```bash
# Backend Logs
tail -f /var/log/apebrain-backend-error.log

# Nginx Logs
tail -f /var/log/nginx/apebrain-error.log

# MongoDB Logs
journalctl -xeu mongod

# PM2 Logs
pm2 logs --lines 50
```

---

## 🌐 Zugriff

### Website
- **Frontend**: `https://yourdomain.com`
- **Admin-Panel**: `https://yourdomain.com/shroomsadmin`
- **API Docs**: `https://yourdomain.com/api/docs`

### Standard-Login
- **Admin Username**: `admin`
- **Admin Password**: (in `.env` festgelegt)

---

## 📁 Projekt-Struktur

```
apebrain.cloud/
├── backend/
│   ├── server.py              # Haupt-API (FastAPI)
│   ├── auth_endpoints.py      # Kunden-Authentifizierung
│   ├── requirements.txt       # Python Dependencies
│   ├── .env                   # Environment Variables (API Keys)
│   └── ecosystem.config.js    # PM2 Konfiguration
├── frontend/
│   ├── src/
│   │   ├── App.js            # Haupt-Komponente
│   │   ├── pages/            # Seiten (Landing, Blog, Shop)
│   │   └── components/       # Wiederverwendbare Komponenten
│   ├── package.json          # Node Dependencies
│   └── .env                  # Backend URL
├── ULTIMATE-SETUP.sh         # One-Command Installation
├── README.md                 # Diese Datei
└── DEPLOYMENT.md             # Detaillierte Deployment-Anleitung
```

---

## 🛠️ Technologie-Stack

### Frontend
- **React 19** - UI Library
- **Tailwind CSS** - Utility-First CSS
- **Shadcn UI** - Component Library
- **React Router** - Navigation
- **Axios** - HTTP Client
- **Sonner** - Toast Notifications

### Backend
- **FastAPI** - Python Web Framework
- **Motor** - Async MongoDB Driver
- **PyMongo** - MongoDB Integration
- **Pydantic** - Data Validation
- **Python-Jose** - JWT Authentication
- **Bcrypt** - Password Hashing
- **Google Generative AI** - AI Content Generation
- **PayPal REST SDK** - Payment Processing
- **Aiosmtplib** - Async Email Sending

### Infrastructure
- **Ubuntu 24.04** - Server OS
- **Nginx** - Reverse Proxy & Static Files
- **PM2** - Process Manager (Backend)
- **MongoDB 7.0** - Database
- **Certbot** - SSL/TLS Certificates
- **UFW** - Firewall

---

## 🐛 Troubleshooting

### Backend startet nicht

```bash
# Logs prüfen
pm2 logs apebrain-backend --lines 50

# .env Datei prüfen
cat /var/www/apebrain/backend/.env

# Virtual Environment prüfen
cd /var/www/apebrain/backend
source venv/bin/activate
python --version
pip list
```

### Frontend zeigt 502 Bad Gateway

```bash
# Backend Status prüfen
pm2 status

# Backend neu starten
pm2 restart apebrain-backend

# Nginx Logs prüfen
tail -f /var/log/nginx/apebrain-error.log
```

### MongoDB verbindet nicht

```bash
# MongoDB Status
systemctl status mongod

# MongoDB neu starten
systemctl restart mongod

# MongoDB Logs
journalctl -xeu mongod
```

### SSL-Zertifikat Fehler

```bash
# DNS prüfen
ping yourdomain.com

# Certbot erneut ausführen
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Certbot Logs
journalctl -xeu certbot
```

### Port 8001 bereits belegt

```bash
# Prozess finden
lsof -i :8001

# Prozess beenden
kill -9 PID

# PM2 neu starten
pm2 restart apebrain-backend
```

---

## 🔄 Updates & Maintenance

### App von GitHub aktualisieren

```bash
/root/apebrain-update.sh
```

**Oder manuell:**
```bash
cd /var/www/apebrain
git pull origin main

# Backend aktualisieren
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
pm2 restart apebrain-backend

# Frontend aktualisieren
cd ../frontend
yarn install
yarn build
systemctl reload nginx
```

### Datenbank-Backup

```bash
# Backup erstellen
mongodump --db apebrain_blog --out /root/backups/$(date +%Y%m%d)

# Backup wiederherstellen
mongorestore --db apebrain_blog /root/backups/DATUM/apebrain_blog
```

---

## 📚 Weitere Dokumentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Detaillierte Deployment-Anleitung
- **[API Docs](https://yourdomain.com/api/docs)** - Automatische FastAPI Dokumentation
- **Frontend Components** - Siehe `/frontend/src/components/`

---

## 🤝 Support

Bei Problemen:
1. Logs prüfen: `/root/apebrain-debug.sh`
2. Health Check: `/root/apebrain-health.sh`
3. Setup Log: `cat /root/apebrain-setup.log`

---

## 📄 Lizenz

Privates Projekt - Alle Rechte vorbehalten.

---

**🍄🧠 Built with Love & Consciousness Expansion**
