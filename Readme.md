# DINEFLOW

### Restaurant Management System API

DINEFLOW is a backend REST API built with **Django** and **Django REST Framework** for managing restaurant operations.

It allows restaurants to manage users, menus, tables, reservations, orders, kitchen operations, and payments through a secure and organized API.

---

## Features

* User registration and JWT authentication
* Role-based access for Admin, Staff, and Customers
* Restaurant menu and category management
* Dining table management
* Table reservations
* Order management
* Kitchen order status tracking
* Payment management
* Search, filtering, ordering, and pagination
* API documentation with Swagger

---

## Main User Flow

```text
Register / Login
       ↓
Browse Menu
       ↓
Reserve a Table
       ↓
Place an Order
       ↓
Kitchen Prepares Order
       ↓
Order Served
       ↓
Make Payment
       ↓
Order Completed
```

---

## User Roles

| Role     | Description                                                      |
| -------- | ---------------------------------------------------------------- |
| Customer | Browse the menu, reserve tables, place orders, and make payments |
| Staff    | Manage menus, tables, reservations, and orders                   |
| Admin    | Manage users and restaurant operations                           |

---

## Technologies

* Python
* Django
* Django REST Framework
* Simple JWT
* PostgreSQL / SQLite
* django-filter
* drf-spectacular
* WhiteNoise

---

## Project Structure

```text
DINEFLOW/
│
├── accounts/
├── restaurant/
├── config/
├── manage.py
├── requirements.txt
├── .env
└── README.md
```

---

## Installation

Clone the project:

```bash
git clone https://github.com/Solvit-Django-Hub/DineFlow.git
cd DineFlow
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and configure your environment variables:

```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOW_ALL=True
```

Run migrations:

```bash
python manage.py migrate
```

Create an admin user:

```bash
python manage.py createsuperuser
```

Start the server:

```bash
python manage.py runserver
```

---

## API Documentation

After starting the server, open Swagger:

```text
http://127.0.0.1:8000/api/docs/
```

Swagger provides an interactive interface for viewing and testing the API endpoints.

---

## Testing

Run the tests with:

```bash
python manage.py test
```

---

## Deployment

DINEFLOW can be deployed using **Vercel**.

Install the Vercel CLI:

```bash
npm install -g vercel
```

Login:

```bash
vercel login
```

Deploy:

```bash
vercel
```

For production:

```bash
vercel --prod
```

---

## Purpose

DINEFLOW was created as a practical Django REST Framework project to demonstrate:

* Backend development with Django
* REST API development
* Authentication and permissions
* Database relationships
* Business logic and validation
* API documentation
* Testing and deployment
