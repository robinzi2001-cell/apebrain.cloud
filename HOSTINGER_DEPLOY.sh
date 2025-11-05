#!/bin/bash
# ============================================
# APEBRAIN.CLOUD - Deployment Script
# Deploy from GitHub to Hostinger VPS
# ============================================

set -e  # Exit on error

# ============================================
# CONFIGURATION VARIABLES
# ============================================
GITHUB_REPO="YOUR_GITHUB_USERNAME/YOUR_REPO_NAME"  # ⚠️ CHANGE THIS!
DOMAIN="apebrain.cloud"  # ⚠️ CHANGE THIS to your domain!
APP_DIR="/var/www/apebrain"
BACKEND_PORT=8001
FRONTEND_PORT=3000

echo "🚀 Starting APEBRAIN deployment..."

# ============================================
# 1. CLONE GITHUB REPOSITORY
# ============================================
echo "📥 Cloning GitHub repository..."
cd /var/www/apebrain

# If directory exists and has content, pull latest
if [ -d ".git" ]; then
    echo "Repository exists, pulling latest changes..."
    git pull origin main
else
    echo "Cloning repository..."
    git clone https://github.com/${GITHUB_REPO}.git .
fi

# ============================================
# 2. BACKEND SETUP
# ============================================
echo "🐍 Setting up backend..."
cd ${APP_DIR}/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
MONGO_URL="mongodb://localhost:27017"
DB_NAME="apebrain_blog"
CORS_ORIGINS="https://${DOMAIN},https://www.${DOMAIN}"
FRONTEND_URL="https://${DOMAIN}"
JWT_SECRET_KEY="$(openssl rand -hex 32)"

# ⚠️ ADD YOUR API KEYS HERE:
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
EMERGENT_LLM_KEY="YOUR_EMERGENT_LLM_KEY"
PEXELS_API_KEY="YOUR_PEXELS_API_KEY"

# Admin credentials
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="YOUR_SECURE_PASSWORD"

# PayPal (Sandbox or Live)
PAYPAL_MODE="sandbox"
PAYPAL_CLIENT_ID="YOUR_PAYPAL_CLIENT_ID"
PAYPAL_CLIENT_SECRET="YOUR_PAYPAL_CLIENT_SECRET"

# SMTP Email
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="YOUR_EMAIL@gmail.com"
SMTP_PASSWORD="YOUR_APP_PASSWORD"
NOTIFICATION_EMAIL="YOUR_EMAIL@gmail.com"

# Google OAuth
GOOGLE_CLIENT_ID="YOUR_GOOGLE_CLIENT_ID"
GOOGLE_CLIENT_SECRET="YOUR_GOOGLE_CLIENT_SECRET"
EOF

echo "⚠️  IMPORTANT: Edit /var/www/apebrain/backend/.env and add your API keys!"

deactivate

# ============================================
# 3. FRONTEND SETUP
# ============================================
echo "⚛️ Setting up frontend..."
cd ${APP_DIR}/frontend

# Install dependencies
yarn install

# Create .env file
cat > .env << EOF
REACT_APP_BACKEND_URL=https://${DOMAIN}
EOF

# Build production version
echo "🏗️ Building frontend..."
yarn build

# ============================================
# 4. NGINX CONFIGURATION
# ============================================
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/apebrain << EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    # Redirect to HTTPS (will be enabled after SSL setup)
    # return 301 https://\$server_name\$request_uri;

    # Frontend - React build
    root ${APP_DIR}/frontend/build;
    index index.html;

    # Handle React Router
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API - FastAPI
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

    # Static files
    location /static {
        alias ${APP_DIR}/frontend/build/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/apebrain /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

# Reload nginx
systemctl reload nginx

# ============================================
# 5. PM2 SETUP - Backend Process
# ============================================
echo "⚙️ Setting up PM2 for backend..."
cd ${APP_DIR}/backend

cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'apebrain-backend',
    script: 'venv/bin/uvicorn',
    args: 'server:app --host 0.0.0.0 --port ${BACKEND_PORT}',
    cwd: '${APP_DIR}/backend',
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

# Stop existing process if any
pm2 delete apebrain-backend || true

# Start backend with PM2
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup systemd -u root --hp /root

echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Configure DNS A record: ${DOMAIN} -> 72.61.177.155"
echo "2. Edit backend/.env and add your API keys"
echo "3. Run SSL setup: certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
echo "4. Restart services: pm2 restart all && systemctl reload nginx"
echo ""
echo "🌐 Your site will be available at: http://${DOMAIN}"
