from app import create_app
from app.sample_data import seed_sample_data

app = create_app()
with app.app_context():
    counts = seed_sample_data()
    print("Sample data ready:")
    for key, value in counts.items():
        print(f"- {key}: {value}")
