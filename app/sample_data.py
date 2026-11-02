from datetime import date, timedelta

from .extensions import db
from .models import (
    AuditLog,
    Department,
    Equipment,
    Maintenance,
    PartUsage,
    ServiceRequest,
    SparePart,
    User,
)


def seed_sample_data():
    """Insert a small demo dataset if the application has no seeded records."""
    departments = [
        {"name": "ICU", "location": "Ground Floor"},
        {"name": "Radiology", "location": "East Wing"},
        {"name": "Biomedical Engineering", "location": "Maintenance Block"},
        {"name": "General Surgery", "location": "Second Floor"},
    ]

    department_map = {}
    for item in departments:
        department = Department.query.filter_by(name=item["name"]).first()
        if department is None:
            department = Department(name=item["name"], location=item["location"])
            db.session.add(department)
            db.session.flush()
        department_map[item["name"]] = department

    users = [
        {"full_name": "System Administrator", "email": "admin@memms.local", "role": "ADMIN", "password": "AdminPassword123!"},
        {"full_name": "Dr. Aisha Rahman", "email": "bioengineer@memms.local", "role": "BIOMEDICAL_ENGINEER", "password": "BioEngineer123!"},
        {"full_name": "Lucas James", "email": "technician@memms.local", "role": "TECHNICIAN", "password": "Technician123!"},
        {"full_name": "Miriam Patel", "email": "nurse@memms.local", "role": "DEPARTMENT_STAFF", "password": "NursePassword123!"},
        {"full_name": "Daniel Stone", "email": "manager@memms.local", "role": "MANAGEMENT", "password": "ManagerPassword123!"},
    ]

    user_map = {}
    for item in users:
        user = User.query.filter_by(email=item["email"]).first()
        if user is None:
            user = User(
                full_name=item["full_name"],
                email=item["email"],
                role=item["role"],
                department_id=department_map["ICU"].id if item["role"] == "DEPARTMENT_STAFF" else None,
            )
            user.set_password(item["password"])
            db.session.add(user)
            db.session.flush()
        user_map[item["email"]] = user

    equipment_rows = [
        {
            "asset_code": "ICU-1001",
            "name": "Patient Monitor",
            "category": "Monitoring",
            "manufacturer": "Philips",
            "model": "MX450",
            "serial_number": "PM-1001",
            "location": "ICU Room 1",
            "purchase_date": date.today() - timedelta(days=800),
            "warranty_expiry": date.today() + timedelta(days=400),
            "maintenance_interval_days": 90,
            "status": "AVAILABLE",
            "department_name": "ICU",
        },
        {
            "asset_code": "ICU-1002",
            "name": "Mechanical Ventilator",
            "category": "Respiratory",
            "manufacturer": "GE Healthcare",
            "model": "Carestation",
            "serial_number": "MV-1002",
            "location": "ICU Room 2",
            "purchase_date": date.today() - timedelta(days=1200),
            "warranty_expiry": date.today() - timedelta(days=30),
            "maintenance_interval_days": 60,
            "status": "IN_SERVICE",
            "department_name": "ICU",
        },
        {
            "asset_code": "RAD-2001",
            "name": "Portable X-Ray Unit",
            "category": "Imaging",
            "manufacturer": "Siemens",
            "model": "Mobilett XP",
            "serial_number": "XR-2001",
            "location": "Radiology Bay",
            "purchase_date": date.today() - timedelta(days=2000),
            "warranty_expiry": date.today() + timedelta(days=220),
            "maintenance_interval_days": 120,
            "status": "AVAILABLE",
            "department_name": "Radiology",
        },
        {
            "asset_code": "SUR-3001",
            "name": "Infusion Pump",
            "category": "Therapy",
            "manufacturer": "Baxter",
            "model": "Sigma Spectrum",
            "serial_number": "IP-3001",
            "location": "Surgery Ward",
            "purchase_date": date.today() - timedelta(days=500),
            "warranty_expiry": date.today() + timedelta(days=500),
            "maintenance_interval_days": 75,
            "status": "AVAILABLE",
            "department_name": "General Surgery",
        },
    ]

    equipment_map = {}
    for item in equipment_rows:
        equipment = Equipment.query.filter_by(asset_code=item["asset_code"]).first()
        if equipment is None:
            equipment = Equipment(
                asset_code=item["asset_code"],
                name=item["name"],
                category=item["category"],
                manufacturer=item["manufacturer"],
                model=item["model"],
                serial_number=item["serial_number"],
                location=item["location"],
                purchase_date=item["purchase_date"],
                warranty_expiry=item["warranty_expiry"],
                maintenance_interval_days=item["maintenance_interval_days"],
                status=item["status"],
                department_id=department_map[item["department_name"]].id,
            )
            db.session.add(equipment)
            db.session.flush()
        equipment_map[item["asset_code"]] = equipment

    maintenance_rows = [
        {
            "equipment_code": "ICU-1001",
            "maintenance_type": "PREVENTIVE",
            "scheduled_date": date.today() + timedelta(days=15),
            "completed_date": date.today() - timedelta(days=8),
            "status": "COMPLETED",
            "technician_email": "technician@memms.local",
            "work_description": "Calibrated monitor alarms and replaced worn leads.",
            "downtime_hours": 1.5,
            "cost": 210.00,
        },
        {
            "equipment_code": "ICU-1002",
            "maintenance_type": "CORRECTIVE",
            "scheduled_date": date.today() - timedelta(days=2),
            "completed_date": date.today() - timedelta(days=1),
            "status": "COMPLETED",
            "technician_email": "bioengineer@memms.local",
            "work_description": "Repaired pressure sensor drift and verified ventilation cycle stability.",
            "downtime_hours": 3.25,
            "cost": 640.00,
        },
        {
            "equipment_code": "RAD-2001",
            "maintenance_type": "PREVENTIVE",
            "scheduled_date": date.today() + timedelta(days=30),
            "completed_date": None,
            "status": "SCHEDULED",
            "technician_email": "bioengineer@memms.local",
            "work_description": "Routine X-ray inspection and image quality test.",
            "downtime_hours": 0.0,
            "cost": 0.0,
        },
    ]

    for item in maintenance_rows:
        equipment = equipment_map[item["equipment_code"]]
        record = Maintenance.query.filter_by(equipment_id=equipment.id, scheduled_date=item["scheduled_date"]).first()
        if record is None:
            db.session.add(
                Maintenance(
                    equipment_id=equipment.id,
                    maintenance_type=item["maintenance_type"],
                    scheduled_date=item["scheduled_date"],
                    completed_date=item["completed_date"],
                    status=item["status"],
                    technician_id=user_map[item["technician_email"]].id,
                    work_description=item["work_description"],
                    downtime_hours=item["downtime_hours"],
                    cost=item["cost"],
                )
            )

    service_requests = [
        {
            "equipment_code": "ICU-1002",
            "reported_by_email": "nurse@memms.local",
            "assigned_to_email": "bioengineer@memms.local",
            "issue_description": "Ventilator alarm is intermittent and oxygen flow appears unstable.",
            "priority": "HIGH",
            "status": "IN_PROGRESS",
            "reported_at": date.today() - timedelta(days=5),
            "started_at": date.today() - timedelta(days=3),
            "resolved_at": None,
            "downtime_hours": 2.5,
            "repair_notes": "Pressure sensor line inspected; awaiting replacement filter set.",
        },
        {
            "equipment_code": "SUR-3001",
            "reported_by_email": "nurse@memms.local",
            "assigned_to_email": "technician@memms.local",
            "issue_description": "Infusion pump dose accuracy check failed during post-use inspection.",
            "priority": "MEDIUM",
            "status": "OPEN",
            "reported_at": date.today() - timedelta(days=1),
            "started_at": None,
            "resolved_at": None,
            "downtime_hours": 0.0,
            "repair_notes": "Awaiting technician review and calibration logs.",
        },
    ]

    for item in service_requests:
        equipment = equipment_map[item["equipment_code"]]
        record = ServiceRequest.query.filter_by(
            equipment_id=equipment.id,
            issue_description=item["issue_description"],
            reported_by_id=user_map[item["reported_by_email"]].id,
        ).first()
        if record is None:
            db.session.add(
                ServiceRequest(
                    equipment_id=equipment.id,
                    reported_by_id=user_map[item["reported_by_email"]].id,
                    assigned_to_id=user_map[item["assigned_to_email"]].id,
                    issue_description=item["issue_description"],
                    priority=item["priority"],
                    status=item["status"],
                    reported_at=item["reported_at"],
                    started_at=item["started_at"],
                    resolved_at=item["resolved_at"],
                    downtime_hours=item["downtime_hours"],
                    repair_notes=item["repair_notes"],
                )
            )

    spare_parts = [
        {"part_code": "BAT-001", "part_name": "12V Monitoring Battery", "quantity": 18, "minimum_stock": 5, "unit_price": 120.00},
        {"part_code": "FIL-010", "part_name": "Ventilator Filter Set", "quantity": 9, "minimum_stock": 6, "unit_price": 42.50},
        {"part_code": "TUB-204", "part_name": "Infusion Tubing Kit", "quantity": 32, "minimum_stock": 10, "unit_price": 18.25},
        {"part_code": "LEAD-015", "part_name": "Patient Monitor Lead Set", "quantity": 14, "minimum_stock": 7, "unit_price": 35.00},
    ]

    part_map = {}
    for item in spare_parts:
        part = SparePart.query.filter_by(part_code=item["part_code"]).first()
        if part is None:
            part = SparePart(
                part_code=item["part_code"],
                part_name=item["part_name"],
                quantity=item["quantity"],
                minimum_stock=item["minimum_stock"],
                unit_price=item["unit_price"],
            )
            db.session.add(part)
            db.session.flush()
        part_map[item["part_code"]] = part

    part_usage_rows = [
        {"part_code": "LEAD-015", "maintenance_id": None, "service_request_id": None, "quantity_used": 2},
        {"part_code": "FIL-010", "maintenance_id": None, "service_request_id": None, "quantity_used": 1},
    ]

    if PartUsage.query.count() == 0:
        maintenance_ref = Maintenance.query.filter_by(equipment_id=equipment_map["ICU-1001"].id).first()
        service_ref = ServiceRequest.query.filter_by(equipment_id=equipment_map["ICU-1002"].id).first()
        for item in part_usage_rows:
            db.session.add(
                PartUsage(
                    part_id=part_map[item["part_code"]].id,
                    maintenance_id=maintenance_ref.id if item["part_code"] == "LEAD-015" else None,
                    service_request_id=service_ref.id if item["part_code"] == "FIL-010" else None,
                    quantity_used=item["quantity_used"],
                )
            )

    audit_logs = [
        {"user_email": "admin@memms.local", "action": "created_demo_dataset", "entity_type": "seed", "entity_id": 1, "details": "Inserted baseline maintenance sample data."},
        {"user_email": "bioengineer@memms.local", "action": "completed_maintenance", "entity_type": "maintenance", "entity_id": 1, "details": "Verified ICU monitor alarm calibration."},
        {"user_email": "nurse@memms.local", "action": "reported_fault", "entity_type": "service_request", "entity_id": 1, "details": "Reported ventilator alarm issue."},
    ]

    for item in audit_logs:
        user = user_map.get(item["user_email"])
        if user is None:
            continue
        existing = AuditLog.query.filter_by(user_id=user.id, action=item["action"], entity_type=item["entity_type"]).first()
        if existing is None:
            db.session.add(
                AuditLog(
                    user_id=user.id,
                    action=item["action"],
                    entity_type=item["entity_type"],
                    entity_id=item["entity_id"],
                    details=item["details"],
                )
            )

    db.session.commit()
    return {
        "departments": Department.query.count(),
        "users": User.query.count(),
        "equipment": Equipment.query.count(),
        "maintenance": Maintenance.query.count(),
        "service_requests": ServiceRequest.query.count(),
        "spare_parts": SparePart.query.count(),
    }
