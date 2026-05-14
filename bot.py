import yfinance as yf
import requests
import pandas as pd

# ลิงก์ Discord ของคุณ
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1502609125597773874/mclvaofs8FavFZRuItcX68fYAA-65Fi9HN8wSYtCZ4Hmzqy9zGQ5t22Y4KvmMl9tzN3w"

# รายชื่อหุ้น
stocks = ["JEPQ", "VOO", "SCHD", "GOOGL", "TSM"]

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def run_bot():
    print("⏳ เริ่มการวิเคราะห์หุ้น...")
    full_message = "🤖 **บทวิเคราะห์และการแนะนำจุดเข้าซื้อ** 📈\n"
    
    for ticker in stocks:
        try:
            # ดึงข้อมูลย้อนหลัง 6 เดือน
            df = yf.download(ticker, period="6mo", progress=False)
            if df.empty:
                continue

            # ตรวจสอบโครงสร้างข้อมูล (รองรับ yfinance รูปแบบใหม่)
            if isinstance(df.columns, pd.MultiIndex):
                close_prices = df['Close'][ticker]
                low_prices = df['Low'][ticker]
            else:
                close_prices = df['Close']
                low_prices = df['Low']

            current_price = float(close_prices.iloc[-1])
            monthly_low = float(low_prices.rolling(window=20).min().iloc[-1])
            
            # คำนวณ RSI
            rsi_series = calculate_rsi(close_prices)
            rsi_now = float(rsi_series.iloc[-1])

            full_message += f"\n🔍 **{ticker}** | ราคา: `${current_price:.2f}`\n"
            
            # --- ส่วนการวิเคราะห์ ---
            if rsi_now < 35:
                analysis = "🔥 **จุดซื้อที่ดีมาก!** (Oversold)"
            elif rsi_now < 45:
                analysis = "✅ **น่าสะสม** ราคาเริ่มย่อตัว"
            elif rsi_now > 70:
                analysis = "⚠️ **ระวัง!** (Overbought) ราคาเริ่มแพงไป"
            else:
                analysis = "⏳ **ถือรอ/ดูเชิง** ราคายังอยู่กลางทาง"
            
            full_message += f"   • สถานะ: {analysis}\n"
            full_message += f"   • RSI: `{rsi_now:.1f}`\n"
            
            # แนะนำจุดซื้อ (ต่ำกว่าราคาปัจจุบัน หรือใกล้จุดต่ำสุดเดือน)
            target_entry = monthly_low * 1.01 
            full_message += f"   • 🎯 **จุดเข้าซื้อแนะนำ:** `${target_entry:.2f}`\n"
            
            if current_price <= target_entry:
                full_message += "   🚩 **[ ACTION ]** ราคาถึงจุดที่ควรพิจารณาซื้อ!\n"

        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")
            full_message += f"\n❌ {ticker}: วิเคราะห์ขัดข้อง\n"
            
    # ส่งเข้า Discord
    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": full_message})
    if response.status_code == 204:
        print("✅ ส่งรายงานสำเร็จ!")
    else:
        print(f"❌ ส่งไม่สำเร็จ: {response.status_code}")

if __name__ == "__main__":
    run_bot()
