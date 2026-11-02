from datetime import date
import numpy as np
from .models import Equipment, Maintenance, ServiceRequest

def build_metrics():
    equipment = Equipment.query.all()
    maintenance = Maintenance.query.all()
    tickets = ServiceRequest.query.all()
    completed = [m for m in maintenance if m.status == "COMPLETED"]
    scheduled_due = [m for m in maintenance if m.scheduled_date <= date.today()]
    completed_due = [m for m in scheduled_due if m.status == "COMPLETED"]
    costs = np.array([float(m.cost or 0) for m in maintenance], dtype=float)
    repairs = np.array([float(t.downtime_hours or 0) for t in tickets
                        if t.status == "RESOLVED"], dtype=float)
    intervals = []
    by_equipment = {}
    for t in sorted(tickets, key=lambda x: x.reported_at):
        by_equipment.setdefault(t.equipment_id, []).append(t.reported_at)
    for events in by_equipment.values():
        if len(events) > 1:
            intervals.extend([(events[i] - events[i-1]).total_seconds()/3600
                              for i in range(1, len(events))])
    return {
        "equipment_count": len(equipment),
        "available_count": sum(e.status == "AVAILABLE" for e in equipment),
        "open_tickets": sum(t.status in ("OPEN", "ASSIGNED", "IN_PROGRESS") for t in tickets),
        "pm_compliance": (100 * len(completed_due) / len(scheduled_due)) if scheduled_due else 0.0,
        "total_cost": float(costs.sum()) if costs.size else 0.0,
        "mttr": float(np.mean(repairs)) if repairs.size else 0.0,
        "mtbf": float(np.mean(intervals)) if intervals else 0.0,
        "total_downtime": float(sum(m.downtime_hours or 0 for m in maintenance) +
                                sum(t.downtime_hours or 0 for t in tickets))
    }
