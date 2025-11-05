# 🍄🧠 APEBRAIN.CLOUD - Stoned Ape Theory Platform

> Eine Full-Stack-Webanwendung rund um die Stoned Ape Theory, Bewusstsein und Mykologie.

## 📋 Übersicht

APEBRAIN.CLOUD ist eine moderne Web-Plattform mit:
- **Knowledge Portal** - AI-generierte Blog-Artikel über Bewusstsein, Mykologie und Evolution
- **Sacred Shop** - E-Commerce-Shop mit PayPal-Integration
- **Admin-Dashboard** - Vollständiges CMS für Blogs, Produkte, Bestellungen und Coupons
- **User Authentication** - Email/Passwort und Google OAuth Login

## 🛠️ Tech Stack

### Backend
- **FastAPI** (Python 3.12) - REST API
- **MongoDB** - Datenbank
- **PyJWT** - Authentifizierung
- **PayPal SDK** - Zahlungsabwicklung
- **Emergent Integrations** - AI-Integrationen (Gemini)
- **SMTP** - Email-Benachrichtigungen

### Frontend
- **React** (Create React App)
- **Tailwind CSS** - Styling
- **Shadcn UI** - UI-Komponenten
- **React Router** - Navigation
- **Axios** - HTTP-Client

### Deployment
- **Nginx** - Reverse Proxy & Static File Server
- **PM2** - Process Manager für Backend
- **Certbot** - SSL/TLS-Zertifikate (Let's Encrypt)
- **UFW** - Firewall

## 🚀 Schnellstart - Hostinger VPS Deployment

### Voraussetzungen

1. **Hostinger VPS** mit Ubuntu 24.04
2. **Domain** (z.B. apebrain.cloud) mit DNS A-Records:
   - `@` → Server-IP
   - `www` → Server-IP
3. **GitHub Repository** mit diesem Code
4. **API Keys** (siehe unten)

### 1-Schritt Installation

```bash
# SSH zum Server verbinden
ssh root@YOUR_SERVER_IP

# Setup-Script herunterladen und ausführen
wget -O setup.sh https://raw.githubusercontent.com/robinzi2001-cell/apebrain.cloud/main/setup-server.sh
chmod +x setup.sh
./setup.sh
```

**Das war's!** 🎉

Das Script installiert automatisch:
- Node.js, Python, MongoDB, Nginx, Certbot, PM2
- Klont das Repository
- Installiert alle Dependencies
- Konfiguriert Services
- Richtet SSL ein

### Manuelle Installation

Für eine detaillierte Schritt-für-Schritt-Anleitung siehe [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

## 🔑 Benötigte API Keys

Erstellen Sie eine `.env` Datei im `backend/` Ordner:

```bash
# MongoDB
MONGO_URL="mongodb://localhost:27017"
DB_NAME="apebrain_blog"

# Security
JWT_SECRET_KEY="your-random-secret-key-here"
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
FRONTEND_URL="https://yourdomain.com"

# AI Integration
GEMINI_API_KEY="your-gemini-api-key"  # https://makersuite.google.com/app/apikey
EMERGENT_LLM_KEY="your-emergent-key"   # Optional

# Images
PEXELS_API_KEY="your-pexels-key"  # https://www.pexels.com/api/

# Admin Credentials
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="your-secure-password"

# PayPal (Sandbox oder Live)
PAYPAL_MODE="sandbox"  # oder "live"
PAYPAL_CLIENT_ID="your-paypal-client-id"
PAYPAL_CLIENT_SECRET="your-paypal-secret"

# Email (Gmail)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"  # Gmail App-Passwort!
NOTIFICATION_EMAIL="your-email@gmail.com"

# Google OAuth
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-secret"
```

## 📁 Projektstruktur

```
apebrain.cloud/
├── backend/
│   ├── server.py              # Haupt-API-Server
│   ├── auth_endpoints.py      # Auth-Endpunkte (Referenz)
│   ├── requirements.txt       # Python-Dependencies
│   ├── .env                   # Umgebungsvariablen (nicht im Git!)
│   └── .env.example          # Beispiel-Konfiguration
├── frontend/
│   ├── src/
│   │   ├── App.js            # Haupt-App-Komponente
│   │   ├── index.js          # Entry Point
│   │   ├── components/       # Wiederverwendbare Komponenten
│   │   └── pages/            # Seiten-Komponenten
│   ├── public/
│   ├── package.json          # Node.js-Dependencies
│   ├── .env                  # Frontend-Konfiguration
│   └── .env.example         # Beispiel-Konfiguration
├── setup-server.sh           # Server-Setup-Script
├── deploy-app.sh             # Deployment-Script
├── update-app.sh             # Update-Script
├── DEPLOYMENT_GUIDE.md       # Ausführliche Anleitung
├── TROUBLESHOOTING.md        # Fehlerbehebung
└── README.md                 # Diese Datei
```

## 🔧 Lokale Entwicklung

### Backend starten

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --reload --port 8001
```

Backend läuft auf: http://localhost:8001

### Frontend starten

```bash
cd frontend
yarn install
yarn start
```

Frontend läuft auf: http://localhost:3000

## 📚 API-Dokumentation

Nach dem Start des Backends ist die interaktive API-Dokumentation verfügbar:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### Wichtige Endpoints

#### Authentication
- `POST /api/auth/register` - Neuen User registrieren
- `POST /api/auth/login` - User-Login
- `POST /api/auth/google/verify` - Google OAuth
- `POST /api/admin/login` - Admin-Login

#### Blogs
- `GET /api/blogs/public` - Alle öffentlichen Blogs
- `GET /api/blogs/{blog_id}` - Einzelner Blog
- `POST /api/blogs/generate` - AI-Blog generieren (Admin)
- `PUT /api/blogs/{blog_id}` - Blog bearbeiten (Admin)

#### Shop
- `GET /api/products` - Alle Produkte
- `POST /api/shop/create-order` - PayPal-Bestellung erstellen
- `GET /api/orders` - Bestellungen abrufen (Admin)

#### Admin
- `GET /api/admin/stats` - Dashboard-Statistiken
- `GET /api/coupons` - Alle Coupons
- `POST /api/coupons` - Neuen Coupon erstellen

## 🎨 Design-System

### Farben
- **Primary**: Fliegenpilz-Rot (#dc2626, #ef4444)
- **Background**: Dunkle mystische Töne (#0a0a0a, #1a1a1a)
- **Accent**: Rosa/Pink Glows (#ec4899, #f43f5e)
- **Text**: Warme Weißtöne (#f5f5f5, #e5e5e5)

### Typografie
- **Headings**: 'Playfair Display' (Serif)
- **Body**: 'Inter', sans-serif
- **Mono**: 'Courier New', monospace

## 🔐 Sicherheit

### Best Practices (implementiert)
- ✅ JWT-basierte Authentifizierung
- ✅ Bcrypt Passwort-Hashing
- ✅ CORS-Konfiguration
- ✅ Environment Variables für Secrets
- ✅ HTTPS via Let's Encrypt
- ✅ UFW Firewall
- ✅ Fail2Ban gegen Brute-Force

### Empfohlene Maßnahmen
- [ ] SSH Key Authentication (statt Passwort)
- [ ] Rate Limiting für API-Endpoints
- [ ] Input Validation & Sanitization
- [ ] CSP Headers
- [ ] Regular Security Updates

## 📊 Monitoring & Logs

### Backend Logs
```bash
pm2 logs apebrain-backend
pm2 monit  # Live-Monitoring
```

### Nginx Logs
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### MongoDB Logs
```bash
tail -f /var/log/mongodb/mongod.log
```

### System Status
```bash
htop              # CPU, RAM, Prozesse
df -h             # Disk Space
systemctl status nginx
systemctl status mongod
pm2 status
```

## 🔄 Updates deployen

### Automatisch (via Script)
```bash
cd /var/www/apebrain
./update-app.sh
```

### Manuell
```bash
cd /var/www/apebrain
git pull origin main

# Backend updaten
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
pm2 restart apebrain-backend

# Frontend updaten
cd ../frontend
yarn install
yarn build
systemctl reload nginx
```

## 🆘 Hilfe & Troubleshooting

Bei Problemen:
1. Siehe [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
2. Logs überprüfen (siehe oben)
3. Services neu starten:
   ```bash
   pm2 restart apebrain-backend
   systemctl restart nginx
   systemctl restart mongod
   ```

## 📝 Features

### ✅ Implementiert
- [x] AI-Blog-Generierung (Gemini)
- [x] Admin-Panel (CRUD für Blogs/Produkte/Coupons)
- [x] E-Commerce mit PayPal
- [x] Shopping Cart
- [x] Coupon-System
- [x] User Authentication (Email + Google OAuth)
- [x] Order Management mit Email-Benachrichtigungen
- [x] Image Upload
- [x] SEO (Meta Tags, Sitemap, Robots.txt)
- [x] Responsive Design
- [x] Dark Theme (Stoned Ape Theory Design)

### 🚧 Geplant
- [ ] Instagram-Integration (Auto-Posting)
- [ ] Mini-Games Section
- [ ] PayPal OAuth Login
- [ ] Newsletter-System
- [ ] Blog-Kommentare
- [ ] Produktbewertungen
- [ ] Multi-Language Support

## 👥 Mitwirken

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## 📄 Lizenz

Dieses Projekt ist privat und proprietär.

## 📧 Kontakt

Bei Fragen: apebrain333@gmail.com

## 🙏 Credits

- **Terence McKenna** - Inspiration und Stoned Ape Theory
- **Emergent AI** - Entwicklungsplattform
- **Pexels** - Kostenlose Bilder
- **FastAPI** - Backend Framework
- **React** - Frontend Framework

---

**Made with 🍄 and 🧠**

*"What expanded primate minds can restore yours."*