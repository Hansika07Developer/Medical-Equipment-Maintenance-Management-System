from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, send_file
from flask_login import login_required
from datetime import date
from io import BytesIO
import qrcode
from ..extensions import db
from ..models import Equipment, Department, AuditLog
from ..permissions import roles_required, log_action

equipment_bp = Blueprint("equipment", __name__, url_prefix="/equipment")
EDIT_ROLES = ("ADMIN", "BIOMEDICAL_ENGINEER")

@equipment_bp.get("/")
@login_required
def list_equipment():
    q = request.args.get("q", "").strip()
    query = Equipment.query
    if q:
        query = query.filter(db.or_(Equipment.asset_code.ilike(f"%{q}%"),
            Equipment.name.ilike(f"%{q}%"), Equipment.serial_number.ilike(f"%{q}%")))
    items = query.order_by(Equipment.name).all()
    return render_template("equipment/list.html", equipment=items, q=q)

@equipment_bp.route("/new", methods=["GET", "POST"])
@roles_required(*EDIT_ROLES)
def create():
    departments = Department.query.order_by(Department.name).all()
    if request.method == "POST":
        code = request.form.get("asset_code", "").strip()
        name = request.form.get("name", "").strip()
        if not code or not name:
            flash("Asset code and name are required.", "danger")
        elif Equipment.query.filter_by(asset_code=code).first():
            flash("Asset code already exists.", "danger")
        else:
            item = Equipment(asset_code=code, name=name,
                category=request.form.get("category"), manufacturer=request.form.get("manufacturer"),
                model=request.form.get("model"), serial_number=request.form.get("serial_number") or None,
                location=request.form.get("location"), status=request.form.get("status", "AVAILABLE"),
                department_id=request.form.get("department_id", type=int) or None,
                maintenance_interval_days=request.form.get("maintenance_interval_days", type=int) or 90)
            db.session.add(item)
            db.session.flush()
            log_action(db, AuditLog, "CREATE_EQUIPMENT", "Equipment", item.id, code)
            db.session.commit()
            flash("Equipment registered.", "success")
            return redirect(url_for("equipment.list_equipment"))
    return render_template("equipment/form.html", item=None, departments=departments)

@equipment_bp.route("/<int:item_id>/edit", methods=["GET", "POST"])
@roles_required(*EDIT_ROLES)
def edit(item_id):
    item = Equipment.query.get_or_404(item_id)
    departments = Department.query.order_by(Department.name).all()
    if request.method == "POST":
        for field in ("name", "category", "manufacturer", "model", "serial_number", "location", "status"):
            setattr(item, field, request.form.get(field) or None)
        item.department_id = request.form.get("department_id", type=int) or None
        item.maintenance_interval_days = request.form.get("maintenance_interval_days", type=int) or 90
        db.session.commit()
        flash("Equipment updated.", "success")
        return redirect(url_for("equipment.list_equipment"))
    return render_template("equipment/form.html", item=item, departments=departments)

@equipment_bp.post("/<int:item_id>/delete")
@roles_required("ADMIN")
def delete(item_id):
    item = Equipment.query.get_or_404(item_id)
    if item.maintenance_records or item.service_requests:
        flash("Cannot delete equipment with maintenance or service history. Retire it instead.", "warning")
    else:
        db.session.delete(item)
        db.session.commit()
        flash("Equipment deleted.", "success")
    return redirect(url_for("equipment.list_equipment"))

@equipment_bp.get("/<int:item_id>/qr.png")
@login_required
def qr_label(item_id):
    item = Equipment.query.get_or_404(item_id)
    img = qrcode.make(f"MEMMS-EQUIPMENT:{item.asset_code}")
    output = BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return send_file(output, mimetype="image/png",
                     download_name=f"{item.asset_code}-qr.png")
