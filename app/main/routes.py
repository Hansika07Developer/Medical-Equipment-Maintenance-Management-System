from datetime import date
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models import Equipment, Maintenance, ServiceRequest, SparePart

main_bp = Blueprint("main", __name__)

@main_bp.get("/")
def index():
    from flask import redirect, url_for
    return redirect(url_for("main.dashboard"))

@main_bp.get("/dashboard")
@login_required
def dashboard():
    today = date.today()
    equipment_count = Equipment.query.count()
    available_count = Equipment.query.filter_by(status="AVAILABLE").count()
    due = Maintenance.query.filter(Maintenance.status == "SCHEDULED",
                                   Maintenance.scheduled_date <= today).count()
    open_tickets = ServiceRequest.query.filter(
        ServiceRequest.status.in_(["OPEN", "ASSIGNED", "IN_PROGRESS"])).count()
    low_stock = SparePart.query.filter(SparePart.quantity <= SparePart.minimum_stock).count()
    recent = ServiceRequest.query.order_by(ServiceRequest.reported_at.desc()).limit(6).all()
    upcoming = Maintenance.query.filter(Maintenance.status == "SCHEDULED").order_by(
        Maintenance.scheduled_date).limit(6).all()
    return render_template("dashboard.html", equipment_count=equipment_count,
        available_count=available_count, due=due, open_tickets=open_tickets,
        low_stock=low_stock, recent=recent, upcoming=upcoming)
