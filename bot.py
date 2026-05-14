import yfinance as yf
import requests
import pandas as pd

# ลิงก์ Discord ของคุณ
URL = "https://discord.com/api/webhooks/1502609125597773874/mclvaofs8FavFZRuItcX68fYAA-65Fi9HN8wSYtCZ4Hmzqy9zGQ5t22Y4KvmMl9tzN3w"
stocks = ["JEPQ", "VOO", "SCHD", "GOOGL", "TSM"]

def run_bot():
    msg = "🤖 *รายงานวิเคราะห์หุ้น (ฉบับแก้ไข)* 📈\n"
    for t in stocks:
        try:
            # ดึงข้อมูลแบบเจาะจงเพื่อลด Error
            data = yf.Ticker(t).history(period="6mo")
            if data.empty: continue

            cur = float(data['Close'].iloc[-1])
            low_20 = float(data['Low'].rolling(window=20).min().iloc[-1])
            
            # คำนวณ RSI แบบง่าย
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]

            msg += f"\n🔍 *{t}*: ${cur:.2f} (RSI: {rsi:.1f})"
            if rsi < 35: msg += " 🔥 *จุดซื้อ!*"
            elif rsi > 70: msg += " ⚠️ *ระวัง!*"
            msg += f"\n🎯 เป้าซื้อ: `${low_20 * 1.01:.2f}`\n"

        except:
            msg += f"\n❌ {t}: Error"
            
    requests.post(URL, json={"content": msg})

if _name_ == "_main_":
    run_bot()
