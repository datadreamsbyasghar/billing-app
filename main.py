import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext

# Import routers directly from routes folder (since you run inside backend/)
from routes import auth, products, bills, clients, analytics, export, invoice

# Import DB setup from database.py
from database import Base, engine

# -----------------------------
# Config
# -----------------------------
SECRET_KEY = os.getenv("BILLING_SECRET_KEY", "CHANGE_ME_STRONG_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "120"))

DEFAULT_ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@12345")

# -----------------------------
# App setup
# -----------------------------
app = FastAPI(title="Billing App", version="1.0.0")

# Mount routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(bills.router)
app.include_router(clients.router)
app.include_router(analytics.router)
app.include_router(export.router)
app.include_router(invoice.router)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict to frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Create tables on startup
# -----------------------------
Base.metadata.create_all(bind=engine)