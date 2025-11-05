# 🚀 APEBRAIN.CLOUD - Komplette Hostinger Server Setup Anleitung

## Server Details
- **IP:** 72.61.177.155
- **OS:** Ubuntu 24.04
- **Domain:** apebrain.cloud (oder Ihre Domain)

---

## 📋 SCHRITT-FÜR-SCHRITT ANLEITUNG

### SCHRITT 1: Code zu GitHub pushen

**In Emergent:**
1. Klicken Sie auf "Save to GitHub" Button
2. Wählen Sie Repository oder erstellen Sie ein neues
3. Notieren Sie sich: `GITHUB_USERNAME/REPO_NAME`

---

### SCHRITT 2: DNS Konfiguration

**Bei Ihrem Domain-Provider (z.B. Namecheap, GoDaddy, Cloudflare):**

Fügen Sie folgende DNS Records hinzu:

```
Type: A
Name: @
Value: 72.61.177.155
TTL: Automatic

Type: A
Name: www
Value: 72.61.177.155
TTL: Automatic
```

⏰ **DNS Propagation dauert 5-60 Minuten**

Testen mit: `ping apebrain.cloud`

---

### SCHRITT 3: SSH Verbindung zum Server

```bash
ssh root@72.61.177.155
```

Bei erster Verbindung: `yes` eingeben für Fingerprint

---

### SCHRITT 4: Server Basis-Setup

```bash
# 1. Setup-Script herunterladen
wget https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/HOSTINGER_SERVER_SETUP.sh

# Oder manuell erstellen:
nano server-setup.sh
# Kopieren Sie den Inhalt von HOSTINGER_SERVER_SETUP.sh hier rein
# CTRL+X, dann Y, dann Enter zum Speichern

# 2. Ausführbar machen
chmod +x server-setup.sh

# 3. Ausführen (dauert ca. 10-15 Minuten)
./server-setup.sh
```

**Was wird installiert:**
- ✅ Node.js 20.x + Yarn
- ✅ Python 3.12 + pip
- ✅ MongoDB 7.0
- ✅ Nginx
- ✅ Certbot (SSL)
- ✅ PM2 (Process Manager)
- ✅ Firewall (UFW)

---

### SCHRITT 5: Deployment Script vorbereiten

```bash
# 1. Deployment-Script erstellen
cd /var/www/apebrain
nano deploy.sh

# Kopieren Sie den Inhalt von HOSTINGER_DEPLOY.sh hier rein

# 2. ⚠️ WICHTIG: Bearbeiten Sie folgende Zeilen:
# Zeile 13: GITHUB_REPO="IHR_GITHUB_USERNAME/IHR_REPO_NAME"
# Zeile 14: DOMAIN="apebrain.cloud"  # Ihre Domain!

# 3. Ausführbar machen
chmod +x deploy.sh
```

---

### SCHRITT 6: Anwendung deployen

```bash
# Script ausführen
./deploy.sh
```

**Das Script wird:**
- ✅ GitHub Repository klonen
- ✅ Backend Dependencies installieren
- ✅ Frontend bauen
- ✅ Nginx konfigurieren
- ✅ PM2 Backend-Process starten

---

### SCHRITT 7: API Keys konfigurieren

```bash
# Backend .env bearbeiten
nano /var/www/apebrain/backend/.env

# Fügen Sie Ihre echten API Keys ein:
# - GEMINI_API_KEY
# - EMERGENT_LLM_KEY
# - PEXELS_API_KEY
# - PAYPAL_CLIENT_ID & SECRET
# - SMTP (Gmail) Credentials
# - GOOGLE_CLIENT_ID & SECRET
```

Speichern: `CTRL+X`, dann `Y`, dann `Enter`

---

### SCHRITT 8: SSL Zertifikat installieren

```bash
# Let's Encrypt SSL (kostenlos)
certbot --nginx -d apebrain.cloud -d www.apebrain.cloud

# Folgen Sie den Anweisungen:
# 1. Email eingeben
# 2. Terms akzeptieren (Y)
# 3. Redirect wählen (2 = HTTPS redirect)
```

✅ **Auto-Renewal wird automatisch eingerichtet**

---

### SCHRITT 9: Services starten

```bash
# Backend neu starten
pm2 restart apebrain-backend

# Nginx neu laden
systemctl reload nginx

# Status prüfen
pm2 status
systemctl status nginx
systemctl status mongod
```

---

### SCHRITT 10: Testen!

Öffnen Sie in Ihrem Browser:
```
https://apebrain.cloud
```

---

## 🔧 NÜTZLICHE BEFEHLE

### Server Management
```bash
# Services prüfen
pm2 status                    # Backend status
systemctl status nginx        # Nginx status
systemctl status mongod       # MongoDB status

# Logs anzeigen
pm2 logs apebrain-backend     # Backend logs
tail -f /var/log/nginx/error.log  # Nginx errors

# Services neu starten
pm2 restart apebrain-backend
systemctl restart nginx
systemctl restart mongod
```

### Updates deployen
```bash
cd /var/www/apebrain
git pull origin main          # Code aktualisieren

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

### MongoDB Management
```bash
# MongoDB Shell öffnen
mongosh

# Datenbank wechseln
use apebrain_blog

# Collections anzeigen
show collections

# Alle Blogs anzeigen
db.blogs.find().pretty()
```

---

## 🔒 SICHERHEIT

### Firewall Status
```bash
ufw status
```

Sollte zeigen:
- ✅ 22/tcp (SSH) - ALLOW
- ✅ 80/tcp (HTTP) - ALLOW
- ✅ 443/tcp (HTTPS) - ALLOW

### SSH Key Authentication (empfohlen)

Auf Ihrem **lokalen Computer**:
```bash
# SSH Key generieren
ssh-keygen -t ed25519 -C "your_email@example.com"

# Key zum Server kopieren
ssh-copy-id root@72.61.177.155
```

Auf dem **Server**:
```bash
# Password Authentication deaktivieren (nach SSH Key Setup!)
nano /etc/ssh/sshd_config

# Ändern Sie:
# PasswordAuthentication no

# SSH neu starten
systemctl restart sshd
```

---

## 🆘 TROUBLESHOOTING

### Problem: Website nicht erreichbar

```bash
# DNS prüfen
ping apebrain.cloud

# Nginx Status
systemctl status nginx
nginx -t  # Config testen

# Backend Status
pm2 status
pm2 logs apebrain-backend
```

### Problem: Backend startet nicht

```bash
# Logs prüfen
pm2 logs apebrain-backend

# Manuell testen
cd /var/www/apebrain/backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001
```

### Problem: SSL Fehler

```bash
# Certbot Status
certbot certificates

# Erneut versuchen
certbot --nginx -d apebrain.cloud -d www.apebrain.cloud --force-renewal
```

### Problem: MongoDB Connection Error

```bash
# MongoDB Status prüfen
systemctl status mongod

# MongoDB starten
systemctl start mongod
systemctl enable mongod

# MongoDB Logs
tail -f /var/log/mongodb/mongod.log
```

---

## 📊 MONITORING

### Server Ressourcen
```bash
htop                    # CPU, RAM, Processes
df -h                   # Disk space
free -h                 # Memory usage
```

### Nginx Access Logs
```bash
tail -f /var/log/nginx/access.log
```

### PM2 Monitoring
```bash
pm2 monit              # Live monitoring
```

---

## 🔄 AUTO-DEPLOYMENT (Optional)

### GitHub Webhook Setup

1. **Auf dem Server:**
```bash
# Webhook listener installieren
npm install -g webhook

# Webhook Script erstellen
nano /var/www/webhook.js
```

2. **Webhook Script:**
```javascript
const http = require('http');
const { exec } = require('child_process');

http.createServer((req, res) => {
  if (req.method === 'POST') {
    exec('cd /var/www/apebrain && ./deploy.sh', (error, stdout, stderr) => {
      console.log(stdout);
      if (error) console.error(error);
    });
  }
  res.writeHead(200);
  res.end('OK');
}).listen(9000);
```

3. **In GitHub:**
   - Settings → Webhooks → Add webhook
   - URL: `http://72.61.177.155:9000`
   - Content type: `application/json`
   - Events: Push events

---

## 📝 ZUSAMMENFASSUNG DER BEFEHLE

**Komplette Installation in einer Session:**
```bash
# 1. SSH Verbinden
ssh root@72.61.177.155

# 2. Server Setup (einmalig)
wget -O setup.sh https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/HOSTINGER_SERVER_SETUP.sh
chmod +x setup.sh
./setup.sh

# 3. Deployment
cd /var/www/apebrain
wget -O deploy.sh https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/HOSTINGER_DEPLOY.sh
# EDIT: nano deploy.sh (GitHub Repo & Domain ändern)
chmod +x deploy.sh
./deploy.sh

# 4. API Keys konfigurieren
nano /var/www/apebrain/backend/.env

# 5. SSL installieren
certbot --nginx -d apebrain.cloud -d www.apebrain.cloud

# 6. Services starten
pm2 restart all
systemctl reload nginx

# ✅ FERTIG!
```

---

## 🎉 ERFOLG!

Ihre APEBRAIN.CLOUD Seite sollte jetzt live sein unter:
- **https://apebrain.cloud**
- **https://www.apebrain.cloud**

Bei Fragen oder Problemen, überprüfen Sie die Logs:
- Backend: `pm2 logs apebrain-backend`
- Nginx: `tail -f /var/log/nginx/error.log`
- MongoDB: `tail -f /var/log/mongodb/mongod.log`

---

**Viel Erfolg! 🚀🍄🧠**
