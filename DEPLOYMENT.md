# 🚀 APEBRAIN.CLOUD - Deployment Guide

**Vollständige Anleitung für Ubuntu 24.04 Server (Hostinger VPS)**

---

## 📋 Inhaltsverzeichnis

1. [Server-Vorbereitung](#1-server-vorbereitung)
2. [DNS-Konfiguration](#2-dns-konfiguration)
3. [Installation](#3-installation)
4. [API Keys Konfiguration](#4-api-keys-konfiguration)
5. [SSL-Einrichtung](#5-ssl-einrichtung)
6. [Verifizierung](#6-verifizierung)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Server-Vorbereitung

### 1.1 Hostinger VPS bestellen

1. Gehe zu [Hostinger VPS](https://www.hostinger.com/vps-hosting)
2. Wähle einen Plan (mind. 2 CPU / 4GB RAM empfohlen)
3. OS: **Ubuntu 24.04 LTS**
4. Nach Bestellung erhältst du:
   - Server-IP-Adresse
   - Root-Passwort (per Email)

### 1.2 SSH Verbindung einrichten

**Windows (PowerShell/CMD):**
```powershell
ssh root@DEINE-SERVER-IP
```

**Mac/Linux:**
```bash
ssh root@DEINE-SERVER-IP
```

Beim ersten Login:
- Akzeptiere den Fingerprint (yes)
- Gib das Root-Passwort ein
- **Empfohlen**: Ändere das Passwort mit `passwd`

---

## 2. DNS-Konfiguration

### 2.1 A-Records erstellen

**Bei deinem Domain-Provider** (z.B. Namecheap, Cloudflare, etc.):

```
Typ: A
Name: @
Value: DEINE-SERVER-IP
TTL: 300 (5 Min)

Typ: A
Name: www
Value: DEINE-SERVER-IP
TTL: 300 (5 Min)
```

### 2.2 DNS Propagation prüfen

**Warte 5-30 Minuten**, dann teste:

```bash
ping yourdomain.com
ping www.yourdomain.com
```

**Erwartetes Ergebnis:**
```
PING yourdomain.com (DEINE-SERVER-IP) 56(84) bytes of data.
64 bytes from DEINE-SERVER-IP: icmp_seq=1 ttl=54 time=12.3 ms
```

**Online prüfen:**
- https://dnschecker.org/
- https://www.whatsmydns.net/

---

## 3. Installation

### 3.1 One-Command Setup

```bash
# 1. Setup-Script herunterladen
wget https://raw.githubusercontent.com/robinzi2001-cell/apebrain.cloud/main/ULTIMATE-SETUP.sh

# 2. Script anpassen
nano ULTIMATE-SETUP.sh
```

**Ändere diese Zeilen (ca. Zeile 30-32):**
```bash
GITHUB_REPO="robinzi2001-cell/apebrain.cloud"  # Dein GitHub Repo
DOMAIN="yourdomain.com"  # Deine Domain
APP_DIR="/var/www/apebrain"
```

**Speichern:** `Strg+X` → `Y` → `Enter`

```bash
# 3. Ausführbar machen
chmod +x ULTIMATE-SETUP.sh

# 4. Installation starten
./ULTIMATE-SETUP.sh
```

### 3.2 Was das Script macht

**Phase 1: System (5 Min)**
- System-Updates installieren
- Firewall konfigurieren (UFW)
- Fail2Ban einrichten

**Phase 2: Software Stack (5 Min)**
- Node.js 20 + Yarn
- Python 3.12 + pip
- MongoDB 7.0
- Nginx
- Certbot

**Phase 3: App Installation (10 Min)**
- GitHub Repository klonen
- Backend Dependencies installieren
- Frontend bauen (dauert am längsten)
- Nginx konfigurieren
- PM2 Backend starten

**Phase 4: Management Scripts**
- Health Check Script
- Debug Script
- Update Script

**Gesamtdauer: 15-20 Minuten**

### 3.3 SSL-Abfrage

Am Ende fragt das Script:
```
DNS korrekt konfiguriert und SSL jetzt einrichten? (y/n)
```

- **y** → Automatische SSL-Einrichtung
- **n** → SSL später manuell (siehe Abschnitt 5)

---

## 4. API Keys Konfiguration

### 4.1 Benötigte API Keys beschaffen

#### Gemini AI (Content-Generierung)
1. Gehe zu: https://makersuite.google.com/app/apikey
2. Klicke "Create API Key"
3. Kopiere den Key

#### Pexels API (Bilder)
1. Gehe zu: https://www.pexels.com/api/
2. Registriere dich kostenlos
3. Kopiere deinen API Key

#### PayPal (Zahlungen)
**Sandbox (Test):**
1. https://developer.paypal.com/
2. Dashboard → Apps & Credentials → Sandbox
3. Erstelle eine App → Kopiere Client ID & Secret

**Live (Production):**
1. Wechsle zu "Live" Tab
2. Erstelle eine Live App
3. Kopiere Live Client ID & Secret

#### Gmail App Password (Email-Versand)
1. Google Account → https://myaccount.google.com/apppasswords
2. App auswählen: "Mail"
3. Gerät: "Other" → "APEBRAIN"
4. Generieren → Kopiere das 16-stellige Passwort

#### Google OAuth (Social Login)
1. https://console.cloud.google.com/apis/credentials
2. "CREATE CREDENTIALS" → "OAuth client ID"
3. Application type: "Web application"
4. Authorized redirect URIs:
   ```
   https://yourdomain.com/auth/google/callback
   ```
5. Kopiere Client ID & Client Secret

### 4.2 API Keys einfügen

```bash
nano /var/www/apebrain/backend/.env
```

**Füge deine echten Keys ein:**
```env
# AI Integration
GEMINI_API_KEY="AIzaSy..."

# Pexels
PEXELS_API_KEY="yXxO4WF..."

# PayPal (LIVE für Production!)
PAYPAL_MODE="live"  # oder "sandbox"
PAYPAL_CLIENT_ID="AWjyyJV..."
PAYPAL_CLIENT_SECRET="EFD-znj..."

# Gmail
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="xxxx xxxx xxxx xxxx"  # App Password!
NOTIFICATION_EMAIL="your-email@gmail.com"

# Google OAuth
GOOGLE_CLIENT_ID="843038928...-....apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="GOCSPX-..."

# Admin Password (ÄNDERN!)
ADMIN_PASSWORD="your-secure-password-123"

# URLs (anpassen!)
FRONTEND_URL="https://yourdomain.com"
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

**Speichern:** `Strg+X` → `Y` → `Enter`

### 4.3 Backend neu starten

```bash
pm2 restart apebrain-backend

# Logs prüfen (sollten keine Fehler zeigen)
pm2 logs apebrain-backend --lines 20
```

---

## 5. SSL-Einrichtung

### 5.1 Automatisch (wenn DNS bereit)

```bash
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**Fragen beantworten:**
- Email: `your-email@gmail.com` (für Renewal-Benachrichtigungen)
- Terms: `A` (Agree)
- Redirect HTTP → HTTPS: `2` (Ja, empfohlen)

### 5.2 Auto-Renewal prüfen

```bash
# Renewal-Test (macht kein echtes Renewal)
certbot renew --dry-run
```

**Erwartetes Ergebnis:**
```
Congratulations, all simulated renewals succeeded
```

### 5.3 SSL-Status prüfen

```bash
# Zertifikat-Info
certbot certificates

# Nginx-Config prüfen
nginx -t
systemctl reload nginx
```

**Online SSL-Test:**
- https://www.ssllabs.com/ssltest/

---

## 6. Verifizierung

### 6.1 Health Check ausführen

```bash
/root/apebrain-health.sh
```

**Erwartete Ausgabe:**
```
✅ Backend API: OK (200)
✅ Frontend: OK (200)
✅ MongoDB: RUNNING
✅ Nginx: RUNNING
✅ PM2 Backend: RUNNING
```

### 6.2 Website testen

**Im Browser öffnen:**
1. **Frontend**: `https://yourdomain.com`
   - Landing Page sollte sichtbar sein
   - Dark Theme mit 🍄🧠 Icon
   
2. **Blog**: `https://yourdomain.com/blog`
   - 6 Kategorien sichtbar
   
3. **Shop**: `https://yourdomain.com/shop`
   - Produkte werden geladen
   
4. **Admin**: `https://yourdomain.com/shroomsadmin`
   - Login mit deinem Admin-Passwort

### 6.3 API Endpoints testen

```bash
# Produkte abrufen
curl https://yourdomain.com/api/products

# Blog-Posts abrufen
curl https://yourdomain.com/api/blogs

# Health-Endpoint
curl https://yourdomain.com/api/health
```

### 6.4 Logs prüfen

```bash
# Backend Logs (sollten keine Errors zeigen)
pm2 logs apebrain-backend --lines 50

# Nginx Logs
tail -30 /var/log/nginx/apebrain-access.log
tail -30 /var/log/nginx/apebrain-error.log
```

---

## 7. Troubleshooting

### Problem: Backend startet nicht

**Symptom:** PM2 zeigt "errored" oder "stopped"

**Lösung:**
```bash
# Logs prüfen
pm2 logs apebrain-backend --lines 100

# Häufigste Ursachen:
# 1. .env Datei fehlt oder falsch
cat /var/www/apebrain/backend/.env

# 2. Python Dependencies fehlen
cd /var/www/apebrain/backend
source venv/bin/activate
pip install -r requirements.txt

# 3. Port 8001 bereits belegt
lsof -i :8001
kill -9 PID  # PID ersetzen

# Backend neu starten
pm2 restart apebrain-backend
```

### Problem: Frontend zeigt 502 Bad Gateway

**Symptom:** Website zeigt Nginx-Fehlerseite

**Lösung:**
```bash
# Backend-Status prüfen
pm2 status

# Falls Backend stopped → neu starten
pm2 restart apebrain-backend

# Nginx-Config testen
nginx -t

# Nginx neu laden
systemctl reload nginx
```

### Problem: MongoDB verbindet nicht

**Symptom:** Backend-Logs zeigen "Connection refused"

**Lösung:**
```bash
# MongoDB Status
systemctl status mongod

# Falls inactive → starten
systemctl start mongod
systemctl enable mongod

# Logs prüfen
journalctl -xeu mongod

# Backend neu starten
pm2 restart apebrain-backend
```

### Problem: SSL-Zertifikat schlägt fehl

**Symptom:** Certbot Error "DNS resolution failed"

**Lösung:**
```bash
# DNS prüfen
ping yourdomain.com

# Falls DNS nicht auflöst:
# 1. A-Records nochmal prüfen
# 2. DNS Propagation abwarten (bis zu 48h)
# 3. Online prüfen: https://dnschecker.org/

# Certbot erneut versuchen (wenn DNS OK)
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Problem: Frontend-Build schlägt fehl

**Symptom:** `yarn build` Error

**Lösung:**
```bash
cd /var/www/apebrain/frontend

# Dependencies neu installieren
rm -rf node_modules
yarn install

# Build erneut versuchen
yarn build

# Falls weiterhin Fehler → Logs prüfen
```

### Problem: API Keys funktionieren nicht

**Symptom:** Backend-Logs zeigen "Invalid API Key"

**Lösung:**
```bash
# .env Datei prüfen
cat /var/www/apebrain/backend/.env

# Häufige Fehler:
# 1. Anführungszeichen falsch: GEMINI_API_KEY=AIzaSy... (ohne "")
# 2. Leerzeichen: GEMINI_API_KEY= "..." (Leerzeichen entfernen)
# 3. Falscher Key-Name: GEMINI_KEY vs GEMINI_API_KEY

# Nach Änderungen:
pm2 restart apebrain-backend
```

---

## 🎯 Post-Deployment Checklist

- [ ] DNS A-Records zeigen auf Server-IP
- [ ] SSL-Zertifikat eingerichtet (HTTPS funktioniert)
- [ ] Health Check läuft erfolgreich durch
- [ ] API Keys in `.env` eingefügt
- [ ] Backend läuft (PM2 Status: online)
- [ ] Frontend erreichbar (Landing Page lädt)
- [ ] Admin-Panel erreichbar & Login funktioniert
- [ ] Blog-Seiten laden
- [ ] Shop-Seiten laden
- [ ] PayPal-Test-Zahlung (Sandbox) erfolgreich
- [ ] Google OAuth funktioniert
- [ ] Email-Benachrichtigungen funktionieren
- [ ] Admin-Passwort geändert
- [ ] Firewall aktiv (UFW)
- [ ] MongoDB läuft & erreichbar
- [ ] Backups eingerichtet (optional)

---

## 🔄 Regelmäßige Wartung

### Wöchentlich
```bash
# System-Updates
apt update && apt upgrade -y

# Health Check
/root/apebrain-health.sh

# Logs prüfen
pm2 logs apebrain-backend --lines 50
```

### Monatlich
```bash
# Datenbank-Backup
mongodump --db apebrain_blog --out /root/backups/$(date +%Y%m%d)

# SSL-Renewal Test
certbot renew --dry-run

# Disk Space prüfen
df -h
```

### Bei Code-Updates
```bash
# Automatisch
/root/apebrain-update.sh

# Oder manuell
cd /var/www/apebrain
git pull origin main
cd backend && source venv/bin/activate && pip install -r requirements.txt && deactivate
cd ../frontend && yarn install && yarn build
pm2 restart apebrain-backend
systemctl reload nginx
```

---

## 📞 Support

**Bei Problemen:**
1. Logs prüfen: `/root/apebrain-debug.sh`
2. Health Check: `/root/apebrain-health.sh`
3. Setup Log: `cat /root/apebrain-setup.log`

---

**🍄🧠 Happy Deploying!**
