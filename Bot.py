import yfinance as yf
import requests
import time
from datetime import datetime

TOKEN = str(“8659665684:AAGGHYNzLRQNVRlQdEoYJHJJG-u13_9v0fE”)
CHAT_ID = str(“8533718752”)

HISSELER = [
str(“THYAO.IS”),str(“ASELS.IS”),str(“TUPRS.IS”),str(“GARAN.IS”),str(“AKBNK.IS”),
str(“KCHOL.IS”),str(“TCELL.IS”),str(“BIMAS.IS”),str(“FROTO.IS”),str(“EREGL.IS”),
str(“ISCTR.IS”),str(“VAKBN.IS”),str(“YKBNK.IS”),str(“SAHOL.IS”),str(“ENKAI.IS”),
str(“TOASO.IS”),str(“SISE.IS”),str(“PETKM.IS”),str(“TAVHL.IS”),str(“TTKOM.IS”)
]

def tg(m):
try:
url = str(“https://api.telegram.org/bot”) + TOKEN + str(”/sendMessage”)
requests.post(url, json={str(“chat_id”): CHAT_ID, str(“text”): m}, timeout=10)
except Exception as e:
print(str(“Telegram hatasi: “) + str(e))

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
ticker = yf.Ticker(sembol)
df = ticker.history(period=str(“3mo”), interval=str(“1d”))
if df.empty or len(df) < 30:
return None
df.columns = [c.lower() for c in df.columns]
df[str(“rsi”)] = rsi(df[str(“close”)])
df[str(“mh”)] = macd(df[str(“close”)])
df[str(“e20”)] = ema(df[str(“close”)], 20)
df[str(“ho”)] = df[str(“volume”)].rolling(20).mean()
df = df.dropna()
if len(df) < 2:
return None
son = df.iloc[-1]
onceki = df.iloc[-2]
f = son[str(“close”)]
al = sum([
son[str(“rsi”)] < 35,
onceki[str(“mh”)] < 0 and son[str(“mh”)] > 0,
f > son[str(“e20”)],
son[str(“volume”)] > son[str(“ho”)] * 1.2
])
sat = sum([
son[str(“rsi”)] > 65,
onceki[str(“mh”)] > 0 and son[str(“mh”)] < 0,
f < son[str(“e20”)],
son[str(“volume”)] > son[str(“ho”)] * 1.2
])
if al >= 3:
return {
str(“sembol”): sembol.replace(str(”.IS”), str(””)),
str(“sinyal”): str(“AL”),
str(“puan”): al,
str(“fiyat”): round(f, 2),
str(“stop”): round(f * 0.96, 2),
str(“hedef”): round(f * 1.08, 2),
str(“rsi”): round(son[str(“rsi”)], 1)
}
if sat >= 3:
return {
str(“sembol”): sembol.replace(str(”.IS”), str(””)),
str(“sinyal”): str(“SAT”),
str(“puan”): sat,
str(“fiyat”): round(f, 2),
str(“rsi”): round(son[str(“rsi”)], 1)
}
except Exception as e:
print(sembol + str(” hata: “) + str(e))
return None

def tara():
print(str(“Tarama basliyor…”))
al_list = []
sat_list = []
for s in HISSELER:
r = analiz(s)
if r:
if r[str(“sinyal”)] == str(“AL”):
al_list.append(r)
else:
sat_list.append(r)
time.sleep(1)
al_list.sort(key=lambda x: x[str(“puan”)], reverse=True)
msg = str(“BIST TARAMA - “) + datetime.now().strftime(str(”%d.%m.%Y %H:%M”)) + str(”\n”)
msg += str(“Taranan: “) + str(len(HISSELER)) + str(” hisse\n\n”)
if al_list:
msg += str(“AL SINYALLERI:\n”)
for s in al_list[:5]:
msg += s[str(“sembol”)] + str(” @ “) + str(s[str(“fiyat”)]) + str(” TL”)
msg += str(” | RSI:”) + str(s[str(“rsi”)])
msg += str(” | Stop:”) + str(s[str(“stop”)])
msg += str(” | Hedef:”) + str(s[str(“hedef”)]) + str(”\n”)
else:
msg += str(“AL: Sinyal yok\n”)
if sat_list:
msg += str(”\nSAT SINYALLERI:\n”)
for s in sat_list[:3]:
msg += s[str(“sembol”)] + str(” @ “) + str(s[str(“fiyat”)]) + str(” TL”)
msg += str(” | RSI:”) + str(s[str(“rsi”)]) + str(”\n”)
tg(msg)
print(str(“Bitti!”))
print(msg)

tg(str(“Bot baslatildi - “) + datetime.now().strftime(str(”%d.%m.%Y %H:%M”)))
tara()
