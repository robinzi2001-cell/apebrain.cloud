#!/bin/bash
#############################################
# APEBRAIN.CLOUD - Automatisches Server Setup
# Ubuntu 24.04 LTS - Hostinger VPS
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

# Domain abfragen
echo -e "${YELLOW}Bitte geben Sie Ihre Domain ein (z.B. apebrain.cloud):${NC}"
read -p "Domain: " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}❌ Fehler: Domain erforderlich!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Domain: $DOMAIN${NC}"
echo ""

#############################################
# 1. SYSTEM UPDATE
#############################################
echo -e "${GREEN}📦 System wird aktualisiert...${NC}"
apt update && apt upgrade -y
apt install -y curl wget git ufw fail2ban htop vim nano software-properties-common

#############################################
# 2. FIREWALL SETUP
#############################################
echo -e "${GREEN}🔥 Firewall wird konfiguriert...${NC}"
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
echo -e "${GREEN}✅ Firewall aktiv${NC}"

#############################################
# 3. NODE.JS & YARN INSTALLIEREN
#############################################
echo -e "${GREEN}📦 Node.js 20.x wird installiert...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
npm install -g yarn

echo "Node.js Version: $(node --version)"
echo "NPM Version: $(npm --version)"
echo "Yarn Version: $(yarn --version)"
echo -e "${GREEN}✅ Node.js installiert${NC}"

#############################################
# 4. PYTHON 3.12 INSTALLIEREN
#############################################
echo -e "${GREEN}🐍 Python 3.12 wird installiert...${NC}"
apt install -y python3 python3-pip python3-venv python3-dev build-essential

echo "Python Version: $(python3 --version)"
echo "Pip Version: $(pip3 --version)"
echo -e "${GREEN}✅ Python installiert${NC}"

#############################################
# 5. MONGODB 7.0 INSTALLIEREN
#############################################
echo -e "${GREEN}🍃 MongoDB 7.0 wird installiert...${NC}"
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
    exit 1
fi

#############################################
# 6. NGINX INSTALLIEREN
#############################################
echo -e "${GREEN}🌐 Nginx wird installiert...${NC}"
apt install -y nginx

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
apt install -y certbot python3-certbot-nginx
echo -e "${GREEN}✅ Certbot installiert${NC}"

#############################################
# 8. PM2 INSTALLIEREN
#############################################
echo -e "${GREEN}⚙️  PM2 wird installiert...${NC}"
npm install -g pm2
echo "PM2 Version: $(pm2 --version)"
echo -e "${GREEN}✅ PM2 installiert${NC}"

#############################################
# 9. APPLICATION DEPLOYEN
#############################################
echo -e "${GREEN}📥 GitHub Repository wird geklont...${NC}"

# Verzeichnis erstellen und bereinigen
rm -rf ${APP_DIR}
mkdir -p ${APP_DIR}
cd ${APP_DIR}

# Repository klonen
git clone https://github.com/${GITHUB_REPO}.git .

if [ ! -f "${APP_DIR}/backend/server.py" ]; then
    echo -e "${RED}❌ Repository-Klonen fehlgeschlagen oder falsche Struktur${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Repository geklont${NC}"

#############################################
# 10. BACKEND SETUP
#############################################
echo -e "${GREEN}🐍 Backend wird eingerichtet...${NC}"
cd ${APP_DIR}/backend

# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install --upgrade pip
pip install -r requirements.txt

# .env Datei erstellen (mit Platzhaltern)
cat > .env << EOF
MONGO_URL="mongodb://localhost:27017"
DB_NAME="apebrain_blog"
CORS_ORIGINS="https://${DOMAIN},https://www.${DOMAIN}"
FRONTEND_URL="https://${DOMAIN}"
JWT_SECRET_KEY="$(openssl rand -hex 32)"

# ⚠️ WICHTIG: Ersetzen Sie diese Platzhalter mit echten Werten!
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
EMERGENT_LLM_KEY="YOUR_EMERGENT_LLM_KEY"
PEXELS_API_KEY="YOUR_PEXELS_API_KEY"

ADMIN_USERNAME="admin"
ADMIN_PASSWORD="CHANGE_THIS_PASSWORD"

PAYPAL_MODE="sandbox"
PAYPAL_CLIENT_ID="YOUR_PAYPAL_CLIENT_ID"
PAYPAL_CLIENT_SECRET="YOUR_PAYPAL_CLIENT_SECRET"

SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="YOUR_EMAIL@gmail.com"
SMTP_PASSWORD="YOUR_GMAIL_APP_PASSWORD"
NOTIFICATION_EMAIL="YOUR_EMAIL@gmail.com"

GOOGLE_CLIENT_ID="YOUR_GOOGLE_CLIENT_ID"
GOOGLE_CLIENT_SECRET="YOUR_GOOGLE_CLIENT_SECRET"
EOF

deactivate
echo -e "${GREEN}✅ Backend konfiguriert${NC}"
echo -e "${YELLOW}⚠️  WICHTIG: Bearbeiten Sie ${APP_DIR}/backend/.env mit Ihren API Keys!${NC}"

#############################################
# 11. FRONTEND SETUP
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
echo -e "${GREEN}🏗️  Frontend wird gebaut (dauert 3-5 Min)...${NC}"
yarn build

if [ ! -d "${APP_DIR}/frontend/build" ]; then
    echo -e "${RED}❌ Frontend-Build fehlgeschlagen${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Frontend gebaut${NC}"

#############################################
# 12. NGINX KONFIGURIEREN
#############################################
echo -e "${GREEN}🌐 Nginx wird konfiguriert...${NC}"

cat > /etc/nginx/sites-available/apebrain << EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

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
# 13. PM2 BACKEND STARTEN
#############################################
echo -e "${GREEN}⚙️  Backend wird mit PM2 gestartet...${NC}"
cd ${APP_DIR}/backend

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

# Alten Process stoppen (falls vorhanden)
pm2 delete apebrain-backend 2>/dev/null || true

# Backend starten
pm2 start ecosystem.config.js
pm2 save

# PM2 beim Systemstart starten
pm2 startup systemd -u root --hp /root

echo -e "${GREEN}✅ Backend läuft${NC}"

#############################################
# 14. SSL EINRICHTEN
#############################################
echo -e "${GREEN}🔒 SSL-Zertifikat wird eingerichtet...${NC}"
echo -e "${YELLOW}Stellen Sie sicher, dass Ihre DNS-Records auf diesen Server zeigen!${NC}"
echo ""

read -p "Möchten Sie jetzt SSL einrichten? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos --register-unsafely-without-email
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ SSL erfolgreich eingerichtet${NC}"
    else
        echo -e "${YELLOW}⚠️  SSL-Setup fehlgeschlagen. Versuchen Sie es später manuell:${NC}"
        echo "certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
    fi
else
    echo -e "${YELLOW}⚠️  SSL übersprungen. Führen Sie später aus:${NC}"
    echo "certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
fi

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
echo -e "${GREEN}🌐 Ihre Website:${NC} https://${DOMAIN}"
echo ""
echo -e "${YELLOW}📋 Wichtige nächste Schritte:${NC}"
echo "1. API Keys konfigurieren:"
echo "   nano ${APP_DIR}/backend/.env"
echo ""
echo "2. Backend neu starten nach .env Änderungen:"
echo "   pm2 restart apebrain-backend"
echo ""
echo "3. Status prüfen:"
echo "   pm2 status"
echo "   systemctl status nginx"
echo "   systemctl status mongod"
echo ""
echo "4. Logs anzeigen:"
echo "   pm2 logs apebrain-backend"
echo ""
echo -e "${GREEN}🎉 Viel Erfolg mit APEBRAIN.CLOUD! 🍄🧠${NC}"
echo ""
