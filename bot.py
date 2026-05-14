import yfinance as yf
import requests
import pandas as pd

# ลิงก์ Discord ของคุณ
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1502609125597773874/mclvaofs8FavFZRuItcX68fYAA-65Fi9HN8wSYtCZ4Hmzqy9zGQ5t22Y4KvmMl9tzN3w"

# รายชื่อหุ้นที่ต้องการ
stocks = ["JEPQ", "VOO", "SCHD", "GOOGL", "TSM"]

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def run_bot():
    full_message = "🤖 *บทวิเคราะห์และการแนะนำจุดเข้าซื้อ* 📈\n"
    
    for ticker in stocks:
        try:
            # ดึงข้อมูลย้อนหลัง
            df = yf.download(ticker, period="6mo", progress=False)
            if df.empty: continue

            # ดึงราคาปิดปัจจุบัน
            current_price = float(df['Close'].iloc[-1])
            monthly_low = float(df['Low'].rolling(window=20).min().iloc[-1])
            
            # คำนวณ RSI
            df['RSI'] = calculate_rsi(df['Close'])
            rsi_now = float(df['RSI'].iloc[-1])

            full_message += f"\n🔍 *{ticker}* | ราคา: `${current_price:.2f}`\n"
            
            # วิเคราะห์ด้วย RSI
            if rsi_now < 35:
                analysis = "🔥 *จุดซื้อที่ดีมาก!* (Oversold)"
            elif rsi_now < 45:
                analysis = "✅ *น่าสะสม* ราคาเริ่มย่อตัว"
            elif rsi_now > 70:
                analysis = "⚠️ *ระวัง!* (Overbought) อย่าเพิ่งรีบไล่ราคา"
            else:
                analysis = "⏳ *ถือรอ/ดูเชิง* ราคายังอยู่กลางทาง"
            
            full_message += f"   • สถานะ: {analysis}\n"
            full_message += f"   • RSI: `{rsi_now:.1f}`\n"
            
            # แนะนำจุดซื้อ
            target_entry = monthly_low * 1.01 
            full_message += f"   • 🎯 *จุดเข้าซื้อแนะนำ:* `${target_entry:.2f}`\n"
            
            if current_price <= target_entry:
                full_message += "   🚩 *[ ACTION ]* ราคาถึงจุดซื้อที่แนะนำแล้ว!\n"

        except Exception as e:
            full_message += f"\n❌ {ticker}: วิเคราะห์ขัดข้อง\n"
            
    # ส่งข้อมูลเข้า Discord
    requests.post(DISCORD_WEBHOOK_URL, json={"content": full_message})

if _name_ == "_main_":
    run_bot()
