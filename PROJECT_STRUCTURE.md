# 🍄 APEBRAIN.CLOUD - Projektstruktur

## 📁 Verzeichnisstruktur

```
apebrain.cloud/
├── backend/                    # FastAPI Backend
│   ├── server.py              # Haupt-API-Server (alle Endpoints)
│   ├── requirements.txt       # Python Dependencies
│   ├── .env.example          # Beispiel-Konfiguration
│   └── venv/                 # Virtual Environment (nicht in Git)
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── App.js            # Haupt-App mit Routing
│   │   ├── index.js          # Entry Point
│   │   ├── index.css         # Globale Styles
│   │   ├── App.css           # App-spezifische Styles
│   │   ├── components/       # Wiederverwendbare Komponenten
│   │   │   ├── ui/           # UI-Komponenten (Shadcn)
│   │   │   ├── Footer.js
│   │   │   ├── FloatingCoupon.js
│   │   │   └── UserDropdown.js
│   │   ├── pages/            # Seiten-Komponenten
│   │   │   ├── LandingPage.js
│   │   │   ├── BlogHomePage.js
│   │   │   ├── BlogPage.js
│   │   │   ├── ShopPage.js
│   │   │   ├── Login.js
│   │   │   ├── Register.js
│   │   │   ├── Dashboard.js
│   │   │   ├── AdminLogin.js
│   │   │   ├── AdminDashboard.js
│   │   │   ├── AdminProducts.js
│   │   │   ├── AdminCoupons.js
│   │   │   ├── AdminOrders.js
│   │   │   ├── AdminSettings.js
│   │   │   ├── CreateBlog.js
│   │   │   ├── EditBlog.js
│   │   │   ├── PaymentSuccess.js
│   │   │   ├── PaymentCancel.js
│   │   │   ├── Impressum.js
│   │   │   ├── Privacy.js
│   │   │   └── Terms.js
│   │   └── hooks/
│   │       └── use-toast.js
│   ├── public/
│   │   ├── index.html
│   │   ├── manifest.json
│   │   ├── robots.txt
│   │   └── sitemap.xml
│   ├── package.json          # Node.js Dependencies
│   ├── tailwind.config.js    # Tailwind CSS Konfiguration
│   ├── .env.example         # Beispiel-Konfiguration
│   └── build/               # Production Build (nicht in Git)
│
├── ULTIMATE-SETUP.sh         # 1-Command Setup für Server
├── setup-server.sh           # Server-Basisinstallation
├── deploy-app.sh             # App-Deployment
├── update-app.sh             # App-Updates
│
├── README.md                 # Hauptdokumentation
├── DEPLOYMENT_GUIDE.md       # Deployment-Anleitung
├── SCHNELLSTART-ANLEITUNG.md # Schnellstart-Guide
├── TROUBLESHOOTING.md        # Fehlerbehebung
│
├── .gitignore               # Git Ignore-Regeln
└── PROJECT_STRUCTURE.md     # Diese Datei
```

## 📄 Wichtige Dateien

### Backend
- **server.py** (3,700+ Zeilen)
  - Alle API-Endpoints
  - Blog CRUD, Produkte, Coupons, Bestellungen
  - PayPal Integration
  - Email-Benachrichtigungen
  - User & Admin Authentifizierung

- **requirements.txt**
  - FastAPI, Uvicorn
  - MongoDB (motor)
  - PayPal SDK
  - Emergent Integrations (AI)
  - SMTP, JWT, Google Auth

### Frontend
- **App.js** - React Router Setup
- **LandingPage.js** - Stoned Ape Theory Design
- **BlogHomePage.js** - Knowledge Portal
- **ShopPage.js** - Sacred Shop mit Warenkorb
- **Admin*.js** - Admin-Panel Seiten

### Deployment
- **ULTIMATE-SETUP.sh** - Komplettes automatisches Setup
- **setup-server.sh** - Server-Grundinstallation
- **deploy-app.sh** - App-Deployment von GitHub
- **update-app.sh** - Einfache Updates

### Dokumentation
- **README.md** - Projekt-Übersicht, Features, Tech Stack
- **DEPLOYMENT_GUIDE.md** - Detaillierte Deployment-Anleitung
- **SCHNELLSTART-ANLEITUNG.md** - 3-Schritte Quickstart
- **TROUBLESHOOTING.md** - Problemlösungen

## 🔧 Konfigurationsdateien

### Backend (.env)
```env
MONGO_URL=mongodb://localhost:27017
GEMINI_API_KEY=...
PEXELS_API_KEY=...
PAYPAL_CLIENT_ID=...
ADMIN_USERNAME=admin
ADMIN_PASSWORD=...
# etc.
```

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=https://yourdomain.com
```

## 🚫 Nicht in Git

Diese Ordner/Dateien sind in `.gitignore`:
- `node_modules/` - Node.js Dependencies
- `venv/` - Python Virtual Environment
- `backend/.env` - Sensitive Daten
- `frontend/.env` - API URLs
- `frontend/build/` - Production Build
- `__pycache__/` - Python Cache
- `*.log` - Log-Dateien

## 📊 Statistiken

- **Backend:** 1 Hauptdatei (server.py)
- **Frontend:** ~25 Komponenten/Pages
- **Dependencies:** 
  - Backend: ~20 Packages
  - Frontend: ~30 Packages
- **API Endpoints:** ~60+
- **Lines of Code:** ~7,000+

## 🎯 Clean & Minimal

Das Repository enthält nur:
✅ Produktionscode
✅ Deployment-Scripts
✅ Dokumentation
✅ Konfigurationsbeispiele

❌ Keine Test-Dateien
❌ Keine alten/doppelten Dateien
❌ Keine Build-Artefakte
❌ Keine Secrets
