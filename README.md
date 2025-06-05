# 🗺️ Spatial Analysis App - Albania

An AI-powered web GIS tool for spatial analysis using Leaflet + Flask + GPT-4.

## 🌍 Country Context: Albania 🇦🇱
The map is centered on Tirana and ready for drawing and spatial queries.

## Features
✅ Draw multiple features  
✅ Run Buffer, Union, or Intersection  
✅ Ask GPT for chained operations like "Buffer and intersect"  
✅ Simple UI with dropdown + natural language input

## 📦 Stack
- **Frontend:** Leaflet, Turf.js, Leaflet.Draw
- **Backend:** Flask + Shapely + OpenAI GPT
- **Deployment:** Vercel (frontend) + Render (backend)

## 🚀 Deployment Steps

### Frontend (Vercel)
1. Deploy the `/frontend` folder using [Vercel](https://vercel.com)
2. Set your API endpoint in `index.html` to your Render backend

### Backend (Render)
1. Deploy `/backend` as a **Web Service**
2. Set environment variable `OPENAI_API_KEY`
3. Use `requirements.txt` and `app.py`

## 📜 License
MIT — Customize for your own projects.