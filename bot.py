import os
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from textblob import TextBlob

# SECURITY: Reads the key from GitHub Secrets, not your code
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
WATCHLIST = ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL"]
KEYWORDS = ["earnings", "dividend", "acquisition", "ai", "lawsuit", "growth"]

class MarketAnalyst:
    def __init__(self):
        self.results = []

    def get_sentiment(self, text):
        return round(TextBlob(text).sentiment.polarity, 2)

    def analyze(self, ticker):
        # 1. Price Data (2026 Multi-Index Fix)
        df = yf.download(ticker, period="5d", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        last_price = df['Close'].iloc[-1]
        
        # 2. News & Sentiment
        end = datetime.now().strftime('%Y-%m-%d')
        start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={start}&to={end}&token={FINNHUB_API_KEY}"
        
        news_data = requests.get(url).json()
        total_sentiment, alerts = 0, 0
        
        for item in news_data[:10]:
            headline = item.get('headline', '')
            total_sentiment += self.get_sentiment(headline)
            if any(k in headline.lower() for k in KEYWORDS):
                alerts += 1

        avg_sent = total_sentiment / len(news_data[:10]) if news_data else 0
        
        self.results.append({
            "Ticker": ticker,
            "Price": f"${last_price:.2f}",
            "Sentiment": avg_sent,
            "Alerts": alerts,
            "Mood": "📈 Bullish" if avg_sent > 0.05 else "📉 Bearish" if avg_sent < -0.05 else "↔️ Neutral"
        })

if __name__ == "__main__":
    if not FINNHUB_API_KEY:
        print("❌ Error: FINNHUB_API_KEY environment variable not found.")
    else:
        analyst = MarketAnalyst()
        for stock in WATCHLIST:
            try:
                analyst.analyze(stock)
            except Exception as e:
                print(f"⚠️ Could not process {stock}: {e}")
        
        print(f"\n--- DAILY REPORT: {datetime.now().strftime('%Y-%m-%d')} ---")
        print(pd.DataFrame(analyst.results).to_string(index=False))
