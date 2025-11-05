#!/bin/bash
#############################################
# APEBRAIN.CLOUD - ULTIMATE 1-COMMAND SETUP
# Vollautomatisches Setup für Ubuntu 24.04
# Optimiert für Hostinger VPS
# GitHub-Safe: Keine API Keys im Script!
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
║   Stoned Ape Theory Design             ║
║   Vollautomatische Installation         ║
╚══════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Konfiguration - ANPASSEN!
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
apt install -y curl wget git ufw fail2ban htop vim nano software-properties-common jq net-tools build-essential

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
# SCHRITT 3: NODE.JS 20 & YARN
#############################################
echo -e "${GREEN}[3/12] Node.js 20 & Yarn werden installiert...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
npm install -g yarn@1.22.22 pm2

echo -e "${BLUE}Node.js: $(node --version)${NC}"
echo -e "${BLUE}NPM: $(npm --version)${NC}"
echo -e "${BLUE}Yarn: $(yarn --version)${NC}"
echo -e "${BLUE}PM2: $(pm2 --version)${NC}"

#############################################
# SCHRITT 4: PYTHON 3.12
#############################################
echo -e "${GREEN}[4/12] Python 3.12 wird installiert...${NC}"
apt install -y python3 python3-pip python3-venv python3-dev

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

# WICHTIG: emergentintegrations mit speziellem Index installieren
echo -e "${YELLOW}[INFO] Installiere emergentintegrations...${NC}"
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ || {
    echo -e "${YELLOW}⚠️  emergentintegrations Installation fehlgeschlagen - wird übersprungen${NC}"
}

echo -e "${YELLOW}[INFO] Installiere restliche Backend Dependencies...${NC}"
pip install -r requirements.txt

deactivate
echo -e "${GREEN}✅ Backend Dependencies installiert${NC}"

# .env Datei NICHT automatisch erstellen - User macht das später!
echo -e "${YELLOW}⚠️  .env Datei muss noch konfiguriert werden (siehe Ende)${NC}"

#############################################
# SCHRITT 10: FRONTEND SETUP
#############################################
echo -e "${GREEN}[10/12] Frontend wird eingerichtet...${NC}"
cd ${APP_DIR}/frontend

# .env für Frontend
cat > .env << EOF
REACT_APP_BACKEND_URL=https://${DOMAIN}
EOF

echo -e "${BLUE}[INFO] Installiere Frontend Dependencies (dauert 2-3 Min)...${NC}"
yarn install

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
    server_name apebrain.cloud www.apebrain.cloud;

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

    # React Router - Frontend
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
        
        # Timeouts
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Static Files Caching
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
# SCHRITT 12: PM2 SETUP (Backend noch nicht starten!)
#############################################
echo -e "${GREEN}[12/12] PM2 wird konfiguriert...${NC}"
cd ${APP_DIR}/backend

cat > ecosystem.config.js << 'EOFPM2'
module.exports = {
  apps: [{
    name: 'apebrain-backend',
    script: './venv/bin/python',
    args: '-m uvicorn server:app --host 0.0.0.0 --port 8001 --workers 2',
    cwd: '/var/www/apebrain/backend',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      PYTHONUNBUFFERED: '1'
    },
    error_file: '/var/log/apebrain-backend-error.log',
    out_file: '/var/log/apebrain-backend-out.log',
    log_file: '/var/log/apebrain-backend-combined.log',
    time: true
  }]
};
EOFPM2

echo -e "${YELLOW}⚠️  Backend wird NICHT automatisch gestartet (API Keys fehlen noch)${NC}"

#############################################
# MONITORING & DEBUG SCRIPTS ERSTELLEN
#############################################
echo -e "${GREEN}[BONUS] Erstelle Management Scripts...${NC}"

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
echo "Backend (letzte 30 Zeilen):"
pm2 logs apebrain-backend --lines 30 --nostream
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
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ || true
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

#############################################
# SSL EINRICHTEN
#############################################
echo ""
echo -e "${GREEN}[SSL] SSL-Zertifikat einrichten...${NC}"
echo -e "${YELLOW}WICHTIG: DNS muss auf diese Server-IP zeigen!${NC}"
echo -e "${YELLOW}Prüfen Sie: ping ${DOMAIN}${NC}"
echo ""

read -p "DNS korrekt konfiguriert und SSL jetzt einrichten? (y/n) " -n 1 -r
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
║   🍄🧠 APEBRAIN.CLOUD IST BEREIT!      ║
╚══════════════════════════════════════════╝
EOF
echo -e "${NC}"
echo ""
echo -e "${BLUE}📊 INSTALLIERTE KOMPONENTEN:${NC}"
echo "=================================="
echo "✅ System aktualisiert (Ubuntu 24.04)"
echo "✅ Firewall konfiguriert (UFW)"
echo "✅ Node.js 20 + Yarn installiert"
echo "✅ Python 3.12 + Virtual Environment"
echo "✅ MongoDB 7.0 installiert & läuft"
echo "✅ Nginx konfiguriert"
echo "✅ GitHub Repository geklont"
echo "✅ Backend Dependencies installiert"
echo "✅ Frontend gebaut (React 19 + Tailwind)"
echo "✅ PM2 konfiguriert"
echo ""
echo -e "${YELLOW}⚠️  WICHTIGE NÄCHSTE SCHRITTE:${NC}"
echo "=================================="
echo ""
echo -e "${RED}SCHRITT 1: API KEYS KONFIGURIEREN${NC}"
echo "-----------------------------------"
echo "Die .env Datei muss JETZT erstellt werden!"
echo ""
echo "Option A - Interaktiv (empfohlen):"
echo "  nano /var/www/apebrain/backend/.env"
echo ""
echo "Option B - Vorlage kopieren:"
echo "  cp /var/www/apebrain/backend/.env.example /var/www/apebrain/backend/.env"
echo "  nano /var/www/apebrain/backend/.env"
echo ""
echo "Benötigte API Keys:"
echo "  - GEMINI_API_KEY (https://makersuite.google.com/app/apikey)"
echo "  - PEXELS_API_KEY (https://www.pexels.com/api/)"
echo "  - PAYPAL_CLIENT_ID & SECRET (https://developer.paypal.com/)"
echo "  - SMTP_USER & PASSWORD (Gmail App Password)"
echo "  - GOOGLE_CLIENT_ID & SECRET (Google OAuth)"
echo "  - ADMIN_PASSWORD (ÄNDERN!)"
echo ""
read -p "Möchtest du JETZT die .env Datei erstellen? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${GREEN}Öffne Editor für .env Konfiguration...${NC}"
    echo -e "${YELLOW}Füge deine API Keys ein und speichere mit Strg+X, Y, Enter${NC}"
    sleep 3
    
    # Erstelle .env mit Template falls nicht vorhanden
    if [ ! -f "/var/www/apebrain/backend/.env" ]; then
        if [ -f "/var/www/apebrain/backend/.env.example" ]; then
            cp /var/www/apebrain/backend/.env.example /var/www/apebrain/backend/.env
        else
            # Fallback: Erstelle minimale .env
            cat > /var/www/apebrain/backend/.env << 'ENVEOF'
# MongoDB
MONGO_URL="mongodb://localhost:27017"
DB_NAME="apebrain_blog"

# CORS & Security
CORS_ORIGINS="*"
FRONTEND_URL="https://apebrain.cloud"
JWT_SECRET_KEY="CHANGE-THIS-SECRET-KEY"

# Admin Credentials (ÄNDERN!)
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="CHANGE-THIS-PASSWORD"

# AI Integration
GEMINI_API_KEY="YOUR-GEMINI-API-KEY-HERE"
EMERGENT_LLM_KEY="YOUR-EMERGENT-KEY-HERE-OPTIONAL"

# Pexels (Bilder)
PEXELS_API_KEY="YOUR-PEXELS-API-KEY-HERE"

# PayPal Integration
PAYPAL_MODE="sandbox"
PAYPAL_CLIENT_ID="YOUR-PAYPAL-CLIENT-ID"
PAYPAL_CLIENT_SECRET="YOUR-PAYPAL-CLIENT-SECRET"

# Email (Gmail)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="YOUR-EMAIL@gmail.com"
SMTP_PASSWORD="YOUR-GMAIL-APP-PASSWORD"
NOTIFICATION_EMAIL="YOUR-EMAIL@gmail.com"

# Google OAuth
GOOGLE_CLIENT_ID="YOUR-GOOGLE-CLIENT-ID"
GOOGLE_CLIENT_SECRET="YOUR-GOOGLE-CLIENT-SECRET"
ENVEOF
        fi
    fi
    
    nano /var/www/apebrain/backend/.env
    
    echo ""
    echo -e "${GREEN}✅ .env Datei gespeichert${NC}"
    echo ""
    echo -e "${RED}SCHRITT 2: BACKEND STARTEN${NC}"
    echo "---------------------------"
    read -p "Backend jetzt starten? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd /var/www/apebrain/backend
        pm2 start ecosystem.config.js
        pm2 save
        pm2 startup systemd -u root --hp /root
        echo ""
        echo -e "${GREEN}✅ Backend gestartet!${NC}"
        echo ""
        sleep 2
        /root/apebrain-health.sh
    else
        echo ""
        echo -e "${YELLOW}Backend später manuell starten:${NC}"
        echo "  cd /var/www/apebrain/backend"
        echo "  pm2 start ecosystem.config.js"
        echo "  pm2 save"
    fi
else
    echo ""
    echo -e "${YELLOW}⚠️  .env Datei MUSS konfiguriert werden bevor Backend startet!${NC}"
    echo ""
    echo "Führe später aus:"
    echo "  nano /var/www/apebrain/backend/.env"
    echo "  pm2 start /var/www/apebrain/backend/ecosystem.config.js"
    echo "  pm2 save"
fi

echo ""
echo -e "${GREEN}🔧 NÜTZLICHE BEFEHLE:${NC}"
echo "=================================="
echo "📊 System-Status prüfen:    /root/apebrain-health.sh"
echo "🔍 Debug-Informationen:     /root/apebrain-debug.sh"
echo "🔄 App aktualisieren:       /root/apebrain-update.sh"
echo "📝 Backend Logs:            pm2 logs apebrain-backend"
echo "📝 Nginx Logs:              tail -f /var/log/nginx/apebrain-error.log"
echo "🔄 Backend neu starten:     pm2 restart apebrain-backend"
echo "🔄 Nginx neu laden:         systemctl reload nginx"
echo "🔄 MongoDB neu starten:     systemctl restart mongod"
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
