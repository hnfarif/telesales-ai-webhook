# app.py
import os
import json
import subprocess
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
        # WAJIB balas hub.challenge persis dalam body (HTTP 200)
        return Response(challenge or "", status=200, mimetype="text/html")
    return Response("Forbidden", status=403)

@app.post("/webhooks/whatsapp")
def handle():
    payload = request.get_json(force=True, silent=True) or {}
    # ——— Parsers umum:
    # a) Format “calls” Cloud API (akan datang di field webhook WhatsApp Business).
    # b) Format provider (contoh: YCloud) type=whatsapp.call.status.updated
    #
    # Contoh payload YCloud (disederhanakan):
    # { "type":"whatsapp.call.status.updated",
    #   "callingStatusUpdated": { "status":"ACCEPTED", "wacid":"...", "recipientPhone":"+62..." } }
    #
    # Kamu bisa buat parser fleksibel seperti ini:
    evt_type = payload.get("type")
    if evt_type == "whatsapp.call.status.updated":
        info = payload.get("callingStatusUpdated", {})
        status = (info.get("status") or "").upper()
        phone  = info.get("recipientPhone") or ""
        wacid  = info.get("wacid") or ""
        if status in ("ACCEPTED", "ACTIVE"):
            run_your_program(phone, wacid)

    # (Opsional) Tambahkan parser alternatif jika kamu menerima struktur Cloud API langsung.
    # Lihat panduan webhook WhatsApp Business Platform. :contentReference[oaicite:2]{index=2}

    return jsonify(ok=True)
    
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
