# How to Get GitHub OAuth Client ID and Secret

## Step-by-Step Guide

### Step 1: Go to GitHub Developer Settings

1. **Log in to GitHub** (create an account if you don't have one: https://github.com)

2. **Navigate to Developer Settings:**
   - Click your **profile picture** (top right)
   - Click **Settings**
   - Scroll down in the left sidebar
   - Click **Developer settings** (at the bottom)

### Step 2: Create a New OAuth App

1. In Developer settings, click **OAuth Apps** (in the left sidebar)

2. Click the **"New OAuth App"** button (or **"Register a new application"**)

3. Fill in the form:

   **Application name:**
   ```
   Restaverse Scraper (or any name you prefer)
   ```

   **Homepage URL:**
   ```
   http://localhost:5173
   ```

   **Application description (optional):**
   ```
   Real-time web scraper application
   ```

   **Authorization callback URL:**
   ```
   http://localhost:8000/auth/callback
   ```
   ⚠️ **IMPORTANT:** This must match exactly what's in your `.env` file!

4. Click **"Register application"**

### Step 3: Get Your Client ID and Secret

After creating the app, you'll see a page with:

- **Client ID** - This is visible immediately (copy it)
- **Client secret** - Click **"Generate a new client secret"** button to reveal it
  - ⚠️ **Copy it immediately** - you can only see it once!
  - If you lose it, you'll need to generate a new one

### Step 4: Add to Your .env File

Create a `.env` file in your project root (`Restaverse/.env`) and add:

```bash
FRONTEND_ORIGIN=http://localhost:5173

OAUTH_CLIENT_ID=paste_your_client_id_here
OAUTH_CLIENT_SECRET=paste_your_client_secret_here
OAUTH_AUTHORIZE_URL=https://github.com/login/oauth/authorize
OAUTH_TOKEN_URL=https://github.com/login/oauth/access_token
OAUTH_USER_API=https://api.github.com/user
OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback

SESSION_SECRET_KEY=generate-a-long-random-string-here
```

### Quick Reference URLs

- **GitHub OAuth Apps:** https://github.com/settings/developers
- **Create New OAuth App:** https://github.com/settings/developers/new

---

## For Production Deployment

When deploying to production (Vercel/Netlify), you'll need to:

1. **Create a NEW OAuth App** (or update the existing one) with production URLs:
   - **Homepage URL:** `https://your-frontend.vercel.app`
   - **Authorization callback URL:** `https://your-backend.railway.app/auth/callback`

2. **Update your production environment variables** with the new Client ID and Secret

---

## Troubleshooting

### "Redirect URI mismatch" error
- Make sure the callback URL in GitHub matches exactly: `http://localhost:8000/auth/callback`
- Check your `.env` file has the correct `OAUTH_REDIRECT_URI`

### "Invalid client" error
- Verify your Client ID and Secret are correct
- Make sure there are no extra spaces when copying

### Can't see Client Secret
- You can only see it once when you generate it
- If lost, generate a new one from the OAuth App settings page

