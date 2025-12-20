#!/bin/bash
#############################################
# APEBRAIN.CLOUD - Automatisches Server Setup
# Ubuntu 24.04 LTS - Hostinger VPS
# FIXED VERSION - Production Ready
#############################################

set -e  # Exit bei Fehler

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════╗"
echo "║   🍄🧠 APEBRAIN.CLOUD Setup Script       ║"
echo "║   Ubuntu 24.04 - Hostinger VPS           ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# Konfiguration
GITHUB_REPO="robinzi2001-cell/apebrain.cloud"
APP_DIR="/var/www/apebrain"
BACKEND_PORT=8001

# Domain als Parameter oder Standard (KEIN read -p!)
DOMAIN="${1:-apebrain.cloud}"
echo -e "${GREEN}✅ Domain: $DOMAIN${NC}"
echo ""

#############################################
# 1. SYSTEM UPDATE
#############################################
echo -e "${GREEN}📦 System wird aktualisiert...${NC}"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq curl wget git ufw fail2ban htop vim nano software-properties-common

#############################################
# 2. FIREWALL SETUP
#############################################
echo -e "${GREEN}🔥 Firewall wird konfiguriert...${NC}"
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo -e "${GREEN}✅ Firewall aktiv${NC}"

#############################################
# 3. NODE.JS & YARN INSTALLIEREN
#############################################
echo -e "${GREEN}📦 Node.js 20.x wird installiert...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y -qq nodejs
npm install -g yarn pm2

echo "Node.js Version: $(node --version)"
echo "NPM Version: $(npm --version)"
echo "Yarn Version: $(yarn --version)"
echo "PM2 Version: $(pm2 --version)"
echo -e "${GREEN}✅ Node.js & PM2 installiert${NC}"

#############################################
# 4. PYTHON 3.12 INSTALLIEREN
#############################################
echo -e "${GREEN}🐍 Python 3.12 wird installiert...${NC}"
apt-get install -y -qq python3 python3-pip python3-venv python3-dev build-essential

echo "Python Version: $(python3 --version)"
echo "Pip Version: $(pip3 --version)"
echo -e "${GREEN}✅ Python installiert${NC}"

#############################################
# 5. MONGODB 7.0 INSTALLIEREN
#############################################
echo -e "${GREEN}🍃 MongoDB 7.0 wird installiert...${NC}"
if ! systemctl is-active --quiet mongod; then
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
      gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg

    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
      tee /etc/apt/sources.list.d/mongodb-org-7.0.list

    apt-get update -qq
    apt-get install -y -qq mongodb-org

    systemctl start mongod
    systemctl enable mongod
fi

if systemctl is-active --quiet mongod; then
    echo -e "${GREEN}✅ MongoDB läuft${NC}"
else
    echo -e "${RED}❌ MongoDB konnte nicht gestartet werden${NC}"
    exit 1
fi

#############################################
# 6. NGINX INSTALLIEREN
#############################################
echo -e "${GREEN}🌐 Nginx wird installiert...${NC}"
apt-get install -y -qq nginx

systemctl start nginx
systemctl enable nginx

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx läuft${NC}"
else
    echo -e "${RED}❌ Nginx konnte nicht gestartet werden${NC}"
    exit 1
fi

#############################################
# 7. CERTBOT (Let's Encrypt SSL)
#############################################
echo -e "${GREEN}🔒 Certbot wird installiert...${NC}"
apt-get install -y -qq certbot python3-certbot-nginx
echo -e "${GREEN}✅ Certbot installiert${NC}"

#############################################
# 8. APPLICATION DEPLOYEN
#############################################
echo -e "${GREEN}📥 GitHub Repository wird geklont...${NC}"

# Verzeichnis erstellen und bereinigen
rm -rf ${APP_DIR}
mkdir -p ${APP_DIR}

# Repository klonen
git clone https://github.com/${GITHUB_REPO}.git ${APP_DIR}

if [ ! -f "${APP_DIR}/backend/server.py" ]; then
    echo -e "${RED}❌ Repository-Klonen fehlgeschlagen oder falsche Struktur${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Repository geklont${NC}"

#############################################
# 9. BACKEND SETUP
#############################################
echo -e "${GREEN}🐍 Backend wird eingerichtet...${NC}"
cd ${APP_DIR}/backend

# FIX: emergentintegrations aus requirements.txt entfernen
echo -e "${YELLOW}🔧 Fixe requirements.txt (emergentintegrations entfernen)...${NC}"
grep -v "emergentintegrations" requirements.txt > requirements.tmp.txt
mv requirements.tmp.txt requirements.txt

# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install --upgrade pip
pip install -r requirements.txt

deactivate

# .env Datei erstellen (OHNE EMERGENT_LLM_KEY!)
if [ ! -f ".env" ]; then
    cat > .env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=apebrain_blog
CORS_ORIGINS=https://${DOMAIN},https://www.${DOMAIN}
FRONTEND_URL=https://${DOMAIN}
JWT_SECRET_KEY=$(openssl rand -hex 32)

# ⚠️ WICHTIG: Ersetzen Sie diese Platzhalter mit echten Werten!
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
PEXELS_API_KEY=YOUR_PEXELS_API_KEY

ADMIN_USERNAME=admin
ADMIN_PASSWORD=CHANGE_THIS_PASSWORD

PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=YOUR_PAYPAL_CLIENT_ID
PAYPAL_CLIENT_SECRET=YOUR_PAYPAL_CLIENT_SECRET

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=YOUR_EMAIL@gmail.com
SMTP_PASSWORD=YOUR_GMAIL_APP_PASSWORD
NOTIFICATION_EMAIL=YOUR_EMAIL@gmail.com

GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET
EOF
fi

echo -e "${GREEN}✅ Backend konfiguriert${NC}"
echo -e "${YELLOW}⚠️  WICHTIG: Bearbeiten Sie ${APP_DIR}/backend/.env mit Ihren API Keys!${NC}"

#############################################
# 10. FRONTEND SETUP
#############################################
echo -e "${GREEN}⚛️  Frontend wird eingerichtet...${NC}"
cd ${APP_DIR}/frontend

# Dependencies installieren
yarn install

# .env Datei erstellen
cat > .env << EOF
REACT_APP_BACKEND_URL=https://${DOMAIN}
EOF

# Frontend bauen
echo -e "${GREEN}🏗️  Frontend wird gebaut (dauert 5-10 Min)...${NC}"
yarn build

if [ ! -d "${APP_DIR}/frontend/build" ]; then
    echo -e "${RED}❌ Frontend-Build fehlgeschlagen${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Frontend gebaut${NC}"

#############################################
# 11. NGINX KONFIGURIEREN
#############################################
echo -e "${GREEN}🌐 Nginx wird konfiguriert...${NC}"

cat > /etc/nginx/sites-available/apebrain << EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN} www.${DOMAIN} _;

    root ${APP_DIR}/frontend/build;
    index index.html;

    # React Router Support
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API Proxy
    location /api {
        proxy_pass http://127.0.0.1:${BACKEND_PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static Files Caching
    location /static {
        alias ${APP_DIR}/frontend/build/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
EOF

# Site aktivieren
ln -sf /etc/nginx/sites-available/apebrain /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Nginx Konfiguration testen
nginx -t

if [ $? -eq 0 ]; then
    systemctl reload nginx
    echo -e "${GREEN}✅ Nginx konfiguriert${NC}"
else
    echo -e "${RED}❌ Nginx-Konfiguration fehlerhaft${NC}"
    exit 1
fi

#############################################
# 12. PM2 BACKEND STARTEN
#############################################
echo -e "${GREEN}⚙️  Backend wird mit PM2 gestartet...${NC}"
cd ${APP_DIR}/backend

# Alten Process stoppen (falls vorhanden)
pm2 delete apebrain-backend 2>/dev/null || true

# Backend mit Python starten (NICHT uvicorn!)
pm2 start venv/bin/python --name "apebrain-backend" -- server.py
pm2 save

# PM2 beim Systemstart starten
pm2 startup systemd -u root --hp /root

echo -e "${GREEN}✅ Backend läuft${NC}"

#############################################
# 13. HELPER SCRIPTS ERSTELLEN
#############################################
echo -e "${GREEN}📝 Helper Scripts werden erstellt...${NC}"

# Health Check Script
cat > /root/apebrain-health.sh << 'HEALTH_EOF'
#!/bin/bash
echo "=== ApeBrain Health Check ==="
echo ""
echo "MongoDB:"
systemctl status mongod --no-pager | grep Active || echo "❌ MongoDB nicht aktiv"
echo ""
echo "Nginx:"
systemctl status nginx --no-pager | grep Active || echo "❌ Nginx nicht aktiv"
echo ""
echo "Backend (PM2):"
pm2 list | grep apebrain-backend || echo "❌ Backend nicht aktiv"
echo ""
echo "API Test:"
curl -s http://localhost:8001/api/health 2>/dev/null && echo " ✅" || echo "⚠️  API antwortet nicht (API Keys konfigurieren!)"
echo ""
echo "Frontend Test:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost/
echo ""
HEALTH_EOF
chmod +x /root/apebrain-health.sh

# Update Script
cat > /root/apebrain-update.sh << 'UPDATE_EOF'
#!/bin/bash
echo "🔄 ApeBrain Update..."
cd /var/www/apebrain
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ../frontend
yarn install
yarn build
pm2 restart apebrain-backend
systemctl reload nginx
echo "✅ Update abgeschlossen!"
UPDATE_EOF
chmod +x /root/apebrain-update.sh

# Logs Script
cat > /root/apebrain-logs.sh << 'LOGS_EOF'
#!/bin/bash
echo "📋 ApeBrain Logs"
echo ""
echo "=== Backend Logs (PM2) ==="
pm2 logs apebrain-backend --lines 50 --nostream
echo ""
echo "=== Nginx Error Log ==="
tail -30 /var/log/nginx/error.log
LOGS_EOF
chmod +x /root/apebrain-logs.sh

echo -e "${GREEN}✅ Helper Scripts erstellt:${NC}"
echo "  - /root/apebrain-health.sh"
echo "  - /root/apebrain-update.sh"
echo "  - /root/apebrain-logs.sh"

#############################################
# 14. SSL INFO (KEINE INTERACTIVE PROMPTS!)
#############################################
echo ""
echo -e "${YELLOW}🔒 SSL-Zertifikat Setup:${NC}"
echo "Nach DNS-Konfiguration ausführen:"
echo "  certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
echo ""

#############################################
# 15. ABSCHLUSS
#############################################
echo ""
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════╗"
echo "║   ✅ SETUP ERFOLGREICH ABGESCHLOSSEN!    ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${GREEN}🌐 Ihre Website:${NC} http://$(curl -s ifconfig.me) (IP)"
echo -e "${GREEN}🌐 Nach DNS:${NC} https://${DOMAIN}"
echo ""
echo -e "${YELLOW}📋 Wichtige nächste Schritte:${NC}"
echo ""
echo "1. API Keys konfigurieren (PFLICHT!):"
echo "   nano ${APP_DIR}/backend/.env"
echo "   Mindestens: GEMINI_API_KEY, PEXELS_API_KEY, ADMIN_PASSWORD"
echo ""
echo "2. Backend neu starten:"
echo "   pm2 restart apebrain-backend"
echo ""
echo "3. Health Check:"
echo "   /root/apebrain-health.sh"
echo ""
echo "4. DNS A-Records konfigurieren:"
echo "   @ → $(curl -s ifconfig.me)"
echo "   www → $(curl -s ifconfig.me)"
echo ""
echo "5. SSL einrichten (nach DNS):"
echo "   certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
echo ""
echo -e "${YELLOW}📚 Nützliche Befehle:${NC}"
echo "   pm2 status              - Backend Status"
echo "   pm2 logs apebrain-backend - Backend Logs"
echo "   /root/apebrain-health.sh - System Health"
echo "   /root/apebrain-update.sh - App Update"
echo "   /root/apebrain-logs.sh   - Alle Logs"
echo ""
echo -e "${GREEN}🎉 Viel Erfolg mit APEBRAIN.CLOUD! 🍄🧠${NC}"
echo ""
