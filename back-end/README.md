# sales-manager-api

A Flask REST API for managing shipments, shipment details, and payments.

## Features
- CRUD endpoints for Shipments, Shipment Details, and Payments
- PostgreSQL database support
- Example models and routes

## Setup
1. Create a virtual environment and activate it.
2. Install dependencies:
   pip install -r requirements.txt
3. Set up your PostgreSQL database and update the config in `config.py`.
4. Run the app:
   flask run

## Endpoints
- `/shipments` - List and create shipments
- `/shipments/<id>` - Get, update, or delete a shipment
- `/shipments/<id>/details` - List and add details for a shipment
- `/payments` - List and create payments

See the code for more details.
