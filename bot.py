import yfinance as yf
import requests
import pandas as pd

# เปลี่ยนเป็น Webhook URL ของคุณเอง
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1502609125597773874/mclvaofs8FavFZRuItcX68fYAA-65Fi9HN8wSYtCZ4Hmzqy9zGQ5t22Y4KvmMl9tzN3w" 

stocks = ["JEPQ", "VOO", "SCHD", "GOOGL", "TSM"]

def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def run_bot():
    full_message = "🤖 **รายงานวิเคราะห์หุ้น (ไต้หวัน)** 🇹🇼\n"
    
    for ticker in stocks:
        try:
            df = yf.download(ticker, period="2mo", progress=False)
            if df.empty: continue

            current_price = float(df['Close'].iloc[-1])
            df['RSI'] = calculate_rsi(df['Close'])
            rsi_now = float(df['RSI'].iloc[-1])

            full_message += f"\n🔍 **{ticker}** | `${current_price:.2f}`\n"
            
            if rsi_now < 35:
                status = "🔥 **จุดซื้อที่ดี!** (Oversold)"
            elif rsi_now < 45:
                status = "✅ **น่าสะสม**"
            else:
                status = "⏳ **ถือรอ**"
            
            full_message += f"   • สถานะ: {status} (RSI: `{rsi_now:.1f}`)\n"

        except Exception as e:
            print(f"Error {ticker}: {e}")

    requests.post(DISCORD_WEBHOOK_URL, json={"content": full_message})

if __name__ == "__main__":
    run_bot()
