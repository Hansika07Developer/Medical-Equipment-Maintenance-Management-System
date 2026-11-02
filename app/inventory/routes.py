from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..extensions import db
from ..models import SparePart
from ..permissions import roles_required

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")

@inventory_bp.get("/")
@roles_required("ADMIN", "BIOMEDICAL_ENGINEER", "TECHNICIAN", "MANAGEMENT")
def index():
    parts = SparePart.query.order_by(SparePart.part_name).all()
    return render_template("inventory/index.html", parts=parts)

@inventory_bp.post("/add")
@roles_required("ADMIN", "BIOMEDICAL_ENGINEER")
def add():
    code = request.form.get("part_code", "").strip()
    name = request.form.get("part_name", "").strip()
    if not code or not name or SparePart.query.filter_by(part_code=code).first():
        flash("Provide a unique part code and part name.", "danger")
    else:
        db.session.add(SparePart(part_code=code, part_name=name,
            quantity=request.form.get("quantity", type=int) or 0,
            minimum_stock=request.form.get("minimum_stock", type=int) or 5,
            unit_price=request.form.get("unit_price", type=float) or 0))
        db.session.commit()
        flash("Spare part added.", "success")
    return redirect(url_for("inventory.index"))

@inventory_bp.post("/<int:part_id>/adjust")
@roles_required("ADMIN", "BIOMEDICAL_ENGINEER")
def adjust(part_id):
    part = SparePart.query.get_or_404(part_id)
    delta = request.form.get("delta", type=int)
    if delta is None or part.quantity + delta < 0:
        flash("Stock adjustment would result in invalid stock.", "danger")
    else:
        part.quantity += delta
        db.session.commit()
        flash("Stock updated.", "success")
    return redirect(url_for("inventory.index"))
