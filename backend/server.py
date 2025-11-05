from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import asyncio
from emergentintegrations.llm.chat import LlmChat, UserMessage
import base64
import re
import paypalrestsdk
import httpx
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from passlib.context import CryptContext
from jose import JWTError, jwt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Auth Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Tracking URL generator
def generate_tracking_url(carrier: str, tracking_number: str) -> str:
    carrier_urls = {
        "DHL": f"https://www.dhl.de/de/privatkunden/pakete-empfangen/verfolgen.html?piececode={tracking_number}",
        "DPD": f"https://tracking.dpd.de/parcelstatus?query={tracking_number}&locale=de_DE",
        "Hermes": f"https://www.myhermes.de/empfangen/sendungsverfolgung/sendungsinformation/#{tracking_number}",
        "UPS": f"https://www.ups.com/track?tracknum={tracking_number}",
        "GLS": f"https://gls-group.eu/DE/de/paketverfolgung?match={tracking_number}"
    }
    return carrier_urls.get(carrier, f"https://www.google.com/search?q={carrier}+tracking+{tracking_number}")

# Email notification function
async def send_order_notification(order_data):
    try:
        smtp_host = os.environ.get('SMTP_HOST')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_user = os.environ.get('SMTP_USER')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        notification_email = os.environ.get('NOTIFICATION_EMAIL')
        
        if not all([smtp_host, smtp_user, smtp_password, notification_email]):
            logging.warning("Email configuration incomplete, skipping notification")
            return
        
        # Create email
        message = MIMEMultipart()
        message['From'] = smtp_user
        message['To'] = notification_email
        message['Subject'] = "🛍️ Neue Bestellung - apebrain.cloud"
        
        # Email body
        items_html = "<br>".join([
            f"- {item['name']} x{item['quantity']} - €{item['price'] * item['quantity']:.2f}"
            for item in order_data['items']
        ])
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #7a9053;">Neue Bestellung eingegangen!</h2>
            <p><strong>Bestellnummer:</strong> {order_data['id']}</p>
            <p><strong>Kunde Email:</strong> {order_data['customer_email']}</p>
            <p><strong>Datum:</strong> {datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M:%S')} UTC</p>
            <hr>
            <h3>Bestellte Produkte:</h3>
            <p>{items_html}</p>
            <hr>
            <p><strong>Gesamtbetrag:</strong> €{order_data['total']:.2f}</p>
            <p><strong>PayPal Payment ID:</strong> {order_data.get('payment_id', 'N/A')}</p>
            <p><strong>Status:</strong> {order_data['status']}</p>
        </body>
        </html>
        """
        
        message.attach(MIMEText(html_body, 'html'))
        
        # Send email
        await aiosmtplib.send(
            message,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            start_tls=True
        )
        
        logging.info(f"Order notification email sent for order {order_data['id']}")
    except Exception as e:
        logging.error(f"Failed to send order notification: {str(e)}")

# Customer order status notification
async def send_customer_notification(order_data, status_type: str):
    try:
        smtp_host = os.environ.get('SMTP_HOST')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_user = os.environ.get('SMTP_USER')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        
        if not all([smtp_host, smtp_user, smtp_password]):
            logging.warning("Email configuration incomplete, skipping customer notification")
            return
        
        customer_email = order_data.get('customer_email')
        if not customer_email:
            logging.warning("No customer email found")
            return
        
        # Create email
        message = MIMEMultipart()
        message['From'] = smtp_user
        message['To'] = customer_email
        
        # Different email content based on status
        if status_type == 'paid':
            subject = "✅ Bestellbestätigung - apebrain.cloud"
            status_text = "Ihre Bestellung wurde erfolgreich bezahlt und wird bearbeitet."
        elif status_type == 'shipped':
            subject = "📦 Ihre Bestellung wurde versendet - apebrain.cloud"
            tracking_html = ""
            if order_data.get('tracking_number'):
                tracking_url = order_data.get('tracking_url', '#')
                tracking_html = f'<p><strong>Sendungsverfolgung:</strong> <a href="{tracking_url}">{order_data["tracking_number"]}</a></p>'
            status_text = f"Ihre Bestellung ist unterwegs!<br>{tracking_html}"
        elif status_type == 'delivered':
            subject = "🏠 Ihre Bestellung wurde zugestellt - apebrain.cloud"
            status_text = "Ihre Bestellung wurde erfolgreich zugestellt. Wir hoffen, Sie genießen Ihre Produkte!"
        else:
            subject = f"📬 Update zu Ihrer Bestellung - apebrain.cloud"
            status_text = f"Status Ihrer Bestellung: {order_data.get('status', 'N/A')}"
        
        message['Subject'] = subject
        
        items_html = "<br>".join([
            f"- {item['name']} x{item['quantity']} - €{item['price'] * item['quantity']:.2f}"
            for item in order_data.get('items', [])
        ])
        
        tracking_section = ""
        if order_data.get('tracking_url') and order_data.get('tracking_number'):
            tracking_section = f"""
            <div style="margin-top: 1.5rem; padding: 1rem; background: #f3f4f6; border-radius: 8px;">
                <h3 style="color: #7a9053; margin-top: 0;">Sendungsverfolgung</h3>
                <p><strong>Tracking-Nummer:</strong> {order_data['tracking_number']}</p>
                <p><strong>Versanddienstleister:</strong> {order_data.get('shipping_carrier', 'N/A')}</p>
                <p><a href="{order_data['tracking_url']}" style="color: #7a9053; text-decoration: underline;">Sendung verfolgen →</a></p>
            </div>
            """
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #7a9053; color: white; padding: 2rem; text-align: center;">
                <h1 style="margin: 0;">apebrain.cloud</h1>
            </div>
            <div style="padding: 2rem;">
                <h2 style="color: #3a4520;">{subject.split(' - ')[0]}</h2>
                <p>{status_text}</p>
                <hr style="border: 1px solid #e8ebe0; margin: 1.5rem 0;">
                <p><strong>Bestellnummer:</strong> {order_data.get('id', 'N/A')[:12]}...</p>
                <p><strong>Datum:</strong> {datetime.now(timezone.utc).strftime('%d.%m.%Y')}</p>
                <h3 style="color: #3a4520;">Bestellte Produkte:</h3>
                <p style="margin-left: 1rem;">{items_html}</p>
                <hr style="border: 1px solid #e8ebe0; margin: 1.5rem 0;">
                <p><strong>Gesamtbetrag:</strong> €{order_data.get('total', 0):.2f}</p>
                {tracking_section}
                <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #e8ebe0; color: #7a9053; font-size: 0.9rem;">
                    <p>Bei Fragen kontaktieren Sie uns: apebrain333@gmail.com</p>
                    <p>Vielen Dank für Ihren Einkauf!</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        message.attach(MIMEText(html_body, 'html'))
        
        # Send email
        await aiosmtplib.send(
            message,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            start_tls=True
        )
        
        logging.info(f"Customer notification sent to {customer_email} for order {order_data.get('id')}")
    except Exception as e:
        logging.error(f"Failed to send customer notification: {str(e)}")

# Admin delivery completion notification
async def send_admin_delivery_notification(order_data):
    try:
        smtp_host = os.environ.get('SMTP_HOST')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_user = os.environ.get('SMTP_USER')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        notification_email = os.environ.get('NOTIFICATION_EMAIL')
        
        if not all([smtp_host, smtp_user, smtp_password, notification_email]):
            logging.warning("Email configuration incomplete, skipping admin delivery notification")
            return
        
        # Create email
        message = MIMEMultipart()
        message['From'] = smtp_user
        message['To'] = notification_email
        message['Subject'] = "✅ Bestellung zugestellt - apebrain.cloud"
        
        items_html = "<br>".join([
            f"- {item['name']} x{item['quantity']} - €{item['price'] * item['quantity']:.2f}"
            for item in order_data.get('items', [])
        ])
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #22c55e;">Bestellung erfolgreich zugestellt! ✅</h2>
            <p>Die folgende Bestellung wurde erfolgreich an den Kunden zugestellt:</p>
            <hr>
            <p><strong>Bestellnummer:</strong> {order_data.get('id', 'N/A')}</p>
            <p><strong>Kunde Email:</strong> {order_data.get('customer_email', 'N/A')}</p>
            <p><strong>Zugestellt am:</strong> {datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M:%S')} UTC</p>
            <hr>
            <h3>Bestellte Produkte:</h3>
            <p>{items_html}</p>
            <hr>
            <p><strong>Gesamtbetrag:</strong> €{order_data.get('total', 0):.2f}</p>
            {f'<p><strong>Tracking-Nummer:</strong> {order_data.get("tracking_number", "N/A")}</p>' if order_data.get('tracking_number') else ''}
            <p style="margin-top: 2rem; color: #7a9053;">Diese Bestellung ist nun abgeschlossen.</p>
        </body>
        </html>
        """
        
        message.attach(MIMEText(html_body, 'html'))
        
        # Send email
        await aiosmtplib.send(
            message,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            start_tls=True
        )
        
        logging.info(f"Admin delivery notification sent for order {order_data.get('id')}")
    except Exception as e:
        logging.error(f"Failed to send admin delivery notification: {str(e)}")




# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Configure PayPal
paypalrestsdk.configure({
    "mode": os.environ.get('PAYPAL_MODE', 'sandbox'),
    "client_id": os.environ.get('PAYPAL_CLIENT_ID', ''),
    "client_secret": os.environ.get('PAYPAL_CLIENT_SECRET', '')
})

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
# User Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    hashed_password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    auth_provider: str = "email"  # email, google, paypal
    google_id: Optional[str] = None
    paypal_id: Optional[str] = None
    is_member: bool = True  # All registered users are members
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str

class BlogPost(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    keywords: str
    image_url: Optional[str] = None
    image_urls: Optional[List[str]] = None  # Multiple images from Pexels
    image_base64: Optional[str] = None
    video_url: Optional[str] = None  # YouTube URL
    audio_url: Optional[str] = None  # Audio file URL or base64
    status: str = "draft"  # draft or published
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None

class BlogPostCreate(BaseModel):
    keywords: str

class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    keywords: Optional[str] = None
    image_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    status: Optional[str] = None

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminSettingsUpdate(BaseModel):
    current_password: str
    admin_username: str
    new_password: Optional[str] = None

# Shop Models
class OrderItem(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int
    product_type: str  # physical or digital

class CreateOrder(BaseModel):
    items: List[OrderItem]
    total: float
    customer_email: str
    coupon_code: Optional[str] = None

class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payment_id: Optional[str] = None
    items: List[dict]
    total: float
    customer_email: str
    coupon_code: Optional[str] = None
    discount_amount: float = 0.0
    status: str = "pending"  # pending, paid, packed, shipped, in_transit, delivered, cancelled
    tracking_number: Optional[str] = None
    shipping_carrier: Optional[str] = None  # DHL, DPD, Hermes, UPS, etc.
    tracking_url: Optional[str] = None
    viewed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

# Coupon Models
class Coupon(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    discount_type: str  # percentage or fixed
    discount_value: float
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

class CouponCreate(BaseModel):
    code: str
    discount_type: str
    discount_value: float
    is_active: bool = True
    expires_at: Optional[datetime] = None

class CouponUpdate(BaseModel):
    code: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None

class CouponValidate(BaseModel):
    code: str
    order_total: float

class GenerateResponse(BaseModel):
    title: str
    content: str
    image_base64: Optional[str] = None

# Admin authentication
@api_router.post("/admin/login")
async def admin_login(login: AdminLogin):
    stored_username = os.environ.get('ADMIN_USERNAME', 'admin')
    stored_password = os.environ.get('ADMIN_PASSWORD', 'apebrain2024')
    
    if login.username == stored_username and login.password == stored_password:
        return {"success": True, "message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Get admin settings
@api_router.get("/admin/settings")
async def get_admin_settings():
    return {
        "admin_username": os.environ.get('ADMIN_USERNAME', 'admin')
    }

# Update admin settings
@api_router.post("/admin/settings")
async def update_admin_settings(settings: AdminSettingsUpdate):
    # Verify current password
    stored_password = os.environ.get('ADMIN_PASSWORD', 'apebrain2024')
    if settings.current_password != stored_password:
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    # Update .env file
    env_path = ROOT_DIR / '.env'
    env_content = env_path.read_text()
    
    # Update username
    if 'ADMIN_USERNAME=' in env_content:
        env_content = re.sub(r'ADMIN_USERNAME=.*', f'ADMIN_USERNAME=\"{settings.admin_username}\"', env_content)
    else:
        env_content += f'\nADMIN_USERNAME=\"{settings.admin_username}\"'
    
    # Update password if provided
    if settings.new_password:
        if 'ADMIN_PASSWORD=' in env_content:
            env_content = re.sub(r'ADMIN_PASSWORD=.*', f'ADMIN_PASSWORD=\"{settings.new_password}\"', env_content)
        else:
            env_content += f'\nADMIN_PASSWORD=\"{settings.new_password}\"'
    
    env_path.write_text(env_content)
    
    # Reload environment variables
    load_dotenv(ROOT_DIR / '.env', override=True)
    
    return {"success": True, "message": "Settings updated successfully"}

# ============= CUSTOMER AUTH ENDPOINTS =============
# Register new customer
@api_router.post("/auth/register")
async def register_customer(user_data: UserCreate):
    try:
        # Check if email already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user document
        user_doc = {
            "id": str(uuid.uuid4()),
            "email": user_data.email,
            "hashed_password": get_password_hash(user_data.password),
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "auth_provider": "email",
            "is_member": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_login": None
        }
        
        await db.users.insert_one(user_doc)
        
        # Send notification email to admin
        try:
            smtp_host = os.environ.get('SMTP_HOST')
            smtp_port = int(os.environ.get('SMTP_PORT', 587))
            smtp_user = os.environ.get('SMTP_USER')
            smtp_password = os.environ.get('SMTP_PASSWORD')
            admin_email = os.environ.get('SMTP_USER')  # Admin email
            
            message = MIMEMultipart("alternative")
            message["Subject"] = "🎉 Neue Registrierung - ApeBrain.cloud"
            message["From"] = smtp_user
            message["To"] = admin_email
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f8f9fa; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px;">
                    <h2 style="color: #7a9053;">🍄 Neue Mitgliederregistrierung</h2>
                    <p>Ein neuer Kunde hat sich registriert!</p>
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 5px 0;"><strong>Email:</strong> {user_doc["email"]}</p>
                        <p style="margin: 5px 0;"><strong>Name:</strong> {user_doc.get("first_name", "")} {user_doc.get("last_name", "")}</p>
                        <p style="margin: 5px 0;"><strong>Registriert am:</strong> {datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M")} UTC</p>
                    </div>
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                    <p style="color: #9ca3af; font-size: 0.8rem;">ApeBrain.cloud Admin Notification</p>
                </div>
            </body>
            </html>
            """
            
            message.attach(MIMEText(html_content, "html"))
            
            await aiosmtplib.send(
                message,
                hostname=smtp_host,
                port=smtp_port,
                username=smtp_user,
                password=smtp_password,
                start_tls=True
            )
        except Exception as email_error:
            logging.error(f"Failed to send registration notification: {str(email_error)}")
        
        # Create access token
        access_token = create_access_token(data={"sub": user_doc["id"]})
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_doc["id"],
                "email": user_doc["email"],
                "first_name": user_doc.get("first_name"),
                "last_name": user_doc.get("last_name")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

# Customer login
@api_router.post("/auth/login")
async def login_customer(login_data: UserLogin):
    try:
        # Find user by email
        user = await db.users.find_one({"email": login_data.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not verify_password(login_data.password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Update last login
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {"last_login": datetime.now(timezone.utc).isoformat()}}
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": user["id"]})
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "is_member": user.get("is_member", True)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error logging in user: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

# Get current user info
@api_router.get("/auth/me")
async def get_current_user_info(user_id: str = Depends(get_current_user)):
    try:
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "hashed_password": 0})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching user info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user info")

# Get user orders
@api_router.get("/auth/orders")
async def get_user_orders(user_id: str = Depends(get_current_user)):
    try:
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Find orders by user email
        orders = await db.orders.find({"customer_email": user["email"]}, {"_id": 0}).sort("created_at", -1).to_list(length=100)
        return orders
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching user orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch orders")

# Request password reset
@api_router.post("/auth/password-reset-request")
async def request_password_reset(request: PasswordResetRequest):
    try:
        user = await db.users.find_one({"email": request.email})
        if not user:
            return {"success": True, "message": "If your email is registered, you will receive a password reset link"}
        
        # Generate reset token
        reset_token = create_access_token(
            data={"sub": user["id"], "purpose": "password_reset"},
            expires_delta=timedelta(hours=1)
        )
        
        # Save token in database
        await db.password_reset_tokens.insert_one({
            "user_id": user["id"],
            "token": reset_token,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "used": False
        })
        
        # Send email with reset link
        smtp_host = os.environ.get('SMTP_HOST')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_user = os.environ.get('SMTP_USER')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
        
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"
        
        message = MIMEMultipart("alternative")
        message["Subject"] = "Password Reset - ApeBrain.cloud"
        message["From"] = smtp_user
        message["To"] = user["email"]
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f8f9fa; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px;">
                <h2 style="color: #7a9053;">🍄 Password Reset Request</h2>
                <p>Hello,</p>
                <p>You requested to reset your password for your ApeBrain.cloud account.</p>
                <p>Click the button below to reset your password (link expires in 1 hour):</p>
                <a href="{reset_link}" style="display: inline-block; background-color: #7a9053; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0;">Reset Password</a>
                <p style="color: #6b7280; font-size: 0.9rem;">If you didn't request this, please ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                <p style="color: #9ca3af; font-size: 0.8rem;">ApeBrain.cloud - god knows how</p>
            </div>
        </body>
        </html>
        """
        
        message.attach(MIMEText(html_content, "html"))
        
        await aiosmtplib.send(
            message,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            start_tls=True
        )
        
        return {"success": True, "message": "If your email is registered, you will receive a password reset link"}
    except Exception as e:
        logging.error(f"Error requesting password reset: {str(e)}")
        return {"success": True, "message": "If your email is registered, you will receive a password reset link"}

# Reset password
@api_router.post("/auth/password-reset")
async def reset_password(reset_data: PasswordReset):
    try:
        # Verify token
        payload = jwt.decode(reset_data.token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        purpose = payload.get("purpose")
        
        if purpose != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid reset token")
        
        # Check if token was already used
        token_record = await db.password_reset_tokens.find_one({"token": reset_data.token, "used": False})
        if not token_record:
            raise HTTPException(status_code=400, detail="Reset token already used or invalid")
        
        # Update password
        hashed_password = get_password_hash(reset_data.new_password)
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"hashed_password": hashed_password}}
        )
        
        # Mark token as used
        await db.password_reset_tokens.update_one(
            {"token": reset_data.token},
            {"$set": {"used": True}}
        )
        
        return {"success": True, "message": "Password reset successful"}
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error resetting password: {str(e)}")
        raise HTTPException(status_code=500, detail="Password reset failed")

# Google OAuth Login
@api_router.get("/auth/google/url")
async def get_google_auth_url():
    """Get Google OAuth authorization URL"""
    try:
        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        redirect_uri = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/auth/google/callback"
        
        auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            "response_type=code&"
            "scope=openid%20email%20profile&"
            "access_type=offline"
        )
        
        return {"auth_url": auth_url}
    except Exception as e:
        logging.error(f"Error generating Google auth URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate auth URL")

# Google OAuth Callback - verify token
@api_router.post("/auth/google/verify")
async def verify_google_token(token_data: dict):
    """Verify Google ID token and create/login user"""
    try:
        token = token_data.get('credential')
        if not token:
            raise HTTPException(status_code=400, detail="Token missing")
        
        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            client_id
        )
        
        # Get user info from token
        google_user_id = idinfo['sub']
        email = idinfo['email']
        first_name = idinfo.get('given_name')
        last_name = idinfo.get('family_name')
        
        # Check if user exists
        user = await db.users.find_one({"$or": [{"google_id": google_user_id}, {"email": email}]})
        
        if not user:
            # Create new user
            user_doc = {
                "id": str(uuid.uuid4()),
                "email": email,
                "hashed_password": "",
                "first_name": first_name,
                "last_name": last_name,
                "auth_provider": "google",
                "google_id": google_user_id,
                "is_member": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_login": datetime.now(timezone.utc).isoformat()
            }
            
            await db.users.insert_one(user_doc)
            
            # Send admin notification
            try:
                smtp_host = os.environ.get('SMTP_HOST')
                smtp_port = int(os.environ.get('SMTP_PORT', 587))
                smtp_user = os.environ.get('SMTP_USER')
                smtp_password = os.environ.get('SMTP_PASSWORD')
                
                message = MIMEMultipart("alternative")
                message["Subject"] = "🎉 Neue Google-Registrierung - ApeBrain.cloud"
                message["From"] = smtp_user
                message["To"] = smtp_user
                
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; background-color: #f8f9fa; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px;">
                        <h2 style="color: #7a9053;">🍄 Neue Google-Registrierung</h2>
                        <p>Ein neuer Kunde hat sich über Google angemeldet!</p>
                        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <p style="margin: 5px 0;"><strong>Email:</strong> {email}</p>
                            <p style="margin: 5px 0;"><strong>Name:</strong> {first_name} {last_name}</p>
                            <p style="margin: 5px 0;"><strong>Auth Provider:</strong> Google</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                message.attach(MIMEText(html_content, "html"))
                await aiosmtplib.send(message, hostname=smtp_host, port=smtp_port, username=smtp_user, password=smtp_password, start_tls=True)
            except Exception as email_error:
                logging.error(f"Failed to send notification: {str(email_error)}")
            
            user = user_doc
        else:
            # Update last login and google_id if not set
            update_data = {"last_login": datetime.now(timezone.utc).isoformat()}
            if not user.get("google_id"):
                update_data["google_id"] = google_user_id
            
            await db.users.update_one({"id": user["id"]}, {"$set": update_data})
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user["id"]})
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "is_member": True
            }
        }
    except ValueError as e:
        logging.error(f"Invalid token: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logging.error(f"Error verifying Google token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify Google login")

# Get landing page settings (button visibility + gallery)
@api_router.get("/landing-settings")
async def get_landing_settings():
    try:
        settings = await db.settings.find_one({"type": "landing_page"}, {"_id": 0})
        if not settings:
            # Return defaults
            return {
                "show_blog": True,
                "show_shop": True,
                "show_minigames": True,
                "blog_gallery_mode": "none",
                "shop_gallery_mode": "none",
                "minigames_gallery_mode": "none",
                "blog_gallery_images": [],
                "shop_gallery_images": [],
                "minigames_gallery_images": [],
                "card_bg_color_start": "rgba(167, 139, 250, 0.15)",
                "card_bg_color_middle": "rgba(139, 92, 246, 0.12)",
                "card_bg_color_end": "rgba(124, 58, 237, 0.15)"
            }
        
        # If gallery mode is "auto", fetch images from database
        if settings.get("blog_gallery_mode") == "auto":
            blogs = await db.blogs.find({"status": "published"}, {"_id": 0, "image_urls": 1}).limit(3).to_list(length=3)
            auto_images = []
            for blog in blogs:
                if blog.get("image_urls"):
                    auto_images.extend(blog["image_urls"][:1])  # Take first image from each blog
            settings["blog_gallery_images"] = auto_images[:3]  # Max 3 images
        
        if settings.get("shop_gallery_mode") == "auto":
            products = await db.products.find({"image_url": {"$exists": True}}, {"_id": 0, "image_url": 1}).limit(3).to_list(length=3)
            settings["shop_gallery_images"] = [p["image_url"] for p in products if p.get("image_url")][:3]
        
        return settings
    except Exception as e:
        logging.error(f"Error fetching landing settings: {str(e)}")
        # Return defaults on error
        return {
            "show_blog": True,
            "show_shop": True,
            "show_minigames": True,
            "blog_gallery_mode": "none",
            "shop_gallery_mode": "none",
            "minigames_gallery_mode": "none",
            "blog_gallery_images": [],
            "shop_gallery_images": [],
            "minigames_gallery_images": [],
            "card_bg_color_start": "rgba(167, 139, 250, 0.15)",
            "card_bg_color_middle": "rgba(139, 92, 246, 0.12)",
            "card_bg_color_end": "rgba(124, 58, 237, 0.15)"
        }

# Update landing page settings (button visibility + gallery)
@api_router.post("/landing-settings")
async def update_landing_settings(settings: dict):
    try:
        settings_doc = {
            "type": "landing_page",
            "show_blog": settings.get("show_blog", True),
            "show_shop": settings.get("show_shop", True),
            "show_minigames": settings.get("show_minigames", True),
            "blog_gallery_mode": settings.get("blog_gallery_mode", "none"),
            "shop_gallery_mode": settings.get("shop_gallery_mode", "none"),
            "minigames_gallery_mode": settings.get("minigames_gallery_mode", "none"),
            "blog_gallery_images": settings.get("blog_gallery_images", []),
            "shop_gallery_images": settings.get("shop_gallery_images", []),
            "minigames_gallery_images": settings.get("minigames_gallery_images", []),
            "card_bg_color_start": settings.get("card_bg_color_start", "rgba(167, 139, 250, 0.15)"),
            "card_bg_color_middle": settings.get("card_bg_color_middle", "rgba(139, 92, 246, 0.12)"),
            "card_bg_color_end": settings.get("card_bg_color_end", "rgba(124, 58, 237, 0.15)")
        }
        
        await db.settings.update_one(
            {"type": "landing_page"},
            {"$set": settings_doc},
            upsert=True
        )
        
        return {"success": True, "message": "Landing page settings updated successfully"}
    except Exception as e:
        logging.error(f"Error updating landing settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update landing settings")

# Upload gallery image for landing page button
@api_router.post("/landing-settings/upload-gallery-image/{section}")
async def upload_landing_gallery_image(section: str, file: UploadFile = File(...)):
    try:
        if section not in ["blog", "shop", "minigames"]:
            raise HTTPException(status_code=400, detail="Invalid section. Must be 'blog', 'shop', or 'minigames'")
        
        # Read and encode image
        contents = await file.read()
        base64_image = base64.b64encode(contents).decode()
        image_url = f"data:{file.content_type};base64,{base64_image}"
        
        # Get current settings
        settings = await db.settings.find_one({"type": "landing_page"})
        if not settings:
            settings = {
                "type": "landing_page",
                "blog_gallery_images": [],
                "shop_gallery_images": [],
                "minigames_gallery_images": []
            }
        
        # Add image to appropriate array
        field_name = f"{section}_gallery_images"
        if field_name not in settings:
            settings[field_name] = []
        
        settings[field_name].append(image_url)
        
        # Limit to 3 images per section
        settings[field_name] = settings[field_name][-3:]
        
        # Update database
        await db.settings.update_one(
            {"type": "landing_page"},
            {"$set": {field_name: settings[field_name]}},
            upsert=True
        )
        
        return {
            "success": True,
            "image_url": image_url,
            "message": f"Gallery image uploaded for {section}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error uploading gallery image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload gallery image: {str(e)}")

# ============= COLOR PROFILE ENDPOINTS =============
# Get all color profiles
@api_router.get("/color-profiles")
async def get_color_profiles():
    try:
        profiles = await db.color_profiles.find({}, {"_id": 0}).to_list(length=100)
        return profiles
    except Exception as e:
        logging.error(f"Error fetching color profiles: {str(e)}")
        return []

# Save new color profile
@api_router.post("/color-profiles")
async def save_color_profile(profile: dict):
    try:
        profile_doc = {
            "id": str(uuid.uuid4()),
            "name": profile.get("name"),
            "startR": profile.get("startR"),
            "startG": profile.get("startG"),
            "startB": profile.get("startB"),
            "startOpacity": profile.get("startOpacity"),
            "middleR": profile.get("middleR"),
            "middleG": profile.get("middleG"),
            "middleB": profile.get("middleB"),
            "middleOpacity": profile.get("middleOpacity"),
            "endR": profile.get("endR"),
            "endG": profile.get("endG"),
            "endB": profile.get("endB"),
            "endOpacity": profile.get("endOpacity"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.color_profiles.insert_one(profile_doc)
        return {"success": True, "message": "Color profile saved successfully"}
    except Exception as e:
        logging.error(f"Error saving color profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save color profile")

# Delete color profile
@api_router.delete("/color-profiles/{profile_id}")
async def delete_color_profile(profile_id: str):
    try:
        result = await db.color_profiles.delete_one({"id": profile_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Color profile not found")
        return {"success": True, "message": "Color profile deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting color profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete color profile")

# ============= BLOG FEATURE SETTINGS =============
# Get blog feature settings
@api_router.get("/blog-features")
async def get_blog_features():
    try:
        settings = await db.settings.find_one({"type": "blog_features"}, {"_id": 0})
        if not settings:
            # Return defaults
            return {
                "enable_video": True,
                "enable_audio": True,
                "enable_text_to_speech": True
            }
        return settings
    except Exception as e:
        logging.error(f"Error fetching blog features: {str(e)}")
        return {
            "enable_video": True,
            "enable_audio": True,
            "enable_text_to_speech": True
        }

# Update blog feature settings
@api_router.post("/blog-features")
async def update_blog_features(settings: dict):
    try:
        settings_doc = {
            "type": "blog_features",
            "enable_video": settings.get("enable_video", True),
            "enable_audio": settings.get("enable_audio", True),
            "enable_text_to_speech": settings.get("enable_text_to_speech", True)
        }
        
        await db.settings.update_one(
            {"type": "blog_features"},
            {"$set": settings_doc},
            upsert=True
        )
        
        return {"success": True, "message": "Blog features updated successfully"}
    except Exception as e:
        logging.error(f"Error updating blog features: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update blog features")

# Generate blog post with AI
@api_router.post("/blogs/generate", response_model=GenerateResponse)
async def generate_blog(input: BlogPostCreate):
    try:
        gemini_api_key = os.environ.get('GEMINI_API_KEY')
        
        # Generate blog content using Gemini Flash Lite
        chat = LlmChat(
            api_key=gemini_api_key,
            session_id=f"blog-gen-{uuid.uuid4()}",
            system_message="You are an expert writer specializing in health, nature, consciousness, spirituality, and holistic wellness. Write engaging, informative blog posts that are SEO-friendly and educational. Cover topics like natural remedies, mindfulness, nutrition, herbal medicine, sustainable living, and personal growth. Focus on scientific facts when available, practical applications, and inspiring content."
        ).with_model("gemini", "gemini-2.0-flash-lite")
        
        user_message = UserMessage(
            text=f"Write a comprehensive blog post about: {input.keywords}. Include an engaging title, detailed content with sections covering the main topic, benefits, scientific research (if applicable), practical applications, and important considerations. Make it around 800-1200 words. Format with proper headings using markdown. Be creative and informative."
        )
        
        blog_content = await chat.send_message(user_message)
        
        # Extract title from content (first line)
        lines = blog_content.strip().split('\n')
        title = lines[0].replace('#', '').strip() if lines else input.keywords
        content = '\n'.join(lines[1:]).strip() if len(lines) > 1 else blog_content
        
        # Fetch image from Pexels based on keywords
        image_base64 = None
        try:
            pexels_key = os.environ.get('PEXELS_API_KEY')
            if pexels_key:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"https://api.pexels.com/v1/search?query={input.keywords}&per_page=1",
                        headers={"Authorization": pexels_key},
                        timeout=10.0
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('photos') and len(data['photos']) > 0:
                            image_url = data['photos'][0]['src']['medium']
                            # Download image and convert to base64
                            img_response = await client.get(image_url, timeout=10.0)
                            if img_response.status_code == 200:
                                image_base64 = f"data:image/jpeg;base64,{base64.b64encode(img_response.content).decode()}"
        except Exception as img_error:
            logging.warning(f"Failed to fetch image for blog generation: {str(img_error)}")
        
        return GenerateResponse(
            title=title,
            content=content,
            image_base64=image_base64
        )
    except Exception as e:
        logging.error(f"Error generating blog: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate blog: {str(e)}")

# Upload image for blog
@api_router.post("/blogs/{blog_id}/upload-image")
async def upload_blog_image(blog_id: str, file: UploadFile = File(...)):
    try:
        # Read file content
        contents = await file.read()
        
        # Convert to base64 for storage
        image_base64 = base64.b64encode(contents).decode('utf-8')
        image_url = f"data:image/{file.content_type.split('/')[-1]};base64,{image_base64}"
        
        # Update blog with image
        result = await db.blogs.update_one(
            {"id": blog_id},
            {"$set": {"image_url": image_url}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Blog not found")
        
        return {"success": True, "image_url": image_url}
    except Exception as e:
        logging.error(f"Error uploading image: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload image")

# Upload image for product
@api_router.post("/products/{product_id}/upload-image")
async def upload_product_image(product_id: str, file: UploadFile = File(...)):
    try:
        # Read file content
        contents = await file.read()
        
        # Convert to base64 for storage
        image_base64 = base64.b64encode(contents).decode('utf-8')
        image_url = f"data:image/{file.content_type.split('/')[-1]};base64,{image_base64}"
        
        # Update product with image
        result = await db.products.update_one(
            {"id": product_id},
            {"$set": {"image_url": image_url}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {"success": True, "image_url": image_url}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error uploading product image: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload product image")

# Upload audio for blog
@api_router.post("/blogs/{blog_id}/upload-audio")
async def upload_blog_audio(blog_id: str, file: UploadFile = File(...)):
    try:
        # Read file content
        contents = await file.read()
        
        # Convert to base64 for storage
        audio_base64 = base64.b64encode(contents).decode('utf-8')
        # Determine audio type
        content_type = file.content_type or 'audio/mpeg'
        audio_url = f"data:{content_type};base64,{audio_base64}"
        
        # Update blog with audio
        result = await db.blogs.update_one(
            {"id": blog_id},
            {"$set": {"audio_url": audio_url}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Blog not found")
        
        return {"success": True, "audio_url": audio_url}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error uploading audio: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload audio")

# Fetch images from web based on keywords
@api_router.get("/fetch-images")
async def fetch_images_from_web(keywords: str, count: int = 3):
    try:
        pexels_api_key = os.environ.get('PEXELS_API_KEY')
        if not pexels_api_key:
            raise HTTPException(status_code=500, detail="Pexels API key not configured")
        
        # Search Pexels for relevant images
        search_url = "https://api.pexels.com/v1/search"
        headers = {
            "Authorization": pexels_api_key
        }
        params = {
            "query": keywords,
            "per_page": min(count, 5),  # Max 5 images
            "orientation": "landscape"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(search_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                image_urls = []
                
                # Download and convert each image to base64
                for photo in data.get('photos', [])[:count]:
                    try:
                        # Use medium size image
                        img_url = photo.get('src', {}).get('medium')
                        if img_url:
                            img_response = await client.get(img_url)
                            if img_response.status_code == 200:
                                image_base64 = base64.b64encode(img_response.content).decode('utf-8')
                                image_data_url = f"data:image/jpeg;base64,{image_base64}"
                                image_urls.append(image_data_url)
                    except Exception as e:
                        logging.error(f"Error downloading image: {str(e)}")
                        continue
                
                if image_urls:
                    return {"success": True, "image_urls": image_urls}
                else:
                    raise HTTPException(status_code=404, detail="No images found")
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch from Pexels")
    except Exception as e:
        logging.error(f"Error fetching images from web: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch images from web: {str(e)}")


# Fetch single image from web (using Pexels)
@api_router.get("/fetch-image")
async def fetch_single_image_from_web(keywords: str = "nature"):
    try:
        pexels_api_key = os.environ.get('PEXELS_API_KEY')
        if not pexels_api_key:
            raise HTTPException(status_code=500, detail="Pexels API key not configured")
        
        # Search Pexels for one image
        search_url = "https://api.pexels.com/v1/search"
        headers = {
            "Authorization": pexels_api_key
        }
        params = {
            "query": keywords,
            "per_page": 1,
            "orientation": "landscape"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(search_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                photos = data.get('photos', [])
                
                if photos:
                    photo = photos[0]
                    img_url = photo.get('src', {}).get('medium')
                    
                    if img_url:
                        # Download and convert to base64
                        img_response = await client.get(img_url)
                        if img_response.status_code == 200:
                            image_base64 = base64.b64encode(img_response.content).decode('utf-8')
                            image_data_url = f"data:image/jpeg;base64,{image_base64}"
                            return {"success": True, "image_url": image_data_url}
                
                raise HTTPException(status_code=404, detail="No image found")
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch from Pexels")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching image from web: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch image from web: {str(e)}")

# Create/Save blog post
@api_router.post("/blogs", response_model=BlogPost)
async def create_blog(blog: BlogPost):
    try:
        doc = blog.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        if doc['published_at']:
            doc['published_at'] = doc['published_at'].isoformat()
        
        await db.blogs.insert_one(doc)
        return blog
    except Exception as e:
        logging.error(f"Error creating blog: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create blog")

# Get all published blogs (public)
@api_router.get("/blogs", response_model=List[BlogPost])
async def get_blogs(status: Optional[str] = "published"):
    try:
        query = {"status": status} if status else {}
        blogs = await db.blogs.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
        
        for blog in blogs:
            if isinstance(blog.get('created_at'), str):
                blog['created_at'] = datetime.fromisoformat(blog['created_at'])
            if blog.get('published_at') and isinstance(blog['published_at'], str):
                blog['published_at'] = datetime.fromisoformat(blog['published_at'])
        
        return blogs
    except Exception as e:
        logging.error(f"Error fetching blogs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch blogs")

# Get single blog
@api_router.get("/blogs/{blog_id}", response_model=BlogPost)
async def get_blog(blog_id: str):
    try:
        blog = await db.blogs.find_one({"id": blog_id}, {"_id": 0})
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")
        
        if isinstance(blog.get('created_at'), str):
            blog['created_at'] = datetime.fromisoformat(blog['created_at'])
        if blog.get('published_at') and isinstance(blog['published_at'], str):
            blog['published_at'] = datetime.fromisoformat(blog['published_at'])
        
        return blog
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching blog: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch blog")

# Update blog
@api_router.put("/blogs/{blog_id}", response_model=BlogPost)
async def update_blog(blog_id: str, update: BlogPostUpdate):
    try:
        update_data = {k: v for k, v in update.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        result = await db.blogs.update_one(
            {"id": blog_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Blog not found")
        
        blog = await db.blogs.find_one({"id": blog_id}, {"_id": 0})
        
        if isinstance(blog.get('created_at'), str):
            blog['created_at'] = datetime.fromisoformat(blog['created_at'])
        if blog.get('published_at') and isinstance(blog['published_at'], str):
            blog['published_at'] = datetime.fromisoformat(blog['published_at'])
        
        return blog
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating blog: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update blog")

# Publish blog
@api_router.post("/blogs/{blog_id}/publish")
async def publish_blog(blog_id: str):
    try:
        result = await db.blogs.update_one(
            {"id": blog_id},
            {"$set": {
                "status": "published",
                "published_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Blog not found")
        
        return {"success": True, "message": "Blog published successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error publishing blog: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to publish blog")

# Delete blog
@api_router.delete("/blogs/{blog_id}")
async def delete_blog(blog_id: str):
    try:
        result = await db.blogs.delete_one({"id": blog_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Blog not found")
        
        return {"success": True, "message": "Blog deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting blog: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete blog")

# ============= SHOP & PAYPAL ENDPOINTS =============

# Create PayPal order
@api_router.post("/shop/create-order")
async def create_shop_order(order: CreateOrder):
    try:
        if not os.environ.get('PAYPAL_CLIENT_ID'):
            raise HTTPException(status_code=500, detail="PayPal not configured. Please add PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET to .env file")
        
        # Validate and apply coupon if provided
        discount_amount = 0.0
        discount_percentage = 0.0
        if order.coupon_code:
            try:
                coupon = await db.coupons.find_one({"code": order.coupon_code.upper(), "is_active": True}, {"_id": 0})
                if coupon:
                    # Calculate discount based on original item prices
                    original_subtotal = sum(item.price * item.quantity for item in order.items)
                    if coupon['discount_type'] == 'percentage':
                        discount_amount = (original_subtotal * coupon['discount_value']) / 100
                        discount_percentage = coupon['discount_value'] / 100
                    else:
                        discount_amount = coupon['discount_value']
                    
                    # The order.total should already be the discounted total from frontend
                    # Don't apply discount again here - just store the discount info
            except Exception as e:
                logging.warning(f"Could not apply coupon: {str(e)}")
        
        # Create PayPal payment with adjusted item prices if discount applied
        items_list = []
        for item in order.items:
            # Calculate adjusted price per item if discount applied
            item_price = item.price
            if discount_percentage > 0:
                # Apply percentage discount to each item
                item_price = item.price * (1 - discount_percentage)
            elif discount_amount > 0 and len(order.items) > 0:
                # For fixed discount, distribute proportionally across items
                item_total = sum(i.price * i.quantity for i in order.items)
                item_discount_ratio = (item.price * item.quantity) / item_total
                item_discount = discount_amount * item_discount_ratio
                item_price = (item.price * item.quantity - item_discount) / item.quantity
            
            items_list.append({
                "name": item.name,
                "sku": item.product_id,
                "price": f"{item_price:.2f}",
                "currency": "USD",
                "quantity": item.quantity
            })
        
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/payment/success",
                "cancel_url": f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/payment/cancel"
            },
            "transactions": [{
                "item_list": {
                    "items": items_list
                },
                "amount": {
                    "total": f"{order.total:.2f}",
                    "currency": "USD"
                },
                "description": "ApeBrain.cloud Shop Purchase"
            }]
        })

        if payment.create():
            # Save order to database
            order_doc = {
                "id": str(uuid.uuid4()),
                "payment_id": payment.id,
                "items": [item.dict() for item in order.items],
                "total": order.total,
                "customer_email": order.customer_email,
                "coupon_code": order.coupon_code,
                "discount_amount": round(discount_amount, 2),
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.orders.insert_one(order_doc)
            
            # Get approval URL
            approval_url = None
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    break
            
            return {
                "success": True,
                "approval_url": approval_url,
                "order_id": order_doc["id"],
                "payment_id": payment.id
            }
        else:
            logging.error(f"PayPal payment creation failed: {payment.error}")
            raise HTTPException(status_code=400, detail=f"Payment creation failed: {payment.error}")
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

# Execute PayPal payment
@api_router.post("/shop/execute-payment")
async def execute_payment(payment_id: str, payer_id: str):
    try:
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({"payer_id": payer_id}):
            # Update order status to 'paid'
            completed_time = datetime.now(timezone.utc).isoformat()
            result = await db.orders.update_one(
                {"payment_id": payment_id},
                {"$set": {
                    "status": "paid",
                    "payer_id": payer_id,
                    "completed_at": completed_time
                }}
            )
            
            if result.matched_count == 0:
                logging.warning(f"Order not found for payment_id: {payment_id}")
            else:
                # Get order data and send notifications
                order = await db.orders.find_one({"payment_id": payment_id})
                if order:
                    # Send admin notification
                    await send_order_notification(order)
                    # Send customer confirmation
                    await send_customer_notification(order, 'paid')
            
            return {
                "success": True,
                "message": "Payment completed successfully",
                "payment_id": payment_id
            }
        else:
            logging.error(f"Payment execution failed: {payment.error}")
            raise HTTPException(status_code=400, detail=f"Payment execution failed: {payment.error}")
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error executing payment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute payment: {str(e)}")

# Get order details
@api_router.get("/orders/{order_id}")
async def get_order(order_id: str):
    try:
        order = await db.orders.find_one({"id": order_id}, {"_id": 0})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching order: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch order")

# Get all orders (admin)
@api_router.get("/orders")
async def get_all_orders():
    try:
        orders = await db.orders.find().sort("created_at", -1).to_list(length=None)
        
        # Convert datetime to ISO string for JSON serialization
        for order in orders:
            if '_id' in order:
                del order['_id']
            if isinstance(order.get('created_at'), datetime):
                order['created_at'] = order['created_at'].isoformat()
            if isinstance(order.get('completed_at'), datetime):
                order['completed_at'] = order['completed_at'].isoformat()
        
        return orders
    except Exception as e:
        logging.error(f"Error fetching orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch orders")

# Mark order as viewed (admin)
@api_router.post("/orders/{order_id}/mark-viewed")
async def mark_order_viewed(order_id: str):
    try:
        result = await db.orders.update_one(
            {"id": order_id},
            {"$set": {"viewed": True}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error marking order as viewed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update order")


# Mark order as viewed - Alias endpoint (shorter URL)
@api_router.post("/orders/{order_id}/viewed")
async def mark_order_viewed_alias(order_id: str):
    """Alias for /orders/{order_id}/mark-viewed for convenience"""
    try:
        result = await db.orders.update_one(
            {"id": order_id},
            {"$set": {"viewed": True}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error marking order as viewed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update order")

# Get unviewed orders count (for notification badge)
@api_router.get("/orders/unviewed/count")
async def get_unviewed_count():
    try:
        count = await db.orders.count_documents({"viewed": {"$ne": True}, "status": "completed"})
        return {"count": count}
    except Exception as e:
        logging.error(f"Error counting unviewed orders: {str(e)}")
        return {"count": 0}

# Delete order (admin)
@api_router.delete("/orders/{order_id}")
async def delete_order(order_id: str):
    try:
        result = await db.orders.delete_one({"id": order_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {"success": True, "message": "Order deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting order: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete order")

# Update order status (admin)
@api_router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, status: str):
    try:
        if status not in ["pending", "paid", "packed", "shipped", "in_transit", "delivered", "cancelled"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        update_data = {"status": status}
        
        # Set timestamp based on status
        if status == "shipped":
            update_data["shipped_at"] = datetime.now(timezone.utc).isoformat()
        elif status == "delivered":
            update_data["delivered_at"] = datetime.now(timezone.utc).isoformat()
        
        result = await db.orders.update_one(
            {"id": order_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Send customer notification for certain status changes
        if status in ["shipped", "delivered"]:
            order = await db.orders.find_one({"id": order_id})
            if order:
                await send_customer_notification(order, status)
                
        # Send admin notification when delivered
        if status == "delivered":
            order = await db.orders.find_one({"id": order_id})
            if order:
                # Send admin notification about delivery completion
                notification_email = os.environ.get('NOTIFICATION_EMAIL')
                if notification_email:
                    await send_admin_delivery_notification(order)
        
        return {"success": True, "message": "Order status updated"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating order status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update order status")

# Update order tracking info (admin)
@api_router.put("/orders/{order_id}/tracking")
async def update_order_tracking(order_id: str, tracking_number: str, shipping_carrier: str = "DHL"):
    try:
        # Generate tracking URL
        tracking_url = generate_tracking_url(shipping_carrier, tracking_number)
        
        result = await db.orders.update_one(
            {"id": order_id},
            {"$set": {
                "tracking_number": tracking_number,
                "shipping_carrier": shipping_carrier,
                "tracking_url": tracking_url,
                "status": "shipped",
                "shipped_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Send shipping notification to customer
        order = await db.orders.find_one({"id": order_id})
        if order:
            await send_customer_notification(order, 'shipped')
        
        return {"success": True, "tracking_url": tracking_url}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating tracking info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update tracking info")

# Public order tracking
@api_router.get("/track-order")
async def track_order(order_id: str, email: str):
    try:
        order = await db.orders.find_one({"id": order_id, "customer_email": email})
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found or email doesn't match")
        
        # Remove sensitive data
        if '_id' in order:
            del order['_id']
        if isinstance(order.get('created_at'), datetime):
            order['created_at'] = order['created_at'].isoformat()
        if isinstance(order.get('completed_at'), datetime):
            order['completed_at'] = order['completed_at'].isoformat()
        if isinstance(order.get('shipped_at'), datetime):
            order['shipped_at'] = order['shipped_at'].isoformat()
        if isinstance(order.get('delivered_at'), datetime):
            order['delivered_at'] = order['delivered_at'].isoformat()
        
        return order
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error tracking order: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to track order")

# ============= COUPON ENDPOINTS =============

# Get active coupon (public)
@api_router.get("/coupons/active")
async def get_active_coupon():
    try:
        coupon = await db.coupons.find_one({"is_active": True}, {"_id": 0})
        if coupon:
            if isinstance(coupon.get('created_at'), str):
                coupon['created_at'] = datetime.fromisoformat(coupon['created_at'])
            if coupon.get('expires_at') and isinstance(coupon['expires_at'], str):
                coupon['expires_at'] = datetime.fromisoformat(coupon['expires_at'])
        return coupon
    except Exception as e:
        logging.error(f"Error fetching active coupon: {str(e)}")
        return None

# Validate coupon
@api_router.post("/coupons/validate")
async def validate_coupon(request: CouponValidate):
    try:
        coupon = await db.coupons.find_one({"code": request.code.upper(), "is_active": True}, {"_id": 0})
        
        if not coupon:
            raise HTTPException(status_code=404, detail="Invalid coupon code")
        
        # Check expiration
        if coupon.get('expires_at'):
            expires = datetime.fromisoformat(coupon['expires_at']) if isinstance(coupon['expires_at'], str) else coupon['expires_at']
            if expires < datetime.now(timezone.utc):
                raise HTTPException(status_code=400, detail="Coupon has expired")
        
        # Calculate discount
        discount = 0
        if coupon['discount_type'] == 'percentage':
            discount = (request.order_total * coupon['discount_value']) / 100
        else:  # fixed
            discount = coupon['discount_value']
        
        return {
            "valid": True,
            "coupon": {
                "code": coupon['code'],
                "discount_type": coupon['discount_type'],
                "discount_value": coupon['discount_value']
            },
            "discount_amount": round(discount, 2)
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error validating coupon: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to validate coupon")

# Create coupon (admin)
@api_router.post("/coupons")
async def create_coupon(coupon: CouponCreate):
    try:
        # Check if code already exists
        existing = await db.coupons.find_one({"code": coupon.code.upper()})
        if existing:
            raise HTTPException(status_code=400, detail="Coupon code already exists")
        
        coupon_id = str(uuid.uuid4())
        doc = {
            "id": coupon_id,
            "code": coupon.code.upper(),
            "discount_type": coupon.discount_type,
            "discount_value": coupon.discount_value,
            "is_active": coupon.is_active,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": coupon.expires_at.isoformat() if coupon.expires_at else None
        }
        
        await db.coupons.insert_one(doc)
        
        # Return without MongoDB _id
        return {
            "id": coupon_id,
            "code": doc["code"],
            "discount_type": doc["discount_type"],
            "discount_value": doc["discount_value"],
            "is_active": doc["is_active"],
            "created_at": doc["created_at"],
            "expires_at": doc["expires_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating coupon: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create coupon: {str(e)}")

# Get all coupons (admin)
@api_router.get("/coupons")
async def get_all_coupons():
    try:
        coupons = await db.coupons.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
        for coupon in coupons:
            if isinstance(coupon.get('created_at'), str):
                coupon['created_at'] = datetime.fromisoformat(coupon['created_at'])
            if coupon.get('expires_at') and isinstance(coupon['expires_at'], str):
                coupon['expires_at'] = datetime.fromisoformat(coupon['expires_at'])
        return coupons
    except Exception as e:
        logging.error(f"Error fetching coupons: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch coupons")

# Update coupon (admin)
@api_router.put("/coupons/{coupon_id}")
async def update_coupon(coupon_id: str, update: CouponUpdate):
    try:
        update_data = {k: v for k, v in update.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # If code is being updated, check uniqueness
        if 'code' in update_data:
            update_data['code'] = update_data['code'].upper()
            existing = await db.coupons.find_one({"code": update_data['code'], "id": {"$ne": coupon_id}})
            if existing:
                raise HTTPException(status_code=400, detail="Coupon code already exists")
        
        # Convert datetime to string if present
        if 'expires_at' in update_data and update_data['expires_at']:
            update_data['expires_at'] = update_data['expires_at'].isoformat()
        
        result = await db.coupons.update_one(
            {"id": coupon_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Coupon not found")
        
        coupon = await db.coupons.find_one({"id": coupon_id}, {"_id": 0})
        return coupon
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating coupon: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update coupon")

# Delete coupon (admin)
@api_router.delete("/coupons/{coupon_id}")
async def delete_coupon(coupon_id: str):
    try:
        result = await db.coupons.delete_one({"id": coupon_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Coupon not found")
        
        return {"success": True, "message": "Coupon deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting coupon: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete coupon")

# ============= PRODUCT MANAGEMENT ENDPOINTS =============

# Get all products
@api_router.get("/products")
async def get_products():
    try:
        # For now, return hardcoded products (can be made dynamic later)
        products = [
            {"id": "phys-1", "name": "Lion's Mane Extract", "price": 29.99, "description": "Premium quality Lion's Mane mushroom extract for cognitive support", "category": "Supplements", "type": "physical"},
            {"id": "phys-2", "name": "Reishi Capsules", "price": 24.99, "description": "Pure Reishi mushroom capsules for immune system support", "category": "Supplements", "type": "physical"},
            {"id": "phys-3", "name": "Mushroom Growing Kit", "price": 49.99, "description": "Complete kit to grow your own gourmet mushrooms at home", "category": "Kits", "type": "physical"},
            {"id": "phys-4", "name": "Cordyceps Powder", "price": 34.99, "description": "Organic Cordyceps mushroom powder for energy and vitality", "category": "Supplements", "type": "physical"},
            {"id": "digi-1", "name": "Mushroom Identification Guide", "price": 19.99, "description": "Comprehensive digital guide to identifying edible mushrooms", "category": "eBooks", "type": "digital"},
            {"id": "digi-2", "name": "Holistic Health Course", "price": 79.99, "description": "Complete online course on natural wellness and mushroom medicine", "category": "Courses", "type": "digital"},
            {"id": "digi-3", "name": "Meditation & Consciousness Pack", "price": 29.99, "description": "Guided meditations and consciousness expansion exercises", "category": "Audio", "type": "digital"}
        ]
        
        # Also get from database
        db_products = await db.products.find({}, {"_id": 0}).to_list(1000)
        
        # Merge with hardcoded (avoid duplicates by ID)
        existing_ids = [p["id"] for p in db_products]
        for prod in products:
            if prod["id"] not in existing_ids:
                db_products.append(prod)
        
        return db_products
    except Exception as e:
        logging.error(f"Error fetching products: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch products")

# Create product
@api_router.post("/products")
async def create_product(product: dict):
    try:
        # Ensure _id is not in the product dict
        if "_id" in product:
            del product["_id"]
        
        await db.products.insert_one(product)
        
        # Return without MongoDB _id
        return {k: v for k, v in product.items() if k != "_id"}
    except Exception as e:
        logging.error(f"Error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")

# Update product
@api_router.put("/products/{product_id}")
async def update_product(product_id: str, product: dict):
    try:
        result = await db.products.update_one(
            {"id": product_id},
            {"$set": product}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating product: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update product")

# Delete product
@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    try:
        result = await db.products.delete_one({"id": product_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"success": True, "message": "Product deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting product: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete product")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()