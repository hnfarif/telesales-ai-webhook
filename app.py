# app.py
import os
import json
import subprocess
import logging
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "WEBHOOK_TOKEN")

def run_your_program(phone: str, wacid: str):
    """
    Ganti implementasi ini sesuai kebutuhan:
    - Panggil Flow webMethods melalui HTTP
    - Menjalankan script Python/Java
    - Publish ke message bus, dsb.
    """
    # Contoh: jalankan script lokal dengan argumen
    subprocess.run(
        ["python", "your_program.py", "--phone", phone, "--wacid", wacid],
        check=False,
    )

@app.get("/webhooks/whatsapp")
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(challenge or "", status=200, mimetype="text/html")
    return Response("Forbidden", status=403)

@app.post("/webhooks/whatsapp")
def handle():
    raw = request.get_data(as_text=True) or ""
    app.logger.info("WEBHOOK RAW BODY: %s", raw)   # << tampil di Deploy Logs

    payload = request.get_json(silent=True) or {}

    # contoh ekstraksi status WhatsApp (sesuai dok):
    try:
        change = payload["entry"][0]["changes"][0]
        value  = change.get("value", {})
        statuses = value.get("statuses") or []
        if statuses:
            app.logger.info("STATUSES: %s", json.dumps(statuses, ensure_ascii=False))
            # ambil status pertama
            s = statuses[0]
            # contoh field umum: s["status"], s["id"] (wamid), s["timestamp"], s.get("errors")
    except Exception as e:
        app.logger.warning("Parse webhook failed: %s", e)

    return Response(status=200)
    
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
