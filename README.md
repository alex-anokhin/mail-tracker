# 📨 FastAPI Email Gateway with MCP Tool Support

Send emails with open & click tracking, log stats to SQLite, and now with full MCP tool integration—all powered by FastAPI.

---

## 🚀 Features

- ✅ MCP tool support for advanced email processing
- ✅ Send HTML emails with tracking pixel
- ✅ Track opens and clicks via `/api/track/`
- ✅ SQLite database logging
- ✅ Auth-protected endpoints
- ✅ Beautiful `/docs`
- ✅ Custom SMTP configuration via `.env`
- ✅ Dockerized for easy deployment

---

## 📦 Setup

### 1. Clone & configure

```bash
git clone https://github.com/your-user/email-tracker.git
cd email-tracker
cp .env.example .env
# edit .env to set SMTP and app credentials
```

### 2. Run with Docker
```bash
docker compose up --build
```
Open: http://localhost:8000/docs

## 📬 Send Email

Send to one or more recipients (comma-separated):

```bash
curl -X POST http://localhost:8000/api/send-email \
	-u admin:supersecret \
	-F "to=someone@example.com,another@example.com" \
	-F "subject=Hello" \
	-F "body=This is a test"
```

## 📊 View Stats

Open `/stats` in your browser or call:

```bash
curl -u admin:supersecret http://localhost:8000/api/stats
```

## 📂 Database

- `emails.db` is used for logging emails and events.
- Inspect with tools like `sqlitebrowser`.

## 🛡 Security Note

Always use a secure SMTP provider and rotate your credentials. Never commit sensitive information.

## 📄 License

MIT License

