import yfinance as yf
import requests

# ลิงก์ Discord ของคุณ
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1502609125597773874/mclvaofs8FavFZRuItcX68fYAA-65Fi9HN8wSYtCZ4Hmzqy9zGQ5t22Y4KvmMl9tzN3w"

# รายชื่อหุ้นของคุณ
stocks = ["JEPQ", "VOO", "SCHD", "GOOGL", "TSM"]

def run_bot():
    print("⏳ กำลังสรุปราคาหุ้นให้ครับ...")
    full_message = "🚀 **รายงานสถานะหุ้นของคุณ** 🚀\n"
    
    for ticker in stocks:
        try:
            # ดึงข้อมูล 1 เดือน
            df = yf.download(ticker, period="1mo", progress=False)
            
            if not df.empty:
                # ดึงค่าราคาปิดล่าสุด และค่าต่ำสุด
                current_price = float(df['Close'].iloc[-1])
                monthly_low = float(df['Low'].min())
                weekly_low = float(df['Low'].tail(5).min())
                
                full_message += f"\n📌 **{ticker}**\n"
                full_message += f"   • ราคาปัจจุบัน: `${current_price:.2f}`\n"
                full_message += f"   • ต่ำสุดรอบสัปดาห์: `${weekly_low:.2f}`\n"
                full_message += f"   • ต่ำสุดรอบเดือน: `${monthly_low:.2f}`\n"
                
                # ถ้าราคาปัจจุบันห่างจากจุดต่ำสุดไม่เกิน 2% ให้เตือน
                if current_price <= (monthly_low * 1.02):
                    full_message += "   ⚠️ **ราคาลงมาใกล้จุดต่ำสุดรอบเดือนแล้ว!**\n"
            
        except Exception as e:
            full_message += f"\n❌ หุ้น {ticker}: ดึงข้อมูลไม่ได้ชั่วคราว\n"
            
    # ส่งเข้า Discord
    requests.post(DISCORD_WEBHOOK_URL, json={"content": full_message})
    print("✅ ข้อมูลส่งเข้า Discord เรียบร้อยแล้ว! ลองไปเช็กดูได้เลยครับ")

# เริ่มรัน
run_bot()
