#!/bin/bash
#############################################
# APEBRAIN.CLOUD - Deployment Script
# Deployed die App von GitHub
#############################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 APEBRAIN.CLOUD Deployment${NC}"

# Konfiguration
GITHUB_REPO="robinzi2001-cell/apebrain.cloud"
DOMAIN="apebrain.cloud"
APP_DIR="/var/www/apebrain"
BACKEND_PORT=8001

# Domain überschreiben falls angegeben
if [ ! -z "$1" ]; then
    DOMAIN=$1
fi

echo -e "${GREEN}Domain: ${DOMAIN}${NC}"

#############################################
# 1. REPOSITORY KLONEN/UPDATEN
#############################################
echo -e "${GREEN}📥 Repository wird aktualisiert...${NC}"

if [ -d "${APP_DIR}/.git" ]; then
    echo "Repository existiert, ziehe Updates..."
    cd ${APP_DIR}
    git pull origin main || git pull origin master
else
    echo "Klone Repository..."
    rm -rf ${APP_DIR}
    mkdir -p ${APP_DIR}
    cd ${APP_DIR}
    git clone https://github.com/${GITHUB_REPO}.git .
fi

#############################################
# 2. BACKEND SETUP
#############################################
echo -e "${GREEN}🐍 Backend wird eingerichtet...${NC}"
cd ${APP_DIR}/backend

# Virtual Environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# .env erstellen falls nicht vorhanden
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env nicht gefunden, erstelle Template...${NC}"
    cat > .env << EOF
MONGO_URL="mongodb://localhost:27017"
DB_NAME="apebrain_blog"
CORS_ORIGINS="https://${DOMAIN},https://www.${DOMAIN}"
FRONTEND_URL="https://${DOMAIN}"
JWT_SECRET_KEY="$(openssl rand -hex 32)"

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
    echo -e "${YELLOW}⚠️  Bitte bearbeiten Sie ${APP_DIR}/backend/.env${NC}"
fi

deactivate
echo -e "${GREEN}✅ Backend konfiguriert${NC}"

#############################################
# 3. FRONTEND SETUP
#############################################
echo -e "${GREEN}⚛️  Frontend wird eingerichtet...${NC}"
cd ${APP_DIR}/frontend

yarn install

# .env erstellen/updaten
cat > .env << EOF
REACT_APP_BACKEND_URL=https://${DOMAIN}
EOF

# Build
echo -e "${GREEN}🏗️  Frontend wird gebaut...${NC}"
yarn build

echo -e "${GREEN}✅ Frontend gebaut${NC}"

#############################################
# 4. NGINX KONFIGURIEREN
#############################################
echo -e "${GREEN}🌐 Nginx wird konfiguriert...${NC}"

cat > /etc/nginx/sites-available/apebrain << EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    root ${APP_DIR}/frontend/build;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

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

    location /static {
        alias ${APP_DIR}/frontend/build/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

ln -sf /etc/nginx/sites-available/apebrain /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t && systemctl reload nginx

echo -e "${GREEN}✅ Nginx konfiguriert${NC}"

#############################################
# 5. PM2 BACKEND STARTEN/RESTARTEN
#############################################
echo -e "${GREEN}⚙️  Backend wird gestartet...${NC}"
cd ${APP_DIR}/backend

# Ecosystem File
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
    max_memory_restart: '1G'
  }]
};
EOF

pm2 delete apebrain-backend 2>/dev/null || true
pm2 start ecosystem.config.js
pm2 save

echo -e "${GREEN}✅ Backend gestartet${NC}"

#############################################
# ABSCHLUSS
#############################################
echo ""
echo -e "${GREEN}✅ DEPLOYMENT ERFOLGREICH!${NC}"
echo ""
echo -e "🌐 Website: https://${DOMAIN}"
echo ""
echo "Status prüfen:"
echo "  pm2 status"
echo "  pm2 logs apebrain-backend"
echo ""
