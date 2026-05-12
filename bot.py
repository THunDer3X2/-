import yfinance as yf
import requests
import pandas as pd

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1502609125597773874/mclvaofs8FavFZRuItcX68fYAA-65Fi9HN8wSYtCZ4Hmzqy9zGQ5t22Y4KvmMl9tzN3w"
stocks = ["JEPQ", "VOO", "SCHD", "GOOGL", "TSM"]

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def run_bot():
    full_message = "🤖 **บทวิเคราะห์และการแนะนำจุดเข้าซื้อ** 📈\n"
    
    for ticker in stocks:
        try:
            # ดึงข้อมูลย้อนหลัง 6 เดือนเพื่อให้คำนวณ RSI ได้แม่นยำ
            df = yf.download(ticker, period="6mo", progress=False)
            if df.empty: continue

            current_price = float(df['Close'].iloc[-1])
            monthly_low = float(df['Low'].rolling(window=20).min().iloc[-1])
            
            # คำนวณ RSI
            df['RSI'] = calculate_rsi(df['Close'])
            rsi_now = float(df['RSI'].iloc[-1])

            full_message += f"\n🔍 **{ticker}** | ราคา: `${current_price:.2f}`\n"
            
            # --- ส่วนการวิเคราะห์ ---
            if rsi_now < 35:
                analysis = "🔥 **จุดซื้อที่ดีมาก!** (Oversold) ราคามีโอกาสดีดกลับสูง"
            elif rsi_now < 45:
                analysis = "✅ **น่าสะสม** ราคาเริ่มย่อตัวลงมาในจุดที่ได้เปรียบ"
            else:
                analysis = "⏳ **ถือรอ/ดูเชิง** ราคายังอยู่กลางทาง ไม่ควรรีบไล่ราคา"
            
            full_message += f"   • สถานะ: {analysis}\n"
            full_message += f"   • RSI: `{rsi_now:.1f}` (ค่าต่ำกว่า 30 คือถูกมาก)\n"
            
            # --- ส่วนการแนะนำจุดเข้าซื้อ ---
            target_entry = monthly_low * 1.01 # แนะนำซื้อที่เหนือกว่าจุดต่ำสุดเดือน 1%
            full_message += f"   • 🎯 **จุดเข้าซื้อแนะนำ:** `${target_entry:.2f}` หรือต่ำกว่า\n"
            
            if current_price <= target_entry:
                full_message += "   🚩 **[ ACTION ]** ราคาถึงจุดซื้อที่แนะนำแล้ว!\n"

        except Exception as e:
            full_message += f"\n❌ {ticker}: วิเคราะห์ขัดข้อง\n"
            
    requests.post(DISCORD_WEBHOOK_URL, json={"content": full_message})

run_bot()
