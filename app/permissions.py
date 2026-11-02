from functools import wraps
from flask import abort
from flask_login import current_user, login_required

def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator

def log_action(db, AuditLog, action, entity_type=None, entity_id=None, details=None):
    from flask_login import current_user
    user_id = current_user.id if current_user.is_authenticated else None
    db.session.add(AuditLog(user_id=user_id, action=action,
                            entity_type=entity_type, entity_id=entity_id,
                            details=details))
