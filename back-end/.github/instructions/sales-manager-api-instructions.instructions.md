---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.
# Sales Manager API Instructions
This project is a Sales Manager API built using Flask and SQLAlchemy. It provides endpoints to manage orders and shipment headers. The database used is SQLite.
## Project Structure
- `app.py`: The main application file that initializes the Flask app and sets up routes.    
- `models.py`: Contains the SQLAlchemy models for the database tables.
- `orders.py`: Contains the routes and logic for managing orders.
- `shipment_header.py`: Contains the routes and logic for managing shipment headers.
- `config.py`: Configuration settings for the Flask app and database.   
- `requirements.txt`: Lists the Python dependencies for the project.
## Coding Guidelines
- Follow PEP 8 style guidelines for Python code.
- Use descriptive variable and function names.
- Include docstrings for all functions and classes. 
- Ensure proper error handling and return appropriate HTTP status codes.
- Write modular and reusable code.
- Use SQLAlchemy ORM features effectively for database interactions.
- Ensure that all API endpoints return JSON responses.
- Validate input data for API endpoints to ensure data integrity.
- Write unit tests for critical functions and endpoints.
- Use version control effectively, with clear and concise commit messages.

- Ensure that sensitive information (like database URIs) is not hardcoded and is managed through configuration files or environment variables.
- Maintain consistency in naming conventions, especially when mapping database fields to API response fields.
- When modifying existing code, ensure backward compatibility unless a major version change is intended.
## Database Schema
### Orders Table
- `order_no` (String, Primary Key): Unique identifier for each order.
- `order_date` (Date): The date when the order was placed.
- `qty` (Integer): Quantity of items in the order.  
- `color` (String): Color of the items in the order.
- `source` (String): Source of the order.   

- `platform` (String): Platform through which the order was placed.
- `order_amount` (Numeric): Total amount for the order.
- `sales_tax` (Numeric): Sales tax applicable to the order.
- `comments` (Text): Additional comments about the order.
### ShipmentHeader Table
- `shipment_id` (Integer, Primary Key): Unique identifier for each shipment.
- `shipment_date` (Date): The date when the shipment was made.
- `carrier` (String): Carrier used for the shipment.
- `tracking_number` (String): Tracking number for the shipment.
- `status` (String): Current status of the shipment.
- `comments` (Text): Additional comments about the shipment.
## API Endpoints
### Orders
- `GET /orders`: Retrieve a list of all orders. 

- `POST /orders`: Insert a new order into the database. Expects a JSON payload with order details.
### Shipment Header 
- `GET /shipment-headers`: Retrieve a list of all shipment headers.
- `POST /shipment-headers`: Insert a new shipment header into the database. Expects a JSON payload with shipment details.   
## Setup Instructions
1. Clone the repository.
2. Create a virtual environment and activate it.
3. Install the dependencies using `pip install -r requirements.txt`.
4. Set up the database by running the application once to create the SQLite database file.
5. Run the Flask application using `python app.py`.
6. Access the API endpoints using a tool like Postman or curl.
## Additional Notes
- Ensure that the SQLite database file is included in the `.gitignore` file to prevent it from being committed to version control.
- Regularly update the `requirements.txt` file when adding new dependencies.
- Consider adding logging to the application for better monitoring and debugging.







