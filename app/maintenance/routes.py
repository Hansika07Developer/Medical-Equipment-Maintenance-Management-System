from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from ..extensions import db
from ..models import Equipment, Maintenance, ServiceRequest, User, SparePart, PartUsage, AuditLog
from ..permissions import roles_required, log_action

maintenance_bp = Blueprint("maintenance", __name__, url_prefix="/maintenance")
MANAGERS = ("ADMIN", "BIOMEDICAL_ENGINEER")

@maintenance_bp.get("/")
@roles_required("ADMIN", "BIOMEDICAL_ENGINEER", "TECHNICIAN", "MANAGEMENT")
def index():
    records = Maintenance.query.order_by(Maintenance.scheduled_date.desc()).all()
    tickets = ServiceRequest.query.order_by(ServiceRequest.reported_at.desc()).all()
    equipment = Equipment.query.order_by(Equipment.name).all()
    technicians = User.query.filter_by(role="TECHNICIAN", active=True).all()
    return render_template("maintenance/index.html", records=records, tickets=tickets,
                           equipment=equipment, technicians=technicians)

@maintenance_bp.post("/schedule")
@roles_required(*MANAGERS)
def schedule():
    equipment_id = request.form.get("equipment_id", type=int)
    scheduled = request.form.get("scheduled_date")
    if not equipment_id or not scheduled:
        flash("Equipment and scheduled date are required.", "danger")
        return redirect(url_for("maintenance.index"))
    record = Maintenance(equipment_id=equipment_id,
        scheduled_date=date.fromisoformat(scheduled),
        maintenance_type=request.form.get("maintenance_type", "PREVENTIVE"),
        technician_id=request.form.get("technician_id", type=int) or None)
    db.session.add(record)
    db.session.commit()
    flash("Maintenance scheduled.", "success")
    return redirect(url_for("maintenance.index"))

@maintenance_bp.post("/<int:record_id>/complete")
@roles_required("ADMIN", "BIOMEDICAL_ENGINEER", "TECHNICIAN")
def complete(record_id):
    record = Maintenance.query.get_or_404(record_id)
    if current_user.role == "TECHNICIAN" and record.technician_id not in (None, current_user.id):
        return "Not assigned to you", 403
    record.status = "COMPLETED"
    record.completed_date = date.today()
    record.work_description = request.form.get("work_description", "").strip()
    record.downtime_hours = request.form.get("downtime_hours", type=float) or 0
    record.cost = request.form.get("cost", type=float) or 0
    if not record.technician_id:
        record.technician_id = current_user.id
    db.session.commit()
    flash("Maintenance marked completed.", "success")
    return redirect(url_for("maintenance.index"))

@maintenance_bp.post("/breakdown")
@roles_required("ADMIN", "BIOMEDICAL_ENGINEER", "DEPARTMENT_STAFF")
def breakdown():
    equipment_id = request.form.get("equipment_id", type=int)
    issue = request.form.get("issue_description", "").strip()
    if not equipment_id or not issue:
        flash("Select equipment and describe the issue.", "danger")
        return redirect(url_for("maintenance.index"))
    ticket = ServiceRequest(equipment_id=equipment_id, reported_by_id=current_user.id,
        issue_description=issue, priority=request.form.get("priority", "MEDIUM"))
    db.session.add(ticket)
    equipment = db.session.get(Equipment, equipment_id)
    if equipment:
        equipment.status = "UNDER_MAINTENANCE"
    db.session.commit()
    flash("Breakdown request submitted.", "success")
    return redirect(url_for("maintenance.index"))

@maintenance_bp.post("/ticket/<int:ticket_id>/assign")
@roles_required(*MANAGERS)
def assign(ticket_id):
    ticket = ServiceRequest.query.get_or_404(ticket_id)
    tech_id = request.form.get("technician_id", type=int)
    tech = db.session.get(User, tech_id) if tech_id else None
    if not tech or tech.role != "TECHNICIAN":
        flash("Choose a valid technician.", "danger")
    else:
        ticket.assigned_to_id = tech.id
        ticket.status = "ASSIGNED"
        db.session.commit()
        flash("Technician assigned.", "success")
    return redirect(url_for("maintenance.index"))

@maintenance_bp.post("/ticket/<int:ticket_id>/resolve")
@roles_required("ADMIN", "BIOMEDICAL_ENGINEER", "TECHNICIAN")
def resolve(ticket_id):
    ticket = ServiceRequest.query.get_or_404(ticket_id)
    if current_user.role == "TECHNICIAN" and ticket.assigned_to_id != current_user.id:
        return "Not assigned to you", 403
    ticket.status = "RESOLVED"
    ticket.resolved_at = datetime.utcnow()
    ticket.repair_notes = request.form.get("repair_notes", "")
    ticket.downtime_hours = request.form.get("downtime_hours", type=float) or 0
    ticket.equipment.status = "AVAILABLE"
    db.session.commit()
    flash("Breakdown resolved and equipment status updated.", "success")
    return redirect(url_for("maintenance.index"))

@maintenance_bp.post("/ticket/<int:ticket_id>/start")
@roles_required("ADMIN", "BIOMEDICAL_ENGINEER", "TECHNICIAN")
def start(ticket_id):
    ticket = ServiceRequest.query.get_or_404(ticket_id)
    if current_user.role == "TECHNICIAN" and ticket.assigned_to_id != current_user.id:
        return "Not assigned to you", 403
    ticket.status = "IN_PROGRESS"
    ticket.started_at = datetime.utcnow()
    db.session.commit()
    return redirect(url_for("maintenance.index"))

@maintenance_bp.post("/<int:record_id>/use-part")
@roles_required("ADMIN", "BIOMEDICAL_ENGINEER", "TECHNICIAN")
def use_part(record_id):
    record = Maintenance.query.get_or_404(record_id)
    part_id = request.form.get("part_id", type=int)
    qty = request.form.get("quantity", type=int)
    part = SparePart.query.get_or_404(part_id)
    if not qty or qty < 1 or part.quantity < qty:
        flash("Invalid quantity or insufficient stock.", "danger")
    else:
        part.quantity -= qty
        db.session.add(PartUsage(part_id=part.id, maintenance_id=record.id, quantity_used=qty))
        db.session.commit()
        flash("Part usage recorded and stock reduced.", "success")
    return redirect(url_for("maintenance.index"))
