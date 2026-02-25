# Setup

## Environment variables
- `SECRET_KEY`: Flask secret.
- `DATABASE_URL`: SQLAlchemy DB URL (default `sqlite:///shornbee.db`).
- `MAIL_FROM`: sender email label.
- `APPROVAL_BASE_URL`: base URL used in approval links (e.g. `https://app.example.com`).

## Steps
1. Install dependencies: `pip install -r requirements.txt`
2. Apply migrations: `python scripts/apply_migrations.py`
3. Seed/import wines: `python scripts/import_wines.py scripts/sample_wines.csv`
4. Run app: `python run.py`
5. Open `http://localhost:5000`

## Roles and naming
- Administrator role label in UI/content: **Cellar Master**
- Enquiries mailbox (server-side destination): `cellarbouncer@mdgloballogistics.com`
- “MD” means Millennial Drinkers.
