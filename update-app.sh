#!/bin/bash
#############################################
# APEBRAIN.CLOUD - Update Script
# Pulled Updates von GitHub und deployed
#############################################

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔄 APEBRAIN.CLOUD Update${NC}"

APP_DIR="/var/www/apebrain"

cd ${APP_DIR}

# Git Updates ziehen
echo -e "${GREEN}📥 Pulling latest changes...${NC}"
git pull origin main || git pull origin master

# Backend updaten
echo -e "${GREEN}🐍 Updating backend...${NC}"
cd ${APP_DIR}/backend
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Frontend updaten
echo -e "${GREEN}⚛️  Updating frontend...${NC}"
cd ${APP_DIR}/frontend
yarn install
yarn build

# Services neu starten
echo -e "${GREEN}🔄 Restarting services...${NC}"
pm2 restart apebrain-backend
systemctl reload nginx

echo ""
echo -e "${GREEN}✅ UPDATE ERFOLGREICH!${NC}"
echo ""
echo "Status:"
pm2 status
echo ""
