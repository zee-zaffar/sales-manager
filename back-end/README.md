# sales-manager-api

A Flask REST API for managing shipments, shipment details, and payments.

## Features
- CRUD endpoints for Shipments, Shipment Details, and Payments
- PostgreSQL database support
- Example models and routes

## Setup (new machine)
Prerequisite: PostgreSQL 18 installed and running, and a Postgres login that can
create a database (or create an empty `sales_manager` database yourself first).

1. Create a virtual environment and activate it.
2. Install dependencies:
   pip install -r requirements.txt
3. Copy `.env.example` to `.env` and set `DATABASE_URL` (host, **port**, user, password, db name).
   Also copy your Etsy credentials / `tokens.json` from the old machine if you use Etsy import.
4. Create the database schema:
   python install_db.py            # creates the DB if missing and applies every migration in db/
   python install_db.py --seed     # optional: also load sample products/orders/shipments
   python install_db.py --status   # list applied / pending migrations
   The script is safe to re-run; applied migrations are tracked in `schema_migrations`.
5. Run the app:
   flask run

### Changing the schema
Add a new numbered file in `db/` (e.g. `12_my_change.sql`) and run `python install_db.py`.
Never edit a migration that has already been applied elsewhere. `03_drop_tables.sql` is
never run by the installer.

### Moving existing data to another machine
The schema is rebuilt by `install_db.py`; data is moved separately with a dump:
   pg_dump -Fc -h localhost -p <port> -U <user> -f sales_manager.dump sales_manager
   pg_restore -h localhost -p <port> -U <user> -d sales_manager --no-owner sales_manager.dump
(Run `install_db.py` first on the new machine only if you want a clean schema without data.)

## Endpoints
- `/shipments` - List and create shipments
- `/shipments/<id>` - Get, update, or delete a shipment
- `/shipments/<id>/details` - List and add details for a shipment
- `/payments` - List and create payments

See the code for more details.
