from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="DEPARTMENT_STAFF")
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    location = db.Column(db.String(150))

class Equipment(db.Model):
    __tablename__ = "equipment"
    id = db.Column(db.Integer, primary_key=True)
    asset_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100))
    manufacturer = db.Column(db.String(120))
    model = db.Column(db.String(120))
    serial_number = db.Column(db.String(120), unique=True)
    location = db.Column(db.String(150))
    purchase_date = db.Column(db.Date)
    warranty_expiry = db.Column(db.Date)
    maintenance_interval_days = db.Column(db.Integer, default=90)
    status = db.Column(db.String(30), default="AVAILABLE", nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    department = db.relationship("Department")
    maintenance_records = db.relationship("Maintenance", backref="equipment", lazy=True)
    service_requests = db.relationship("ServiceRequest", backref="equipment", lazy=True)

class Maintenance(db.Model):
    __tablename__ = "maintenance"
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)
    maintenance_type = db.Column(db.String(30), nullable=False, default="PREVENTIVE")
    scheduled_date = db.Column(db.Date, nullable=False, index=True)
    completed_date = db.Column(db.Date)
    status = db.Column(db.String(30), default="SCHEDULED", nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    work_description = db.Column(db.Text)
    downtime_hours = db.Column(db.Float, default=0)
    cost = db.Column(db.Numeric(12, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    technician = db.relationship("User")

class ServiceRequest(db.Model):
    __tablename__ = "service_requests"
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)
    reported_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    issue_description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default="MEDIUM", nullable=False)
    status = db.Column(db.String(30), default="OPEN", nullable=False)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    downtime_hours = db.Column(db.Float, default=0)
    repair_notes = db.Column(db.Text)
    reporter = db.relationship("User", foreign_keys=[reported_by_id])
    assignee = db.relationship("User", foreign_keys=[assigned_to_id])

class SparePart(db.Model):
    __tablename__ = "spare_parts"
    id = db.Column(db.Integer, primary_key=True)
    part_code = db.Column(db.String(50), unique=True, nullable=False)
    part_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    minimum_stock = db.Column(db.Integer, default=5, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), default=0)

class PartUsage(db.Model):
    __tablename__ = "parts_usage"
    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey("spare_parts.id"), nullable=False)
    maintenance_id = db.Column(db.Integer, db.ForeignKey("maintenance.id"))
    service_request_id = db.Column(db.Integer, db.ForeignKey("service_requests.id"))
    quantity_used = db.Column(db.Integer, nullable=False)
    used_at = db.Column(db.DateTime, default=datetime.utcnow)
    part = db.relationship("SparePart")

class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(120), nullable=False)
    entity_type = db.Column(db.String(80))
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User")
