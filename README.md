# Stock Intelligence Dashboard

A comprehensive stock data intelligence platform featuring real-time analytics, REST APIs, interactive visualizations, and ML-powered price predictions.

## Features

- **Real-time Stock Data**: Fetches live data for 15 NSE stocks using yfinance
- **Calculated Metrics**: Daily Return, Closing Price, Opening Price, Moving Averages 7 day, 52-week High/Low, Volatility Score, Momentum Index
- **REST APIs**: FastAPI backend with Swagger documentation
- **Interactive Dashboard**: React frontend with charts, filters, and comparison tools
- **ML Predictions**: XGBoost-based 7-day price forecasting
- **Correlation Analysis**: Heatmap showing stock correlations
- **Light/Dark Mode**: Theme toggle for user preference
- **Docker Support**: Full containerization for easy deployment

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, FastAPI, SQLite, SQLAlchemy |
| Frontend | React, Vite, Recharts |
| ML | XGBoost, scikit-learn |
| Data | yfinance, Pandas, NumPy |
| Deployment | Docker, Docker Compose |

## Project Structure

```
Stock Intelligence Dashboard/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Configuration
│   │   ├── database/            # DB models & connection
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   ├── ml/                  # ML pipeline
│   │   └── schemas/             # Pydantic models
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── hooks/               # Custom hooks
│   │   ├── context/             # React context
│   │   └── services/            # API client
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)

### Option 1: Run with Docker

```bash
docker-compose up --build
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Run Locally

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/companies` | GET | List all companies with current prices |
| `/data/{symbol}` | GET | Historical stock data (query: days) |
| `/summary/{symbol}` | GET | 52-week stats and insights |
| `/compare` | GET | Compare two stocks |
| `/compare/correlation-matrix` | GET | Correlation matrix |
| `/top-movers` | GET | Top gainers and losers |
| `/predict/{symbol}` | GET | ML price prediction |
| `/predict/train` | POST | Train all models |

## Custom Metrics

| Metric | Description |
|--------|-------------|
| Daily Return | (Close - Open) / Open * 100 |
| Volatility Score | 30-day rolling std of returns (0-100) |
| Momentum Index | Price change vs 20 days ago |
| Trend Strength | Position relative to 20-day MA |

## ML Model

- **Algorithm**: XGBoost Regressor
- **Features**: Price lags, moving averages, volume, time features
- **Output**: 7-day price forecast with 95% confidence interval

## Challenges Faced

1. **Rate Limiting**: yfinance API can be rate-limited; implemented caching
2. **Data Gaps**: Weekends/holidays have no data; handled with forward fill
3. **Model Training**: On-demand training when prediction requested
4. **CORS**: Configured for frontend-backend communication

## Future Improvements

- Add more technical indicators (RSI, MACD, Bollinger Bands)
- Implement Redis for distributed caching
- Add user authentication
- Deploy to cloud (Render/Oracle)
- Add real-time WebSocket updates

## Screenshots

The dashboard features:
- Company sidebar with search<img width="2560" height="1278" alt="screencapture-stock-platform-3f3ghlk7q-soumyas-projects-0b365b8b-vercel-app-2025-12-13-18_14_57" src="https://github.com/user-attachments/assets/25642c41-baf1-4f8c-bd0a-fef502e38247" />

- Interactive price charts with moving averages<img width="2560" height="1278" alt="screencapture-stock-platform-3f3ghlk7q-soumyas-projects-0b365b8b-vercel-app-2025-12-13-18_16_28" src="https://github.com/user-attachments/assets/25a3e1a2-b987-4398-a390-282651d2df08" />

- Stock comparison overlay charts<img width="2560" height="1278" alt="screencapture-stock-platform-3f3ghlk7q-soumyas-projects-0b365b8b-vercel-app-compare-2025-12-13-18_17_44" src="https://github.com/user-attachments/assets/abe7f7fd-3be5-4fbe-a61d-0f2b465d713a" />

- Correlation heatmap<img width="2560" height="1278" alt="screencapture-stock-platform-3f3ghlk7q-soumyas-projects-0b365b8b-vercel-app-correlation-2025-12-13-18_19_08" src="https://github.com/user-attachments/assets/242866c3-6644-4a07-94c2-df113620df52" />

- ML prediction with confidence bands<img width="2560" height="1278" alt="screencapture-stock-platform-3f3ghlk7q-soumyas-projects-0b365b8b-vercel-app-predictions-2025-12-13-18_18_25" src="https://github.com/user-attachments/assets/14c800a8-abee-43a7-934a-1f5085be8218" />

- Light/Dark mode toggle

## Author

Soumya Ranjan Patra

## License

MIT
