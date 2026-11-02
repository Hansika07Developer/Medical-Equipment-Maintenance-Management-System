from app.extensions import db
from app.models import User, Equipment

def login(client, app, role="ADMIN"):
    with app.app_context():
        user = User(full_name="Test User", email=f"{role.lower()}@test.local", role=role)
        user.set_password("LongTestPassword!123")
        db.session.add(user)
        db.session.commit()
    return client.post("/auth/login", data={
        "email": f"{role.lower()}@test.local",
        "password": "LongTestPassword!123"
    }, follow_redirects=True)

def test_login_and_dashboard(client, app):
    login(client, app)
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Maintenance dashboard" in response.data

def test_equipment_page_requires_login(client):
    response = client.get("/equipment/")
    assert response.status_code in (302, 401)

def test_equipment_create_and_qr(client, app):
    login(client, app)
    response = client.post("/equipment/new", data={
        "asset_code": "ICU-001", "name": "Patient Monitor",
        "category": "Monitoring", "status": "AVAILABLE"
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        item = Equipment.query.filter_by(asset_code="ICU-001").first()
        assert item is not None
        item_id = item.id
    qr = client.get(f"/equipment/{item_id}/qr.png")
    assert qr.status_code == 200
    assert qr.mimetype == "image/png"
