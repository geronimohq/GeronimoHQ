# GeronimoHQ CS2 Live Telemetry Relay API

Lightweight Python microservice for querying CS2 Zombie Escape community servers via Valve A2S UDP packets in real time.

## 1-Minute Deploy on Render (Free)

1. Sign in to [render.com](https://render.com) using your GitHub account (`geronimohq`).
2. Click **New +** &rarr; **Web Service**.
3. Select your repository: `geronimohq/GeronimoHQ`.
4. Configure these settings:
   - **Name:** `geronimohq-telemetry`
   - **Root Directory:** (leave blank or `./`)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `uvicorn backend.api:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
5. Click **Create Web Service**.

Once deployed, Render will generate a URL like `https://geronimohq-telemetry.onrender.com`.
The website `https://geronimohq.com` can then fetch `https://geronimohq-telemetry.onrender.com/api/servers` for sub-second live A2S updates!
