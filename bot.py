import yfinance as yf
import requests
import pandas as pd

# ⚠️ อย่าลืมใส่ Webhook URL ของคุณเองตรงนี้ครับ
DISCORD_WEBHOOK_URL = "ใส่_WEBHOOK_URL_ของคุณที่นี่"

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
    full_message = "🤖 **รายงานวิเคราะห์หุ้นฉบับเต็ม (ไต้หวัน)** 🇹🇼\n"
    
    for ticker in stocks:
        try:
            # ดึงข้อมูลย้อนหลัง 3 เดือนเพื่อให้ครอบคลุมการคำนวณทั้งหมด
            df = yf.download(ticker, period="3mo", progress=False)
            if df.empty: continue

            current_price = float(df['Close'].iloc[-1])
            
            # คำนวณราคาต่ำสุด
            weekly_low = float(df['Low'].rolling(window=5).min().iloc[-1])
            monthly_low = float(df['Low'].rolling(window=20).min().iloc[-1])
            
            # คำนวณ RSI
            df['RSI'] = calculate_rsi(df['Close'])
            rsi_now = float(df['RSI'].iloc[-1])

            full_message += f"\n🔍 **{ticker}** | `${current_price:.2f}`\n"
            full_message += f"   • ต่ำสุดสัปดาห์: `${weekly_low:.2f}`\n"
            full_message += f"   • ต่ำสุดเดือน: `${monthly_low:.2f}`\n"
            
            # วิเคราะห์สถานะ
            if rsi_now < 35:
                status = "🔥 **จุดซื้อที่ดี!** (Oversold)"
            elif rsi_now < 45:
                status = "✅ **น่าสะสม**"
            elif rsi_now > 70:
                status = "⚠️ **ราคาตึงเกินไป**"
            else:
                status = "⏳ **ถือรอ**"
            
            full_message += f"   • วิเคราะห์: {status} (RSI: `{rsi_now:.1f}`)\n"
            
            # แนะนำจุดรับ (2% เหนือจุดต่ำสุดเดือน)
            target = monthly_low * 1.02
            full_message += f"   • 🎯 เป้าหมายตั้งรับ: `${target:.2f}`\n"

        except Exception as e:
            print(f"Error {ticker}: {e}")

    requests.post(DISCORD_WEBHOOK_URL, json={"content": full_message})

if __name__ == "__main__":
    run_bot()
