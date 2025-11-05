#!/bin/bash
#############################################
# APEBRAIN.CLOUD - ULTIMATE 1-COMMAND SETUP
# Komplettes automatisches Setup für Ubuntu 24.04
# Mit Debugging, Logging & Auto-Update
#############################################

set -e  # Exit bei Fehler

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Log-Datei
LOGFILE="/root/apebrain-setup.log"
exec > >(tee -a ${LOGFILE})
exec 2>&1

echo -e "${GREEN}"
cat << "EOF"
╔══════════════════════════════════════════╗
║   🍄🧠 APEBRAIN.CLOUD ULTIMATE SETUP   ║
║   Vollautomatische Installation         ║
╚══════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Konfiguration
GITHUB_REPO="robinzi2001-cell/apebrain.cloud"
DOMAIN="apebrain.cloud"
APP_DIR="/var/www/apebrain"
BACKEND_PORT=8001

echo -e "${BLUE}[INFO] Starte Setup um $(date)${NC}"
echo -e "${BLUE}[INFO] GitHub Repo: ${GITHUB_REPO}${NC}"
echo -e "${BLUE}[INFO] Domain: ${DOMAIN}${NC}"
echo ""

#############################################
# SCHRITT 1: SYSTEM UPDATE
#############################################
echo -e "${GREEN}[1/12] System wird aktualisiert...${NC}"
apt update && apt upgrade -y
apt install -y curl wget git ufw fail2ban htop vim nano software-properties-common jq net-tools

#############################################
# SCHRITT 2: FIREWALL
#############################################
echo -e "${GREEN}[2/12] Firewall wird konfiguriert...${NC}"
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
ufw status

#############################################
# SCHRITT 3: NODE.JS & YARN
#############################################
echo -e "${GREEN}[3/12] Node.js & Yarn werden installiert...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
npm install -g yarn pm2

echo -e "${BLUE}Node.js: $(node --version)${NC}"
echo -e "${BLUE}NPM: $(npm --version)${NC}"
echo -e "${BLUE}Yarn: $(yarn --version)${NC}"
echo -e "${BLUE}PM2: $(pm2 --version)${NC}"

#############################################
# SCHRITT 4: PYTHON 3.12
#############################################
echo -e "${GREEN}[4/12] Python 3.12 wird installiert...${NC}"
apt install -y python3 python3-pip python3-venv python3-dev build-essential

echo -e "${BLUE}Python: $(python3 --version)${NC}"
echo -e "${BLUE}Pip: $(pip3 --version)${NC}"

#############################################
# SCHRITT 5: MONGODB 7.0
#############################################
echo -e "${GREEN}[5/12] MongoDB 7.0 wird installiert...${NC}"
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
  gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
  tee /etc/apt/sources.list.d/mongodb-org-7.0.list

apt update
apt install -y mongodb-org

systemctl start mongod
systemctl enable mongod

if systemctl is-active --quiet mongod; then
    echo -e "${GREEN}✅ MongoDB läuft${NC}"
else
    echo -e "${RED}❌ MongoDB konnte nicht gestartet werden${NC}"
    echo -e "${YELLOW}Prüfe Logs: journalctl -xeu mongod${NC}"
    exit 1
fi

#############################################
# SCHRITT 6: NGINX
#############################################
echo -e "${GREEN}[6/12] Nginx wird installiert...${NC}"
apt install -y nginx

systemctl start nginx
systemctl enable nginx

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx läuft${NC}"
else
    echo -e "${RED}❌ Nginx konnte nicht gestartet werden${NC}"
    exit 1
fi

#############################################
# SCHRITT 7: CERTBOT (SSL)
#############################################
echo -e "${GREEN}[7/12] Certbot wird installiert...${NC}"
apt install -y certbot python3-certbot-nginx

#############################################
# SCHRITT 8: GITHUB REPOSITORY KLONEN
#############################################
echo -e "${GREEN}[8/12] GitHub Repository wird geklont...${NC}"

rm -rf ${APP_DIR}
mkdir -p ${APP_DIR}
cd ${APP_DIR}

git clone https://github.com/${GITHUB_REPO}.git .

if [ ! -f "${APP_DIR}/backend/server.py" ]; then
    echo -e "${RED}❌ Repository-Struktur ungültig!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Repository geklont${NC}"

#############################################
# SCHRITT 9: BACKEND SETUP
#############################################
echo -e "${GREEN}[9/12] Backend wird eingerichtet...${NC}"
cd ${APP_DIR}/backend

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# .env Datei erstellen
echo -e "${YELLOW}[INFO] Erstelle Backend .env Datei...${NC}"
cat > .env << EOF
# MongoDB
MONGO_URL="mongodb://localhost:27017"
DB_NAME="apebrain_blog"

# CORS & Security
CORS_ORIGINS="https://${DOMAIN},https://www.${DOMAIN},http://${DOMAIN},http://www.${DOMAIN}"
FRONTEND_URL="https://${DOMAIN}"
JWT_SECRET_KEY="$(openssl rand -hex 32)"

# ⚠️ WICHTIG: Fügen Sie Ihre echten API Keys hier ein!
# Anleitung: nano /var/www/apebrain/backend/.env

# AI Integration
GEMINI_API_KEY="AIzaSyAzgWsRn-KbO9qLJZ1A0_ZvJZZ9AxL2Aok"
EMERGENT_LLM_KEY="sk-emergent-130C20f3fB753C8F9D"

# Pexels (Bilder)
PEXELS_API_KEY="yXxO4WFMwcmGA9XcjDolPJ6rDQKfALaZJ0T0xGWaQQF9AusyO7umw7Vm"

# Admin Credentials
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="apebrain2024"

# PayPal Integration (LIVE KEYS)
PAYPAL_MODE="live"
PAYPAL_CLIENT_ID="AWjyyJVME51tjwiVT0z5G7o9Ym3Mhx9-fuQcTHiV5-Hch9i_VVbgx7Jg9JBb77FBkky707aaYPT8RwCD"
PAYPAL_CLIENT_SECRET="EFD-znjsCz6qgICb8RWGUQL-r9sviePFsceju7D-AugsgveDalt81giZzgUl5veeqyOumRRvqEYTJOD1"

# Email (Gmail)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="apebrain333@gmail.com"
SMTP_PASSWORD="eozyartxejsdueqs"
NOTIFICATION_EMAIL="apebrain333@gmail.com"

# Google OAuth
GOOGLE_CLIENT_ID="843038928917-156ufq5uhk19ebvs3umao28gv15r0q0e.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="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"
EOF

deactivate
echo -e "${GREEN}✅ Backend konfiguriert${NC}"

#############################################
# SCHRITT 10: FRONTEND SETUP
#############################################
echo -e "${GREEN}[10/12] Frontend wird eingerichtet...${NC}"
cd ${APP_DIR}/frontend

yarn install

cat > .env << EOF
REACT_APP_BACKEND_URL=https://${DOMAIN}
EOF

echo -e "${BLUE}[INFO] Frontend wird gebaut (dauert 3-5 Min)...${NC}"
yarn build

if [ ! -d "${APP_DIR}/frontend/build" ]; then
    echo -e "${RED}❌ Frontend-Build fehlgeschlagen${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Frontend gebaut${NC}"

#############################################
# SCHRITT 11: NGINX KONFIGURIEREN
#############################################
echo -e "${GREEN}[11/12] Nginx wird konfiguriert...${NC}"

cat > /etc/nginx/sites-available/apebrain << 'EOFNGINX'
server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER www.DOMAIN_PLACEHOLDER;

    root /var/www/apebrain/frontend/build;
    index index.html;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

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
        
        # Timeouts for large uploads
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Static Files mit Caching
    location /static {
        alias /var/www/apebrain/frontend/build/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Logs
    access_log /var/log/nginx/apebrain-access.log;
    error_log /var/log/nginx/apebrain-error.log;
}
EOFNGINX

# Domain ersetzen
sed -i "s/DOMAIN_PLACEHOLDER/${DOMAIN}/g" /etc/nginx/sites-available/apebrain

ln -sf /etc/nginx/sites-available/apebrain /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t

if [ $? -eq 0 ]; then
    systemctl reload nginx
    echo -e "${GREEN}✅ Nginx konfiguriert${NC}"
else
    echo -e "${RED}❌ Nginx-Konfiguration fehlerhaft${NC}"
    exit 1
fi

#############################################
# SCHRITT 12: PM2 BACKEND STARTEN
#############################################
echo -e "${GREEN}[12/12] Backend wird mit PM2 gestartet...${NC}"
cd ${APP_DIR}/backend

cat > ecosystem.config.js << 'EOFPM2'
module.exports = {
  apps: [{
    name: 'apebrain-backend',
    script: 'venv/bin/uvicorn',
    args: 'server:app --host 0.0.0.0 --port 8001 --workers 2',
    cwd: '/var/www/apebrain/backend',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    },
    error_file: '/var/log/apebrain-backend-error.log',
    out_file: '/var/log/apebrain-backend-out.log',
    log_file: '/var/log/apebrain-backend-combined.log',
    time: true
  }]
};
EOFPM2

pm2 delete apebrain-backend 2>/dev/null || true
pm2 start ecosystem.config.js
pm2 save
pm2 startup systemd -u root --hp /root

echo -e "${GREEN}✅ Backend gestartet${NC}"

#############################################
# MONITORING & DEBUG SCRIPTS ERSTELLEN
#############################################
echo -e "${GREEN}[BONUS] Erstelle Debug & Update Scripts...${NC}"

# Debug Script
cat > /root/apebrain-debug.sh << 'EOFDEBUG'
#!/bin/bash
echo "🔍 APEBRAIN.CLOUD - SYSTEM DEBUG"
echo "================================"
echo ""
echo "📊 SERVICES STATUS:"
echo "-------------------"
echo "Backend (PM2):"
pm2 status
echo ""
echo "Nginx:"
systemctl status nginx --no-pager | head -5
echo ""
echo "MongoDB:"
systemctl status mongod --no-pager | head -5
echo ""
echo "🔥 Firewall:"
ufw status
echo ""
echo "📝 LETZTE LOGS:"
echo "-------------------"
echo "Backend (letzte 20 Zeilen):"
pm2 logs apebrain-backend --lines 20 --nostream
echo ""
echo "Nginx Fehler (letzte 10 Zeilen):"
tail -10 /var/log/nginx/apebrain-error.log
echo ""
echo "💾 DISK SPACE:"
df -h | grep -E "Filesystem|/dev/"
echo ""
echo "🧠 MEMORY:"
free -h
echo ""
echo "🌐 NETWORK TEST:"
curl -s -o /dev/null -w "Backend API Status: %{http_code}\n" http://localhost:8001/api/products
EOFDEBUG

chmod +x /root/apebrain-debug.sh

# Update Script
cat > /root/apebrain-update.sh << 'EOFUPDATE'
#!/bin/bash
echo "🔄 APEBRAIN.CLOUD - UPDATE"
echo "=========================="
echo ""

cd /var/www/apebrain

echo "📥 Pulling latest changes from GitHub..."
git pull origin main || git pull origin master

echo ""
echo "🐍 Updating Backend..."
cd /var/www/apebrain/backend
source venv/bin/activate
pip install -r requirements.txt
deactivate

echo ""
echo "⚛️  Updating Frontend..."
cd /var/www/apebrain/frontend
yarn install
yarn build

echo ""
echo "🔄 Restarting Services..."
pm2 restart apebrain-backend
systemctl reload nginx

echo ""
echo "✅ UPDATE COMPLETE!"
pm2 status
EOFUPDATE

chmod +x /root/apebrain-update.sh

# Health Check Script
cat > /root/apebrain-health.sh << 'EOFHEALTH'
#!/bin/bash
echo "🏥 APEBRAIN.CLOUD - HEALTH CHECK"
echo "================================"
echo ""

# Backend API Test
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/products)
if [ "$BACKEND_STATUS" == "200" ]; then
    echo "✅ Backend API: OK ($BACKEND_STATUS)"
else
    echo "❌ Backend API: FEHLER ($BACKEND_STATUS)"
fi

# Frontend Test
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost)
if [ "$FRONTEND_STATUS" == "200" ]; then
    echo "✅ Frontend: OK ($FRONTEND_STATUS)"
else
    echo "❌ Frontend: FEHLER ($FRONTEND_STATUS)"
fi

# MongoDB Test
if systemctl is-active --quiet mongod; then
    echo "✅ MongoDB: RUNNING"
else
    echo "❌ MongoDB: GESTOPPT"
fi

# Nginx Test
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx: RUNNING"
else
    echo "❌ Nginx: GESTOPPT"
fi

# PM2 Test
PM2_STATUS=$(pm2 status | grep "apebrain-backend" | grep "online" || echo "error")
if [ "$PM2_STATUS" != "error" ]; then
    echo "✅ PM2 Backend: RUNNING"
else
    echo "❌ PM2 Backend: GESTOPPT"
fi

echo ""
echo "📊 SYSTEM RESOURCES:"
echo "Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
echo "Disk: $(df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 " used)"}')"
EOFHEALTH

chmod +x /root/apebrain-health.sh

# Cron Job für Auto-Updates (optional)
cat > /root/setup-auto-update.sh << 'EOFCRON'
#!/bin/bash
echo "Möchten Sie automatische Updates aktivieren?"
echo "Dies führt jeden Tag um 3 Uhr morgens ein Update durch."
read -p "Aktivieren? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    (crontab -l 2>/dev/null; echo "0 3 * * * /root/apebrain-update.sh >> /var/log/apebrain-auto-update.log 2>&1") | crontab -
    echo "✅ Auto-Update aktiviert (täglich 3 Uhr)"
else
    echo "Auto-Update nicht aktiviert"
fi
EOFCRON

chmod +x /root/setup-auto-update.sh

#############################################
# SSL EINRICHTEN
#############################################
echo ""
echo -e "${GREEN}[SSL] SSL-Zertifikat einrichten...${NC}"
echo -e "${YELLOW}WICHTIG: DNS muss auf diese Server-IP zeigen!${NC}"
echo -e "${YELLOW}Prüfen Sie: ping ${DOMAIN}${NC}"
echo ""

read -p "DNS korrekt konfiguriert und möchten Sie SSL jetzt einrichten? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos --register-unsafely-without-email || {
        echo -e "${YELLOW}⚠️  SSL-Setup fehlgeschlagen. Versuchen Sie später manuell:${NC}"
        echo "certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
    }
else
    echo -e "${YELLOW}⚠️  SSL übersprungen. Führen Sie später aus:${NC}"
    echo "certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
fi

#############################################
# FINALE ZUSAMMENFASSUNG
#############################################
echo ""
echo -e "${GREEN}"
cat << "EOF"
╔══════════════════════════════════════════╗
║   ✅ SETUP ERFOLGREICH ABGESCHLOSSEN!   ║
╚══════════════════════════════════════════╝
EOF
echo -e "${NC}"
echo ""
echo -e "${BLUE}📊 INSTALLATION ZUSAMMENFASSUNG:${NC}"
echo "=================================="
echo -e "✅ System aktualisiert"
echo -e "✅ Firewall konfiguriert"
echo -e "✅ Node.js, Python, MongoDB installiert"
echo -e "✅ Nginx konfiguriert"
echo -e "✅ GitHub Repository geklont"
echo -e "✅ Backend & Frontend installiert"
echo -e "✅ PM2 Backend gestartet"
echo -e "✅ Debug-Scripts erstellt"
echo ""
echo -e "${YELLOW}⚠️  WICHTIGE NÄCHSTE SCHRITTE:${NC}"
echo "=================================="
echo ""
echo "1. API KEYS KONFIGURIEREN (ERFORDERLICH!):"
echo "   nano /var/www/apebrain/backend/.env"
echo ""
echo "   Fügen Sie echte Werte ein für:"
echo "   - GEMINI_API_KEY"
echo "   - PEXELS_API_KEY"
echo "   - PAYPAL_CLIENT_ID & SECRET"
echo "   - SMTP_USER & PASSWORD (Gmail)"
echo "   - GOOGLE_CLIENT_ID & SECRET"
echo "   - ADMIN_PASSWORD ändern!"
echo ""
echo "2. BACKEND NEU STARTEN:"
echo "   pm2 restart apebrain-backend"
echo ""
echo "3. SSL EINRICHTEN (falls noch nicht):"
echo "   certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
echo ""
echo -e "${GREEN}🔧 NÜTZLICHE BEFEHLE:${NC}"
echo "=================================="
echo "📊 System-Status prüfen:    /root/apebrain-health.sh"
echo "🔍 Debug-Informationen:     /root/apebrain-debug.sh"
echo "🔄 App aktualisieren:       /root/apebrain-update.sh"
echo "📝 Backend Logs:            pm2 logs apebrain-backend"
echo "📝 Nginx Logs:              tail -f /var/log/nginx/apebrain-error.log"
echo "🔄 Services neu starten:    pm2 restart apebrain-backend && systemctl reload nginx"
echo ""
echo -e "${GREEN}🌐 IHRE WEBSITE:${NC}"
echo "=================================="
echo "HTTP:  http://${DOMAIN}"
echo "HTTPS: https://${DOMAIN} (nach SSL-Setup)"
echo "Admin: https://${DOMAIN}/shroomsadmin"
echo ""
echo -e "${BLUE}📋 SETUP LOG:${NC}"
echo "Vollständiges Log: ${LOGFILE}"
echo ""
echo -e "${GREEN}🎉 VIEL ERFOLG MIT APEBRAIN.CLOUD! 🍄🧠${NC}"
echo ""
