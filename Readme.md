# DineFlow

> A restaurant management system for managing menus, tables, customers, reservations, orders, staff, and payments.

## Overview

DineFlow brings restaurant operations into one system. It allows customers to make reservations and place orders while staff and administrators manage restaurant activities from a central platform.

## Main Features

* User registration and login
* JWT authentication
* User profiles
* Menu and menu item management
* Table management
* Customer management
* Staff and waiter management
* Reservations
* Orders and order items
* Payments
* Role-based permissions
* Search, filtering, and ordering
* Pagination
* REST API
* API documentation
* Automated testing

## User Flow

```text
Customer
   │
   ▼
Register / Login
   │
   ▼
View Menu
   │
   ▼
Make Reservation
   │
   ▼
Place Order
   │
   ▼
Review Order
   │
   ▼
Payment
   │
   ▼
Confirmation
```

```text
Staff / Admin
      │
      ▼
    Login
      │
      ▼
   Dashboard
      │
      ├── Manage Menu
      ├── Manage Tables
      ├── Manage Customers
      ├── Manage Reservations
      ├── Manage Orders
      └── Manage Payments
```

## System Structure

```text
DineFlow
│
├── Accounts
├── Restaurant
│   ├── Menus
│   ├── Menu Items
│   ├── Tables
│   └── Staff
│
├── Customers
├── Reservations
├── Orders
│   └── Order Items
├── Payments
├── API
└── Tests
```

## Technology

* Python
* Django
* Django REST Framework
* SQLite / PostgreSQL
* JWT Authentication
* Swagger / OpenAPI

## Installation

Clone the repository:

```bash
git clone https://github.com/Solvit-Django-Hub/DineFlow.git
cd DineFlow
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run database migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## API

The REST API provides access to the main DineFlow resources, including users, menus, tables, reservations, orders, and payments.

API documentation is available through Swagger/OpenAPI.

## License

This project is developed for learning and portfolio purposes.
