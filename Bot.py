import requests
import yfinance as yf
import time
from datetime import datetime

TOKEN = "8659665684:AAGGHYNzLRQNVRlQdEoYJHJJG-u13_9v0fE"
CHAT_ID = "8533718752"

HISSELER = [
    "THYAO.IS","ASELS.IS","TUPRS.IS","GARAN.IS","AKBNK.IS",
    "KCHOL.IS","TCELL.IS","BIMAS.IS","FROTO.IS","EREGL.IS",
    "ISCTR.IS","VAKBN.IS","YKBNK.IS","SAHOL.IS","ENKAI.IS",
    "TOASO.IS","SISE.IS","PETKM.IS","TAVHL.IS","TTKOM.IS"
]

def tg(m):
    try:
        requests.post(
            "https://api.telegram.org/bot" + TOKEN + "/sendMessage",
            json={"chat_id": CHAT_ID, "text": m},
            timeout=10
        )
    except Exception as e:
        print("Telegram hatasi: " + str(e))

def rsi(seri, period=14):
    delta = seri.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def ema(seri, period):
    return seri.ewm(span=period, adjust=False).mean()

def macd(seri):
    e12 = ema(seri, 12)
    e26 = ema(seri, 26)
    m = e12 - e26
    s = ema(m, 9)
    return m - s

def analiz(sembol):
    try:
        df = yf.Ticker(sembol).history(period="3mo", interval="1d")
        if df.empty or len(df) < 30:
            return None
        df.columns = [c.lower() for c in df.columns]
        df["rsi"] = rsi(df["close"])
        df["mh"] = macd(df["close"])
        df["e20"] = ema(df["close"], 20)
        df["ho"] = df["volume"].rolling(20).mean()
        df = df.dropna()
        if len(df) < 2:
            return None
        son = df.iloc[-1]
        onceki = df.iloc[-2]
        f = son["close"]
        al = sum([
            son["rsi"] < 35,
            onceki["mh"] < 0 and son["mh"] > 0,
            f > son["e20"],
            son["volume"] > son["ho"] * 1.2
        ])
        sat = sum([
            son["rsi"] > 65,
            onceki["mh"] > 0 and son["mh"] < 0,
            f < son["e20"],
            son["volume"] > son["ho"] * 1.2
        ])
        if al >= 3:
            return {
                "sembol": sembol.replace(".IS", ""),
                "sinyal": "AL",
                "puan": al,
                "fiyat": round(f, 2),
                "stop": round(f * 0.96, 2),
                "hedef": round(f * 1.08, 2),
                "rsi": round(son["rsi"], 1)
            }
        if sat >= 3:
            return {
                "sembol": sembol.replace(".IS", ""),
                "sinyal": "SAT",
                "puan": sat,
                "fiyat": round(f, 2),
                "rsi": round(son["rsi"], 1)
            }
    except Exception as e:
        print(sembol + " hata: " + str(e))
    return None

def tara():
    print("Tarama basliyor...")
    al_list = []
    sat_list = []
    for s in HISSELER:
        r = analiz(s)
        if r:
            if r["sinyal"] == "AL":
                al_list.append(r)
            else:
                sat_list.append(r)
        time.sleep(1)

    al_list.sort(key=lambda x: x["puan"], reverse=True)

    msg = "BIST TARAMA - " + datetime.now().strftime("%d.%m.%Y %H:%M") + "\n"
    msg += "Taranan: " + str(len(HISSELER)) + " hisse\n\n"

    if al_list:
        msg += "AL SINYALLERI:\n"
        for s in al_list[:5]:
            msg += s["sembol"] + " @ " + str(s["fiyat"]) + " TL"
            msg += " | RSI:" + str(s["rsi"])
            msg += " | Stop:" + str(s["stop"])
            msg += " | Hedef:" + str(s["hedef"]) + "\n"
    else:
        msg += "AL: Sinyal yok\n"

    if sat_list:
        msg += "\nSAT SINYALLERI:\n"
        for s in sat_list[:3]:
            msg += s["sembol"] + " @ " + str(s["fiyat"]) + " TL"
            msg += " | RSI:" + str(s["rsi"]) + "\n"

    tg(msg)
    print("Bitti!")
    print(msg)

tg("Bot baslatildi - " + datetime.now().strftime("%d.%m.%Y %H:%M"))
tara()
