import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests
import time
from datetime import datetime

TOKEN = ‘8659665684:AAGGHYNzLRQNVRlQdEoYJHJJG-u13_9v0fE’
CHAT_ID = ‘8533718752’

HISSELER = [
“THYAO.IS”,“ASELS.IS”,“TUPRS.IS”,“GARAN.IS”,“AKBNK.IS”,
“KCHOL.IS”,“TCELL.IS”,“BIMAS.IS”,“FROTO.IS”,“EREGL.IS”,
“ISCTR.IS”,“VAKBN.IS”,“YKBNK.IS”,“SAHOL.IS”,“ENKAI.IS”,
“TOASO.IS”,“SISE.IS”,“PETKM.IS”,“TAVHL.IS”,“TTKOM.IS”
]

def telegram(mesaj):
url = f”https://api.telegram.org/bot{TOKEN}/sendMessage”
try:
requests.post(url, json={“chat_id”: CHAT_ID, “text”: mesaj, “parse_mode”: “HTML”}, timeout=10)
except:
print(“Telegram hatasi”)

def analiz(sembol):
try:
df = yf.Ticker(sembol).history(period=“3mo”, interval=“1d”)
if df.empty or len(df) < 30:
return None
df.columns = [c.lower() for c in df.columns]
df[“rsi”] = ta.rsi(df[“close”], length=14)
macd = ta.macd(df[“close”], fast=12, slow=26, signal=9)
df[“macd_hist”] = macd[“MACDh_12_26_9”]
df[“ema20”] = ta.ema(df[“close”], length=20)
df[“hacim_ort”] = df[“volume”].rolling(20).mean()
df = df.dropna()
if len(df) < 2:
return None
son = df.iloc[-1]
onceki = df.iloc[-2]
fiyat = son[“close”]
al = sum([
son[“rsi”] < 35,
onceki[“macd_hist”] < 0 and son[“macd_hist”] > 0,
fiyat > son[“ema20”],
son[“volume”] > son[“hacim_ort”] * 1.2
])
sat = sum([
son[“rsi”] > 65,
onceki[“macd_hist”] > 0 and son[“macd_hist”] < 0,
fiyat < son[“ema20”],
son[“volume”] > son[“hacim_ort”] * 1.2
])
if al >= 3:
return {“sembol”: sembol, “sinyal”: “AL”, “puan”: al, “fiyat”: round(fiyat, 2),
“stop”: round(fiyat * 0.96, 2), “hedef”: round(fiyat * 1.08, 2),
“rsi”: round(son[“rsi”], 1)}
if sat >= 3:
return {“sembol”: sembol, “sinyal”: “SAT”, “puan”: sat, “fiyat”: round(fiyat, 2),
“rsi”: round(son[“rsi”], 1)}
except Exception as e:
print(f”{sembol} hata: {e}”)
return None

def tara():
print(f”\n[{datetime.now().strftime(’%H:%M’)}] Tarama basliyor…”)
al_listesi = []
sat_listesi = []
for s in HISSELER:
sonuc = analiz(s)
if sonuc:
if sonuc[“sinyal”] == “AL”:
al_listesi.append(sonuc)
else:
sat_listesi.append(sonuc)
time.sleep(1)
al_listesi.sort(key=lambda x: x[“puan”], reverse=True)
ozet = f”📊 BIST TARAMA - {datetime.now().strftime(’%d.%m.%Y %H:%M’)}\n”
ozet += f”Taranan: {len(HISSELER)} hisse\n\n”
if al_listesi:
ozet += “🟢 AL SİNYALLERİ:\n”
for s in al_listesi[:5]:
ozet += f”  {s[‘sembol’].replace(’.IS’,’’)} @ {s[‘fiyat’]} TL | RSI:{s[‘rsi’]} | Stop:{s[‘stop’]} | Hedef:{s[‘hedef’]}\n”
else:
ozet += “🟢 AL: Sinyal yok\n”
if sat_listesi:
ozet += “\n🔴 SAT SİNYALLERİ:\n”
for s in sat_listesi[:3]:
ozet += f”  {s[‘sembol’].replace(’.IS’,’’)} @ {s[‘fiyat’]} TL | RSI:{s[‘rsi’]}\n”
telegram(ozet)
print(“Tamamlandi!”)
print(ozet)

if **name** == “**main**”:
telegram(“🤖 BIST Bot baslatildi! Test taramasi yapiliyor…”)
tara()
