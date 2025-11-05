#!/bin/bash
# ============================================
# APEBRAIN.CLOUD - Ubuntu 24.04 Server Setup
# Hostinger VPS Installation Script
# ============================================

set -e  # Exit on error

echo "🚀 Starting APEBRAIN server setup..."

# ============================================
# 1. SYSTEM UPDATE & BASIC TOOLS
# ============================================
echo "📦 Updating system packages..."
apt update && apt upgrade -y
apt install -y curl wget git ufw fail2ban htop vim nano software-properties-common

# ============================================
# 2. FIREWALL SETUP
# ============================================
echo "🔥 Configuring firewall..."
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# ============================================
# 3. INSTALL NODE.JS (v20.x LTS)
# ============================================
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Install Yarn
npm install -g yarn

# Verify installation
node --version
npm --version
yarn --version

# ============================================
# 4. INSTALL PYTHON 3.12
# ============================================
echo "🐍 Installing Python 3.12..."
apt install -y python3 python3-pip python3-venv python3-dev build-essential

# Verify installation
python3 --version
pip3 --version

# ============================================
# 5. INSTALL MONGODB
# ============================================
echo "🍃 Installing MongoDB..."
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
apt update
apt install -y mongodb-org

# Start and enable MongoDB
systemctl start mongod
systemctl enable mongod
systemctl status mongod

# ============================================
# 6. INSTALL NGINX
# ============================================
echo "🌐 Installing Nginx..."
apt install -y nginx

# ============================================
# 7. INSTALL CERTBOT (Let's Encrypt SSL)
# ============================================
echo "🔒 Installing Certbot for SSL..."
apt install -y certbot python3-certbot-nginx

# ============================================
# 8. INSTALL PM2 (Process Manager)
# ============================================
echo "⚙️ Installing PM2..."
npm install -g pm2

# ============================================
# 9. CREATE APPLICATION DIRECTORY
# ============================================
echo "📁 Creating application directory..."
mkdir -p /var/www/apebrain
cd /var/www/apebrain

# ============================================
# 10. SETUP DONE
# ============================================
echo "✅ Basic server setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Clone your GitHub repository"
echo "2. Configure DNS settings"
echo "3. Setup SSL certificate"
echo "4. Deploy the application"
echo ""
echo "Run the deployment script next!"
