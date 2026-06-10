"""
P7 PROTOCOL — CLOUD SERVER
Deploy this to Render.com (free) — then your iPhone tool calls this URL.
NSE data via yfinance. Works for all Nifty 50 stocks + indices.
"""
import os, traceback
from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
from datetime import datetime

app = Flask(__name__)
CORS(app, origins="*")

NSE_MAP = {
    "NIFTY50":"^NSEI","NIFTY":"^NSEI","BANKNIFTY":"^NSEBANK","SENSEX":"^BSESN",
    "RELIANCE":"RELIANCE.NS","TCS":"TCS.NS","HDFCBANK":"HDFCBANK.NS",
    "ICICIBANK":"ICICIBANK.NS","INFOSYS":"INFY.NS","WIPRO":"WIPRO.NS",
    "SBIN":"SBIN.NS","AXISBANK":"AXISBANK.NS","BAJFINANCE":"BAJFINANCE.NS",
    "KOTAKBANK":"KOTAKBANK.NS","LT":"LT.NS","HINDUNILVR":"HINDUNILVR.NS",
    "ITC":"ITC.NS","BHARTIARTL":"BHARTIARTL.NS","MARUTI":"MARUTI.NS",
    "TITAN":"TITAN.NS","TATAMOTORS":"TATAMOTORS.NS","HCLTECH":"HCLTECH.NS",
    "TATASTEEL":"TATASTEEL.NS","HINDALCO":"HINDALCO.NS","ADANIPORTS":"ADANIPORTS.NS",
    "SUNPHARMA":"SUNPHARMA.NS","BAJAJFINSV":"BAJAJFINSV.NS","DRREDDY":"DRREDDY.NS",
    "DIVISLAB":"DIVISLAB.NS","CIPLA":"CIPLA.NS","ULTRACEMCO":"ULTRACEMCO.NS",
    "NESTLEIND":"NESTLEIND.NS","ONGC":"ONGC.NS","POWERGRID":"POWERGRID.NS",
    "NTPC":"NTPC.NS","COALINDIA":"COALINDIA.NS","JSWSTEEL":"JSWSTEEL.NS",
    "M&M":"M&M.NS","EICHERMOT":"EICHERMOT.NS","HEROMOTOCO":"HEROMOTOCO.NS",
    "BPCL":"BPCL.NS","APOLLOHOSP":"APOLLOHOSP.NS","TECHM":"TECHM.NS",
    "INDUSINDBK":"INDUSINDBK.NS","ASIANPAINT":"ASIANPAINT.NS",
}
def to_yf(s):
    u = s.upper().strip()
    return NSE_MAP.get(u, u if (u.endswith(".NS") or u.startswith("^")) else u+".NS")

@app.route("/")
def home():
    return jsonify({"server":"P7 Protocol","status":"live","time":datetime.now().strftime("%H:%M:%S")})

@app.route("/api/health")
def health():
    return jsonify({"status":"ok","time":datetime.now().strftime("%H:%M:%S")})

@app.route("/api/ohlcv")
def ohlcv():
    sym = request.args.get("symbol","NIFTY50").strip()
    yf_sym = to_yf(sym)
    try:
        t = yf.Ticker(yf_sym)
        h = t.history(period="90d", interval="1d")
        if h is None or h.empty:
            return jsonify({"error":f"No data for '{sym}'. Try: NIFTY50, RELIANCE, HDFCBANK"}), 404
        h = h.dropna(subset=["Close"])
        try: h.index = h.index.tz_localize(None)
        except: h.index = h.index.tz_convert(None)
        closes  = [round(float(x),2) for x in h["Close"]]
        opens   = [round(float(x),2) for x in h["Open"]]
        highs   = [round(float(x),2) for x in h["High"]]
        lows    = [round(float(x),2) for x in h["Low"]]
        volumes = [int(x) for x in h["Volume"]]
        dates   = h.index.strftime("%Y-%m-%d").tolist()
        return jsonify({
            "symbol":sym.upper(),"yf":yf_sym,
            "closes":closes,"opens":opens,"highs":highs,"lows":lows,
            "volumes":volumes,"dates":dates,
            "cur":closes[-1],"prev":closes[-2] if len(closes)>1 else closes[-1],
            "change":round((closes[-1]-closes[-2])/closes[-2]*100,2) if len(closes)>1 else 0,
            "at":datetime.now().strftime("%H:%M"),
        })
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error":str(e)}), 500

@app.route("/api/quote")
def quote():
    sym = request.args.get("symbol","NIFTY50").strip()
    yf_sym = to_yf(sym)
    try:
        t = yf.Ticker(yf_sym)
        h = t.history(period="5d", interval="1d")
        if h is None or h.empty:
            return jsonify({"error":f"No price for '{sym}'"}), 404
        h = h.dropna(subset=["Close"])
        p = round(float(h["Close"].iloc[-1]),2)
        return jsonify({"symbol":sym.upper(),"price":p,"at":datetime.now().strftime("%H:%M")})
    except Exception as e:
        return jsonify({"error":str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"P7 Server starting on port {port}")
    app.run(host="0.0.0.0", port=port)
