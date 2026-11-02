from io import BytesIO
from flask import Blueprint, send_file, render_template
from flask_login import login_required
from ..models import Equipment, Maintenance, ServiceRequest, SparePart
from ..analytics import build_metrics

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

@reports_bp.get("/")
@login_required
def index():
    metrics = build_metrics()
    return render_template("reports/index.html", metrics=metrics)

@reports_bp.get("/excel")
@login_required
def excel():
    import pandas as pd
    from ..extensions import db
    equipment = Equipment.query.all()
    maintenance = Maintenance.query.all()
    tickets = ServiceRequest.query.all()
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame([{"asset_code": e.asset_code, "name": e.name, "category": e.category,
            "location": e.location, "status": e.status} for e in equipment]).to_excel(
                writer, sheet_name="Equipment", index=False)
        pd.DataFrame([{"equipment": m.equipment.asset_code, "type": m.maintenance_type,
            "scheduled": m.scheduled_date, "completed": m.completed_date, "status": m.status,
            "cost": float(m.cost or 0), "downtime_hours": m.downtime_hours} for m in maintenance]).to_excel(
                writer, sheet_name="Maintenance", index=False)
        pd.DataFrame([{"equipment": t.equipment.asset_code, "priority": t.priority,
            "status": t.status, "reported": t.reported_at, "downtime_hours": t.downtime_hours}
            for t in tickets]).to_excel(writer, sheet_name="Breakdowns", index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="memms_report.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@reports_bp.get("/pdf")
@login_required
def pdf():
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    metrics = build_metrics()
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph("Medical Equipment Maintenance Management System", styles["Title"]),
             Paragraph("Maintenance performance summary", styles["Heading2"]), Spacer(1, 8*mm)]
    data = [["Metric", "Value"],
        ["Total equipment", str(metrics["equipment_count"])],
        ["Available equipment", str(metrics["available_count"])],
        ["Open breakdowns", str(metrics["open_tickets"])],
        ["PM compliance", f'{metrics["pm_compliance"]:.1f}%'],
        ["Total maintenance cost", f'INR {metrics["total_cost"]:.2f}'],
        ["MTTR (hours)", f'{metrics["mttr"]:.2f}'],
        ["MTBF (hours)", f'{metrics["mtbf"]:.2f}']]
    table = Table(data, colWidths=[85*mm, 75*mm])
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#173b65")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("PADDING",(0,0),(-1,-1),7)]))
    story.append(table)
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("Metrics are based on records currently entered in the system. "
        "Incomplete records can affect MTTR, MTBF and compliance calculations.", styles["BodyText"]))
    doc.build(story)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="memms_summary.pdf",
                     mimetype="application/pdf")
