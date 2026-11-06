# 🌐 GeronimoHQ (geronimohq.com) Deployment & Porkbun DNS Guide

This guide walks you through deploying **GeronimoHQ** to production for free with automated SSL and connecting your **Porkbun** domain (`geronimohq.com`).

---

## ⚡ Option 1: Vercel (Recommended — Fastest 1-Click Setup)

1. Push your repository to **GitHub** (or run `npx vercel` in this folder).
2. Go to [vercel.com](https://vercel.com) and click **"Add New Project"** -> import `GeronimoHQ`.
3. Vercel automatically detects **Vite**:
   - **Framework Preset:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Click **Deploy**. Your site will be live on a `*.vercel.app` URL within ~30 seconds.
5. In your Vercel Project Settings:
   - Go to **Settings** &rarr; **Domains**.
   - Add `geronimohq.com` and `www.geronimohq.com`.

---

## 🐷 Porkbun DNS Records for `geronimohq.com`

Log in to your **[Porkbun Dashboard](https://porkbun.com)**, click **Details** next to `geronimohq.com`, then click **DNS Records** (Edit).

Enter the following 2 DNS records:

| Type | Host / Subdomain | Answer / Points To | TTL | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **A** | `@` (leave blank or enter `@`) | `76.76.21.21` | `600` | Points root domain `geronimohq.com` to Vercel global edge |
| **CNAME** | `www` | `cname.vercel-dns.com` | `600` | Points `www.geronimohq.com` to Vercel |

*(If Porkbun already has default parked "ALIASEX" or parked "A" records pointing to Porkbun parking IPs, delete or replace them with the records above).*

### 🔒 SSL Certificate
Once you save the records, Vercel will automatically verify DNS propagation and issue a free **Let's Encrypt Wildcard SSL** certificate. It usually takes between **2 to 15 minutes** to propagate worldwide.

---

## ☁️ Option 2: Cloudflare Pages

If you prefer Cloudflare Pages:
1. Go to [dash.cloudflare.com](https://dash.cloudflare.com) &rarr; **Workers & Pages** &rarr; **Create application** &rarr; **Pages**.
2. Connect your Git repository.
3. Build Settings:
   - **Framework preset:** `Vite`
   - **Build command:** `npm run build`
   - **Build output directory:** `dist`
4. In **Custom Domains**, add `geronimohq.com`.
5. If using Porkbun nameservers with Cloudflare Pages, add:
   - **CNAME** `@` &rarr; `<your-project>.pages.dev`
   - **CNAME** `www` &rarr; `<your-project>.pages.dev`

---

## 🛠️ Local Development & Scripts

- **Start Dev Server:** `npm run dev` (Runs at `http://localhost:5173`)
- **Production Build:** `npm run build` (Outputs clean bundle to `dist/`)
- **Preview Production Build:** `npm run preview`
