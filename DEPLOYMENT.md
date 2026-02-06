# Railway Deployment Guide

## Local Development (with .env file)

### 1. Create `.env` file locally

Copy `.env.example` and add your actual credentials:

```bash
copy .env.example .env
# Edit .env with your real values (email, reCAPTCHA keys, PayPal, etc.)
```

**Important:**

- `.env` is in `.gitignore` — never commit it to GitHub
- `.env.example` is the template for reference (commit this)
- Local Django will read `.env` automatically (python-dotenv is installed)

### 2. Install python-dotenv to load .env locally

```bash
pip install python-dotenv
```

Then in `manage.py` or at Django startup, it reads the `.env` file.

---

## Railway Deployment (Environment Variables)

### 1. Push Code to GitHub

```bash
# Ensure .env is NOT committed (it's in .gitignore)
cd c:\example-main\website
git add -A
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. Create Railway Project

1. Go to https://railway.app and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize GitHub and select your repository
5. Railway auto-detects Django

### 3. Add PostgreSQL Database

1. In Railway dashboard, go to your project
2. Click "Plugins" or "+" button
3. Select "PostgreSQL"
4. Railway automatically sets `DATABASE_URL` environment variable

### 4. Set Environment Variables

In Railway project settings → **Variables**, add:

```
SECRET_KEY=django-insecure-your-secret-key-here-use-openssl-rand-hex-32
DEBUG=False
ALLOWED_HOSTS=yourdomain.railway.app,www.yourdomain.railway.app
CSRF_TRUSTED_ORIGINS=https://yourdomain.railway.app,https://www.yourdomain.railway.app

EMAIL_HOST=smtp.gmail.com
EMAIL_FROM=your-email@gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-gmail-app-password
EMAIL_PORT=587
EMAIL_USE_TLS=True

RECAPTCHA_PUBLIC_KEY=your-recaptcha-public-key
RECAPTCHA_PRIVATE_KEY=your-recaptcha-private-key

PAYPAL_RECEIVER_EMAIL=your-paypal-email@gmail.com
PAYPAL_TEST=True
```

**Important Notes:**

- `DATABASE_URL` is auto-set by PostgreSQL plugin, don't add it manually
- For Gmail, use a 16-character App Password, not your regular password
- Generate SECRET_KEY: run `openssl rand -hex 32` in terminal

### 5. Deploy

Railway auto-deploys when you push. The `Procfile` handles:

- Web process: `gunicorn website.wsgi:application`
- Release command: runs migrations + collectstatic

Monitor the deployment in Railway's "Deployment" tab.

### 6. Post-Deployment Setup

Once deployment succeeds, run in Railway:

```bash
railway run python manage.py createsuperuser
```

Then visit your Railway app URL to verify.

### 7. Troubleshooting

- Check logs in Railway → Logs tab
- Verify env vars are set (no typos)
- Confirm PostgreSQL plugin is added
- Ensure SECRET_KEY is set (not empty)

## Local Testing (Optional)

```bash
pip install python-dotenv
# Create .env with your values (copy from .env.example)
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```
