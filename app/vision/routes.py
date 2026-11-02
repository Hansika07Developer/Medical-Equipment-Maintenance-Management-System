import re
import cv2
import numpy as np
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from ..models import Equipment

vision_bp = Blueprint("vision", __name__, url_prefix="/vision")

def find_equipment(payload):
    match = re.fullmatch(r"MEMMS-EQUIPMENT:([A-Za-z0-9_-]{1,50})", payload.strip())
    if not match:
        return None
    return Equipment.query.filter_by(asset_code=match.group(1)).first()

@vision_bp.get("/scan")
@login_required
def scan_page():
    return render_template("vision/scan.html")

@vision_bp.post("/lookup")
@login_required
def lookup_qr():
    item = find_equipment(request.form.get("payload", ""))
    if not item:
        return jsonify({"error": "Invalid QR payload or equipment not found"}), 404
    return jsonify({"id": item.id, "asset_code": item.asset_code, "name": item.name,
        "status": item.status, "location": item.location, "category": item.category})

@vision_bp.post("/decode-image")
@login_required
def decode_image():
    uploaded = request.files.get("image")
    if not uploaded:
        return jsonify({"error": "Upload an image file"}), 400
    raw = uploaded.read()
    if not raw or len(raw) > 5 * 1024 * 1024:
        return jsonify({"error": "Image is empty or exceeds 5 MB"}), 400
    image = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        return jsonify({"error": "Invalid image"}), 400
    text, _, _ = cv2.QRCodeDetector().detectAndDecode(image)
    if not text:
        return jsonify({"error": "No QR code detected"}), 404
    item = find_equipment(text)
    if not item:
        return jsonify({"decoded": text, "error": "QR decoded but asset was not found"}), 404
    return jsonify({"decoded": text, "id": item.id, "asset_code": item.asset_code,
        "name": item.name, "status": item.status, "location": item.location})
