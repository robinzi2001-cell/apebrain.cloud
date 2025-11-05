# 🔧 APEBRAIN.CLOUD - Troubleshooting Guide

## Inhaltsverzeichnis

1. [Website nicht erreichbar](#website-nicht-erreichbar)
2. [Backend startet nicht](#backend-startet-nicht)
3. [Frontend zeigt Fehler](#frontend-zeigt-fehler)
4. [MongoDB Probleme](#mongodb-probleme)
5. [SSL/HTTPS Probleme](#sslhttps-probleme)
6. [PayPal Integration Fehler](#paypal-integration-fehler)
7. [Email-Benachrichtigungen funktionieren nicht](#email-benachrichtigungen-funktionieren-nicht)
8. [Performance-Probleme](#performance-probleme)

---

## Website nicht erreichbar

### Symptom
- Browser zeigt "Diese Website ist nicht erreichbar"
- Timeout beim Laden

### Diagnose

```bash
# 1. DNS prüfen (von lokalem Computer)
ping apebrain.cloud
nslookup apebrain.cloud

# 2. Server erreichbar?
ping YOUR_SERVER_IP

# 3. Nginx läuft?
systemctl status nginx

# 4. Firewall prüfen
ufw status
```

### Lösungen

#### DNS-Probleme
```bash
# DNS Records beim Provider prüfen:
# A Record @ -> Server-IP
# A Record www -> Server-IP

# DNS Propagation kann bis zu 48h dauern
# Schneller Test mit:
dig apebrain.cloud
```

#### Nginx startet nicht
```bash
# Konfiguration testen
nginx -t

# Fehler in Config?
nano /etc/nginx/sites-available/apebrain

# Neu starten
systemctl restart nginx

# Logs prüfen
tail -50 /var/log/nginx/error.log
```

#### Firewall blockiert
```bash
# Ports öffnen
ufw allow 80/tcp
ufw allow 443/tcp
ufw reload
```

---

## Backend startet nicht

### Symptom
- API-Calls schlagen fehl
- Frontend kann keine Daten laden
- pm2 status zeigt "errored" oder "stopped"

### Diagnose

```bash
# PM2 Status
pm2 status

# Backend Logs
pm2 logs apebrain-backend --lines 100

# Manueller Start-Test
cd /var/www/apebrain/backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001
```

### Häufige Fehler & Lösungen

#### ModuleNotFoundError
```bash
# Dependencies neu installieren
cd /var/www/apebrain/backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
pm2 restart apebrain-backend
```

#### MongoDB Connection Error
```bash
# MongoDB Status prüfen
systemctl status mongod

# Falls gestoppt:
systemctl start mongod
systemctl enable mongod

# Logs prüfen
tail -50 /var/log/mongodb/mongod.log
```

#### .env Datei fehlt oder falsch
```bash
# .env prüfen
cat /var/www/apebrain/backend/.env

# Muss enthalten:
# - MONGO_URL
# - Alle API Keys
# - Admin Credentials

# Nach Änderungen:
pm2 restart apebrain-backend
```

#### Port 8001 bereits belegt
```bash
# Welcher Prozess nutzt Port 8001?
lsof -i :8001

# Prozess beenden
kill -9 <PID>

# Oder anderen Port in ecosystem.config.js verwenden
```

---

## Frontend zeigt Fehler

### Symptom
- Weiße Seite
- "Failed to fetch" Fehler
- Bilder laden nicht

### Diagnose

```bash
# Build-Verzeichnis existiert?
ls -la /var/www/apebrain/frontend/build

# Nginx zeigt richtige Seite?
curl http://localhost

# Browser Console öffnen (F12) und Fehler prüfen
```

### Lösungen

#### Frontend neu bauen
```bash
cd /var/www/apebrain/frontend
yarn install
yarn build
systemctl reload nginx
```

#### API URL falsch
```bash
# .env prüfen
cat /var/www/apebrain/frontend/.env

# Muss sein:
# REACT_APP_BACKEND_URL=https://apebrain.cloud

# Nach Änderung neu bauen:
yarn build
systemctl reload nginx
```

#### CORS Fehler
```bash
# Backend .env prüfen
cat /var/www/apebrain/backend/.env

# CORS_ORIGINS muss Frontend-Domain enthalten:
# CORS_ORIGINS="https://apebrain.cloud,https://www.apebrain.cloud"

pm2 restart apebrain-backend
```

---

## MongoDB Probleme

### MongoDB startet nicht

```bash
# Status prüfen
systemctl status mongod

# Fehler-Logs
tail -100 /var/log/mongodb/mongod.log

# Häufiges Problem: Disk voll
df -h

# Alte Logs löschen falls nötig
find /var/log -type f -name "*.log" -mtime +30 -delete

# Neu starten
systemctl restart mongod
```

### Datenbank-Verbindung schlägt fehl

```bash
# MongoDB läuft?
systemctl status mongod

# Verbindung testen
mongosh

# In mongosh:
show dbs
use apebrain_blog
show collections
```

### Datenbank zurücksetzen (⚠️ Löscht alle Daten!)

```bash
mongosh

# In mongosh:
use apebrain_blog
db.dropDatabase()
exit

# Backend neu starten
pm2 restart apebrain-backend
```

---

## SSL/HTTPS Probleme

### SSL-Zertifikat abgelaufen

```bash
# Zertifikate prüfen
certbot certificates

# Manuell erneuern
certbot renew

# Nginx neu laden
systemctl reload nginx
```

### Certbot schlägt fehl

```bash
# Häufige Gründe:
# 1. DNS nicht richtig konfiguriert
ping apebrain.cloud  # Muss Server-IP zeigen

# 2. Port 80 nicht offen
ufw allow 80/tcp

# 3. Nginx läuft nicht
systemctl status nginx

# Erneut versuchen:
certbot --nginx -d apebrain.cloud -d www.apebrain.cloud
```

### Mixed Content Warnings

```bash
# Backend .env: FRONTEND_URL muss https:// sein
FRONTEND_URL="https://apebrain.cloud"

# Nginx: Alle HTTP -> HTTPS redirects prüfen
nano /etc/nginx/sites-available/apebrain
```

---

## PayPal Integration Fehler

### "PayPal not configured" Fehler

```bash
# Backend .env prüfen
cat /var/www/apebrain/backend/.env | grep PAYPAL

# Muss enthalten:
# PAYPAL_MODE="sandbox" oder "live"
# PAYPAL_CLIENT_ID="..."
# PAYPAL_CLIENT_SECRET="..."

pm2 restart apebrain-backend
```

### Bestellung schlägt fehl

```bash
# Backend Logs prüfen
pm2 logs apebrain-backend --lines 50

# PayPal Sandbox Credentials testen:
# https://developer.paypal.com/dashboard/

# Sandbox vs. Live Mode:
# Sandbox: Für Tests
# Live: Für echte Zahlungen
```

---

## Email-Benachrichtigungen funktionieren nicht

### Gmail SMTP Fehler

```bash
# Backend .env prüfen
cat /var/www/apebrain/backend/.env | grep SMTP

# Wichtig:
# 1. SMTP_PASSWORD muss ein Gmail "App-Passwort" sein!
#    Nicht Ihr normales Gmail-Passwort
#    Erstellen unter: https://myaccount.google.com/apppasswords

# 2. "Weniger sichere Apps" ist nicht mehr unterstützt
#    Nur App-Passwörter funktionieren

# Test-Email senden:
pm2 logs apebrain-backend | grep -i email
```

---

## Performance-Probleme

### Website lädt langsam

```bash
# System-Ressourcen prüfen
htop
free -h
df -h

# Nginx Zugriffs-Logs
tail -f /var/log/nginx/access.log

# PM2 Monitoring
pm2 monit
```

### Hoher RAM-Verbrauch

```bash
# Größten Prozess finden
ps aux --sort=-%mem | head

# PM2 Memory Limit anpassen
nano /var/www/apebrain/backend/ecosystem.config.js
# max_memory_restart: '1G' -> '512M'

pm2 restart apebrain-backend
```

### Disk Space voll

```bash
# Größte Verzeichnisse finden
du -h --max-depth=1 / | sort -hr | head -10

# Alte Logs löschen
find /var/log -type f -name "*.log" -mtime +30 -delete

# PM2 Logs rotieren
pm2 flush  # Löscht alte PM2 Logs

# MongoDB Logs rotieren
logrotate -f /etc/logrotate.d/mongodb
```

---

## Häufige Kommandos

### Services neu starten
```bash
pm2 restart apebrain-backend
systemctl restart nginx
systemctl restart mongod
```

### Alle Logs auf einmal prüfen
```bash
# Backend
pm2 logs apebrain-backend --lines 50

# Nginx
tail -50 /var/log/nginx/error.log

# MongoDB
tail -50 /var/log/mongodb/mongod.log

# System
journalctl -xe | tail -50
```

### Services Status
```bash
pm2 status
systemctl status nginx
systemctl status mongod
ufw status
```

### Vollständiger Neustart
```bash
pm2 restart all
systemctl restart nginx
systemctl restart mongod
```

---

## Hilfe bekommen

Wenn das Problem weiterhin besteht:

1. **Logs sammeln**:
   ```bash
   pm2 logs apebrain-backend --lines 100 > backend.log
   tail -100 /var/log/nginx/error.log > nginx.log
   ```

2. **System-Info**:
   ```bash
   uname -a
   free -h
   df -h
   ```

3. **GitHub Issue öffnen** mit:
   - Problembeschreibung
   - Logs (backend.log, nginx.log)
   - System-Info
   - Was Sie bereits versucht haben

---

**Bei Notfällen:** Server neu starten
```bash
reboot
```

Nach Reboot:
- MongoDB startet automatisch
- Nginx startet automatisch
- PM2 startet Backend automatisch (dank `pm2 startup`)
