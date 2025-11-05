# 🚀 APEBRAIN.CLOUD - SCHNELLSTART ANLEITUNG

## 📋 VORAUSSETZUNGEN

### Was Sie brauchen:
1. ✅ **Hostinger VPS** mit Ubuntu 24.04
2. ✅ **Domain:** apebrain.cloud
3. ✅ **DNS-Einträge** (siehe unten)
4. ✅ **API Keys** (siehe unten)
5. ✅ **SSH-Zugriff:** `ssh root@72.61.177.155`

---

## 🌐 SCHRITT 1: DNS KONFIGURIEREN

### Bei Ihrem Domain-Provider (Hostinger/Namecheap/etc.):

Erstellen Sie diese DNS-Records:

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

### DNS-Propagation testen:
```bash
ping apebrain.cloud
# Sollte 72.61.177.155 zurückgeben
```

⏰ **Wartezeit:** 5-60 Minuten

---

## 🔑 SCHRITT 2: API KEYS VORBEREITEN

Sammeln Sie folgende API Keys:

### 1. Gemini AI (Für Blog-Generierung)
- **Wo:** https://makersuite.google.com/app/apikey
- **Beispiel:** `AIzaSyBTiERhWmrXx-UKdkOWOV7msA6XB9DYnww`

### 2. Pexels (Für Bilder)
- **Wo:** https://www.pexels.com/api/
- **Beispiel:** `yXxO4WFMwcmGA9XcjDolPJ6rDQKfALaZJ0T0xGWaQQF9AusyO7umw7Vm`

### 3. PayPal (Für Zahlungen)
- **Wo:** https://developer.paypal.com/dashboard/
- **Benötigt:** Client ID & Client Secret
- **Modus:** `sandbox` (Testen) oder `live` (Produktion)

### 4. Gmail (Für Email-Benachrichtigungen)
- **App-Passwort erstellen:** https://myaccount.google.com/apppasswords
- **NICHT** Ihr normales Gmail-Passwort!

### 5. Google OAuth (Für Login)
- **Wo:** https://console.cloud.google.com/
- **Benötigt:** Client ID & Client Secret

---

## 🚀 SCHRITT 3: INSTALLATION (1 BEFEHL!)

### SSH zum Server verbinden:
```bash
ssh root@72.61.177.155
```

### Ultimate Setup ausführen:
```bash
wget https://raw.githubusercontent.com/robinzi2001-cell/apebrain.cloud/main/ULTIMATE-SETUP.sh
chmod +x ULTIMATE-SETUP.sh
./ULTIMATE-SETUP.sh
```

**Das Script macht automatisch:**
- ✅ System Update
- ✅ Firewall konfigurieren
- ✅ Node.js, Python, MongoDB installieren
- ✅ Nginx konfigurieren
- ✅ GitHub Repo klonen
- ✅ Backend & Frontend installieren
- ✅ PM2 starten
- ✅ Debug-Scripts erstellen

⏱️ **Dauer:** 10-15 Minuten

---

## 🔧 SCHRITT 4: API KEYS EINFÜGEN

### Nach dem Setup:

```bash
nano /var/www/apebrain/backend/.env
```

### Fügen Sie Ihre echten Werte ein:

```env
# AI Integration
GEMINI_API_KEY="IHR_GEMINI_KEY_HIER"
EMERGENT_LLM_KEY="IHR_EMERGENT_KEY_HIER"  # Optional

# Pexels (Bilder)
PEXELS_API_KEY="IHR_PEXELS_KEY_HIER"

# Admin Credentials (ÄNDERN!)
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="IHR_SICHERES_PASSWORT"

# PayPal
PAYPAL_MODE="sandbox"  # oder "live"
PAYPAL_CLIENT_ID="IHR_PAYPAL_CLIENT_ID"
PAYPAL_CLIENT_SECRET="IHR_PAYPAL_SECRET"

# Email (Gmail)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="ihre-email@gmail.com"
SMTP_PASSWORD="IHR_GMAIL_APP_PASSWORT"
NOTIFICATION_EMAIL="ihre-email@gmail.com"

# Google OAuth
GOOGLE_CLIENT_ID="IHR_GOOGLE_CLIENT_ID"
GOOGLE_CLIENT_SECRET="IHR_GOOGLE_SECRET"
```

**Speichern:** `CTRL+X` → `Y` → `Enter`

### Backend neu starten:
```bash
pm2 restart apebrain-backend
```

---

## 🔒 SCHRITT 5: SSL AKTIVIEREN

```bash
certbot --nginx -d apebrain.cloud -d www.apebrain.cloud
```

**Folgen Sie den Prompts:**
1. Email eingeben (für Ablauf-Benachrichtigungen)
2. Terms akzeptieren: `Y`
3. Redirect wählen: `2` (HTTPS erzwingen)

✅ **Auto-Renewal** ist automatisch aktiviert!

---

## ✅ SCHRITT 6: TESTEN!

### Website öffnen:
```
https://apebrain.cloud
```

### Admin-Panel testen:
```
https://apebrain.cloud/shroomsadmin
Username: admin
Password: [Ihr Passwort aus .env]
```

### Features testen:
1. **Blog erstellen** - Admin → Blogs → Neuer Blog
2. **Produkt hinzufügen** - Admin → Produkte → Neues Produkt
3. **Shop testen** - Produkt in Warenkorb → Checkout
4. **Coupon testen** - Im Warenkorb "WELCOME10" eingeben

---

## 🔧 NÜTZLICHE BEFEHLE

### System-Status prüfen:
```bash
/root/apebrain-health.sh
```

### Debug-Informationen:
```bash
/root/apebrain-debug.sh
```

### App aktualisieren (neue Version von GitHub):
```bash
/root/apebrain-update.sh
```

### Backend Logs anzeigen:
```bash
pm2 logs apebrain-backend

# Oder letzte 50 Zeilen:
pm2 logs apebrain-backend --lines 50
```

### Nginx Logs:
```bash
tail -f /var/log/nginx/apebrain-error.log
```

### Services neu starten:
```bash
# Backend
pm2 restart apebrain-backend

# Nginx
systemctl reload nginx

# MongoDB
systemctl restart mongod

# Alles
pm2 restart all && systemctl reload nginx
```

### Status prüfen:
```bash
pm2 status
systemctl status nginx
systemctl status mongod
```

---

## 🔄 UPDATES DEPLOYEN

### Wenn Sie Änderungen auf GitHub gepusht haben:

```bash
/root/apebrain-update.sh
```

**Das macht das Script:**
1. Git pull (neueste Änderungen)
2. Backend Dependencies aktualisieren
3. Frontend neu bauen
4. Services neu starten

---

## 🆘 TROUBLESHOOTING

### Problem: Website nicht erreichbar

```bash
# DNS prüfen
ping apebrain.cloud

# Services prüfen
/root/apebrain-health.sh

# Logs anschauen
pm2 logs apebrain-backend
tail -50 /var/log/nginx/apebrain-error.log
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

### Problem: "Module not found"

```bash
cd /var/www/apebrain/backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
pm2 restart apebrain-backend
```

### Problem: MongoDB Connection Error

```bash
systemctl status mongod
systemctl restart mongod
```

### Problem: SSL-Fehler

```bash
certbot certificates
certbot --nginx -d apebrain.cloud -d www.apebrain.cloud --force-renewal
```

---

## 📊 MONITORING

### System-Ressourcen:
```bash
htop              # CPU, RAM, Prozesse
df -h             # Disk Space
free -h           # Memory
```

### Backend Monitoring:
```bash
pm2 monit         # Live-Monitoring
```

### Nginx Zugriffs-Logs:
```bash
tail -f /var/log/nginx/apebrain-access.log
```

---

## 🔐 SICHERHEIT

### SSH Key Authentication (empfohlen):

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

### Firewall Status:
```bash
ufw status
```

Sollte zeigen:
- 22/tcp (SSH) - ALLOW
- 80/tcp (HTTP) - ALLOW
- 443/tcp (HTTPS) - ALLOW

---

## 📝 BACKUP

### MongoDB Backup:
```bash
mkdir -p /backups/mongodb
mongodump --out /backups/mongodb/backup_$(date +%Y%m%d_%H%M%S)
```

### Automated Backups (Cronjob):
```bash
nano /root/backup-mongo.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mongodump --out /backups/mongodb/backup_$DATE
# Alte Backups löschen (älter als 7 Tage)
find /backups/mongodb -type d -mtime +7 -exec rm -rf {} +
```

```bash
chmod +x /root/backup-mongo.sh

# Täglich um 2 Uhr
crontab -e
# Hinzufügen:
0 2 * * * /root/backup-mongo.sh
```

---

## 🎯 FEATURE-CHECKLISTE

Nach dem Setup sollten diese Features funktionieren:

### ✅ Blog-System
- [ ] Neuen Blog erstellen
- [ ] Blog mit AI generieren
- [ ] Blog bearbeiten
- [ ] Blog löschen
- [ ] Blog veröffentlichen
- [ ] Bilder hochladen
- [ ] YouTube-Videos einbetten

### ✅ Shop & E-Commerce
- [ ] Produkte anzeigen
- [ ] Produkt hinzufügen
- [ ] Produkt bearbeiten
- [ ] Produkt löschen
- [ ] Produktbilder hochladen
- [ ] In Warenkorb legen
- [ ] Coupon anwenden
- [ ] PayPal-Checkout

### ✅ Bestellverwaltung
- [ ] Bestellungen anzeigen
- [ ] Bestellstatus ändern
- [ ] Tracking hinzufügen
- [ ] Email-Benachrichtigungen

### ✅ Coupon-System
- [ ] Coupon erstellen
- [ ] Coupon aktivieren/deaktivieren
- [ ] Coupon validieren im Shop
- [ ] Coupon löschen

### ✅ Benutzer-System
- [ ] Registrierung
- [ ] Login
- [ ] Dashboard
- [ ] Meine Bestellungen
- [ ] Google OAuth Login

### ✅ Admin-Panel
- [ ] Admin Login
- [ ] Dashboard
- [ ] Alle Verwaltungsfunktionen

---

## 📞 SUPPORT

Bei Problemen:

1. **Logs prüfen:**
   ```bash
   /root/apebrain-debug.sh
   ```

2. **Health Check:**
   ```bash
   /root/apebrain-health.sh
   ```

3. **Dokumentation:**
   - README.md
   - DEPLOYMENT_GUIDE.md
   - TROUBLESHOOTING.md

---

## 🎉 ERFOLG!

Wenn alles funktioniert:

✅ Website: https://apebrain.cloud
✅ Admin: https://apebrain.cloud/shroomsadmin
✅ Blog: https://apebrain.cloud/blog
✅ Shop: https://apebrain.cloud/shop

**Viel Erfolg mit APEBRAIN.CLOUD! 🍄🧠**
