import os

import smtplib

import yfinance as yf

import pandas as pd

import requests

from email.mime.text import MIMEText

from datetime import datetime, timedelta

from textblob import TextBlob



# SECURITY: These will be set in GitHub Secrets

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

SENDER_EMAIL = os.getenv("SENDER_EMAIL")

SENDER_PASS = os.getenv("SENDER_PASS") # Your 16-char App Password



WATCHLIST = ["AAPL", "NVDA", "TSLA", "MSFT"]

KEYWORDS = ["earnings", "dividend", "acquisition", "ai"]



class StockBot:

    def __init__(self):

        self.report_data = []



    def get_sentiment(self, text):

        return round(TextBlob(text).sentiment.polarity, 2)



    def run_analysis(self):

        for ticker in WATCHLIST:

            # 1. Price

            df = yf.download(ticker, period="5d", interval="1d", progress=False)

            if isinstance(df.columns, pd.MultiIndex):

                df.columns = df.columns.get_level_values(0)

            price = df['Close'].iloc[-1]



            # 2. News

            url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={(datetime.now()-timedelta(days=3)).strftime('%Y-%m-%d')}&to={datetime.now().strftime('%Y-%m-%d')}&token={FINNHUB_API_KEY}"

            news = requests.get(url).json()

            if not isinstance(news, list):

                news = []

            sent_scores = [self.get_sentiment(n.get('headline', '')) for n in news[:5]]

            avg_sent = sum(sent_scores)/len(sent_scores) if sent_scores else 0



            self.report_data.append({

                "Ticker": ticker, "Price": f"${price:.2f}", 

                "Sentiment": avg_sent, "Alerts": len(news[:5])

            })



    def send_email(self):

        df = pd.DataFrame(self.report_data)

        body = f"Daily Market Intelligence Report\n\n{df.to_string(index=False)}"

        msg = MIMEText(body)

        msg['Subject'] = f"📈 Stock Alert: {datetime.now().strftime('%Y-%m-%d')}"

        msg['From'] = SENDER_EMAIL

        msg['To'] = SENDER_EMAIL



        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:

            server.login(SENDER_EMAIL, SENDER_PASS)

            server.send_message(msg)



if __name__ == "__main__":

    bot = StockBot()

    bot.run_analysis()

    bot.send_email()

    print("✅ Analysis complete. Email sent.")
