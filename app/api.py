from fastapi import APIRouter, Form, Depends, Query
from fastapi.responses import Response, RedirectResponse
import aiosmtplib
from email.message import EmailMessage
import imaplib
import email
import uuid
from datetime import datetime
from urllib.parse import unquote
from typing import List
from models import EmailRequest, EventResponse, EmailResponse, EmailStr
from config import *
from db import get_cursor, get_conn
from utils import wrap_links, get_body, extract_email
from auth import authenticate

router = APIRouter(prefix="/api", tags=["API"])

cursor = get_cursor()
conn = get_conn()

@router.post("/send-email", summary="📧 Send tracked email", description="Sends an email and adds an open tracking pixel. Optionally track clicks via /track/click.")
async def send_email(
    to: EmailStr = Form(..., description="Recipient email address"),
    subject: str = Form(..., description="Email subject"),
    body: str = Form(..., description="Plain text content of the email"),
    user: str = Depends(authenticate)
):
    email_id = str(uuid.uuid4())
    html_body_content = wrap_links(body, email_id, TRACKING_DOMAIN)
    html_body = f"""
<html>
  <body>
    <p>{html_body_content}</p>
    <img src="{TRACKING_DOMAIN}/api/track/open?email_id={email_id}" width="1" height="1" style="display:none">
  </body>
</html>
"""
    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    msg.add_alternative(html_body, subtype="html")

    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=EMAIL_USER,
        password=EMAIL_PASS,
        start_tls=True,
    )

    cursor.execute(
        "INSERT INTO emails (email_id, direction, from_addr, to_addr, subject, body, sent_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (email_id, 'sent', EMAIL_USER, to, subject, body, datetime.utcnow().isoformat())
    )
    conn.commit()
    return {"status": "sent", "email_id": email_id}

@router.get("/track/open", summary="📈 Track email open (invisible pixel)")
def track_open(email_id: str = Query(..., description="The UUID of the tracked email")):
    cursor.execute("INSERT INTO events (email_id, event_type, url, timestamp) VALUES (?, 'open', '', ?)",
                   (email_id, datetime.utcnow().isoformat()))
    conn.commit()
    transparent_pixel = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
        b'\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x00\x00\x00'
        b'\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
        b'\x44\x01\x00\x3B'
    )
    return Response(content=transparent_pixel, media_type="image/gif")

@router.get("/track/click", summary="🔗 Track email click and redirect")
def track_click(
    email_id: str = Query(..., description="The UUID of the tracked email"),
    url: str = Query(..., description="Target URL to redirect to")
):
    decoded_url = unquote(url)
    cursor.execute("INSERT INTO events (email_id, event_type, url, timestamp) VALUES (?, 'click', ?, ?)",
                   (email_id, decoded_url, datetime.utcnow().isoformat()))
    conn.commit()
    return RedirectResponse(decoded_url)

@router.get("/stats", response_model=List[EventResponse], summary="📊 Get open/click event stats", description="Returns a list of tracked opens and clicks.")
def get_stats(user: str = Depends(authenticate)):
    cursor.execute("SELECT email_id, event_type, url, timestamp FROM events ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    return [{"email_id": r[0], "event": r[1], "url": r[2], "timestamp": r[3]} for r in rows]

@router.get("/receive-emails", summary="📥 Fetch and store recent received emails", description="Uses IMAP to fetch and store the last 5 emails from inbox.")
def receive_emails(user: str = Depends(authenticate)):
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")
    result, data = mail.search(None, "ALL")
    mail_ids = data[0].split()
    emails = []
    for num in mail_ids[-5:]:
        result, data = mail.fetch(num, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)
        from_addr_raw = msg["From"]
        from_addr = extract_email(from_addr_raw)
        to_addr = EMAIL_USER
        subject = msg["Subject"]
        body = get_body(msg)
        timestamp = msg["Date"]
        email_id = msg["Message-ID"]

        # Insert into DB if not already present
        cursor.execute(
            "SELECT 1 FROM emails WHERE email_id = ? AND direction = 'received'",
            (email_id,)
        )
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO emails (email_id, direction, from_addr, to_addr, subject, body, sent_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (email_id, 'received', from_addr, to_addr, subject, body, timestamp)
            )
            conn.commit()
        emails.append({
            "from": from_addr,
            "subject": subject,
            "body": body,
            "timestamp": timestamp,
            "email_id": email_id
        })
    mail.logout()
    return {"emails": emails}

@router.get("/conversation", response_model=List[EmailResponse], summary="Get conversation with a correspondent")
def get_conversation(
    email: EmailStr = Query(..., description="The correspondent's email address"),
    user: str = Depends(authenticate)
):
    cursor.execute(
        """
        SELECT email_id, direction, from_addr, to_addr, subject, body, sent_at
        FROM emails
        WHERE (from_addr = ? AND to_addr = ?)
           OR (from_addr = ? AND to_addr = ?)
        ORDER BY sent_at ASC
        """,
        (EMAIL_USER, email, email, EMAIL_USER)
    )
    rows = cursor.fetchall()
    return [
        EmailResponse(
            email_id=r[0],
            direction=r[1],
            from_addr=r[2],
            to_addr=r[3],
            subject=r[4],
            body=r[5],
            sent_at=r[6]
        )
        for r in rows
    ]
