import os

API_USER = os.getenv("API_USER", "admin")
API_PASS = os.getenv("API_PASS", "secret")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.example.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
IMAP_HOST = os.getenv("IMAP_HOST", "imap.example.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", 993))
EMAIL_USER = os.getenv("EMAIL_USER", "your_email@example.com")
EMAIL_PASS = os.getenv("EMAIL_PASS", "your_password")
TRACKING_DOMAIN = os.getenv("TRACKING_DOMAIN", "http://localhost:8000")
DB_PATH = os.getenv("DB_PATH", "emails.db")