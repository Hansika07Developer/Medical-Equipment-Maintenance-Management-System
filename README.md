# MEMMS – Medical Equipment Maintenance Management System

Advanced final-year project starter built with Flask, MySQL, Bootstrap, Pandas, NumPy and OpenCV.

## Features
- Role-based sign-in (ADMIN, BIOMEDICAL_ENGINEER, TECHNICIAN, DEPARTMENT_STAFF, MANAGEMENT)
- Equipment register, search, edit and QR label generation
- Preventive maintenance scheduling and completion
- Breakdown reporting, assignment, work progress and resolution
- Spare-parts inventory with stock adjustments and low-stock indicators
- Dashboard and operational analytics (PM compliance, MTTR, MTBF, downtime, cost)
- Excel export (multiple worksheets) and PDF summary report
- Live browser camera QR scanning and image-upload QR decoding with OpenCV; QR payloads are `MEMMS-EQUIPMENT:<asset_code>`
- CSRF protection, password hashing, audit-log model and basic tests

## Requirements
Python 3.10+, MySQL 8+ (SQLite is used automatically for a quick local development run if DATABASE_URL is absent).

## Install (Windows PowerShell)
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```
Edit `.env` and set a strong `SECRET_KEY` and MySQL `DATABASE_URL`.

## MySQL setup
Run `schema.sql` in MySQL Workbench or the MySQL CLI. For a restricted application account:
```sql
CREATE USER 'memms_user'@'localhost' IDENTIFIED BY 'use-a-long-unique-password';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX
ON memms_db.* TO 'memms_user'@'localhost';
FLUSH PRIVILEGES;
```
Set:
`DATABASE_URL=mysql+pymysql://memms_user:password@localhost:3306/memms_db?charset=utf8mb4`

For Linux/macOS activate with `source .venv/bin/activate`.

## Create tables and first administrator
```bash
flask --app run.py init-db
python scripts/create_admin.py
```
The admin creation script prompts for an email, name and password; it does not ship a hard-coded default credential.

## Seed demo data
```bash
flask --app run.py init-db
flask --app run.py seed-sample-data
```
This inserts departments, team members, equipment, maintenance work, spare-parts records and service tickets for a demo environment.

## Run
```bash
python run.py
```
Open http://127.0.0.1:5000 and sign in using the administrator account you created.

## Test
```bash
pytest -q
```

## QR scanning
- Open an equipment row and click Download in the QR column.
- Visit `/vision/scan` to use the live camera scanner or upload a QR image for server-side OpenCV decoding.
- Print the label and attach it to the asset according to hospital policy.
- The QR payload format is `MEMMS-EQUIPMENT:<asset_code>`.
- The authenticated endpoint `POST /vision/lookup` accepts form field `payload` and returns equipment details as JSON.
- The scanner uses html5-qrcode in the browser and posts decoded text to `/vision/lookup`. Image uploads are decoded server-side with OpenCV. Camera access generally requires HTTPS except on localhost.

## Database / schema
`schema.sql` documents the MySQL tables. Flask-SQLAlchemy models in `app/models.py` are the application model definitions. Use Flask-Migrate for future schema changes:
```bash
flask --app run.py db init
flask --app run.py db migrate -m "describe change"
flask --app run.py db upgrade
```
Do not run `db init` repeatedly after the migration repository exists.

## Role policy
- ADMIN: full administration and user provisioning (user provisioning is intentionally CLI/manual in this starter).
- BIOMEDICAL_ENGINEER: equipment, maintenance, assignments and inventory.
- TECHNICIAN: view service operations and update eligible work.
- DEPARTMENT_STAFF: report breakdowns and view operational pages.
- MANAGEMENT: view dashboards, reports and inventory read-only.

## Important production hardening
This is a substantial academic starter, not a certified clinical or production deployment. Before hospital use:
1. Add formal user administration, password reset, MFA and account lockout.
2. Add server-side authorization tests for every object/action and scope technicians to assigned jobs.
3. Add full audit coverage, retention policy, backups, monitoring and incident response.
4. Add validation for date ranges, numeric values, status transitions and equipment references.
5. Use database migrations, HTTPS, secure secrets, least-privilege DB credentials and production WSGI server.
6. Add concurrency-safe stock transactions and approval controls.
7. Add real camera scanning UI, image upload validation and malware scanning.
8. Define MTBF precisely for your institution; the included approximation uses time between recorded breakdown reports per asset and should not be treated as an engineering reliability certification.
9. Clinical safety, calibration acceptance, equipment release and maintenance intervals must be governed by qualified biomedical engineering staff and hospital policy. The software does not certify equipment as safe for patient use.
