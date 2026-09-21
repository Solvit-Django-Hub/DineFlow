# DineFlow

### Restaurant Management System API

DineFlow is a RESTful backend API built with **Django** and **Django REST Framework** for managing restaurant operations.

It provides functionality for managing users, menus, dining tables, reservations, orders, kitchen operations, and payments through a secure and organized API.

---

##  Live API

**API:**
https://dineflow-api.vercel.app/

**Swagger Documentation:**
https://dineflow-api.vercel.app/api/docs/

---

##  Features

* User registration and JWT authentication
* Role-based access for Admin, Staff, and Customers
* Menu and category management
* Dining table management
* Table reservations
* Order management
* Kitchen order tracking
* Payment management
* Search, filtering, ordering, and pagination
* Swagger API documentation

---

##  Main User Flow

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

##  User Roles

| Role         | Description                                                   |
| ------------ | ------------------------------------------------------------- |
| **Customer** | Browse menus, reserve tables, place orders, and make payments |
| **Staff**    | Manage menus, tables, reservations, and orders                |
| **Admin**    | Manage users and restaurant operations                        |

---

##  Tech Stack

* **Python**
* **Django**
* **Django REST Framework**
* **Simple JWT**
* **PostgreSQL**
* **Neon PostgreSQL**
* **django-filter**
* **drf-spectacular**
* **WhiteNoise**
* **Vercel**

---

##  Database

DineFlow uses **PostgreSQL**, hosted on **Neon** for the production environment.

The database stores and manages:

* Users
* Menu categories and items
* Dining tables
* Reservations
* Orders and order items
* Payments

Database credentials are managed through environment variables and are not stored in the repository.

---

##  Project Structure

```text
DineFlow/
│
├── accounts/
├── restaurant/
├── config/
├── manage.py
├── requirements.txt
├── vercel.json
├── .env
├── .gitignore
└── README.md
```

---

##  Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Solvit-Django-Hub/DineFlow.git
cd DineFlow
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOW_ALL=True
DATABASE_URL=your-neon-database-url
```

> Never commit your `.env` file or database credentials to GitHub.

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create an Admin User

```bash
python manage.py createsuperuser
```

### 7. Start the Server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

---

##  API Documentation

DineFlow uses **Swagger / OpenAPI** for interactive API documentation.

### Local

```text
http://127.0.0.1:8000/api/docs/
```

### Live

https://dineflow-api.vercel.app/api/docs/

Swagger allows you to explore and test the available endpoints directly.

---

## Authentication

DineFlow uses **JWT authentication**.

After logging in, the API provides an access token and refresh token.

Protected endpoints require:

```http
Authorization: Bearer <access_token>
```

---

##  Testing

Run the test suite with:

```bash
python manage.py test
```

You can also check the project configuration:

```bash
python manage.py check
```

---

##  Deployment

DineFlow is deployed on **Vercel** with **Neon PostgreSQL** as the production database.

To deploy using Vercel:

```bash
npm install -g vercel
```

```bash
vercel login
```

```bash
vercel --prod
```

Production environment variables should be configured in Vercel and not committed to the repository.

---

##  Links

* **Repository:** https://github.com/Solvit-Django-Hub/DineFlow
* **Live API:** https://dineflow-api.vercel.app/
* **Swagger:** https://dineflow-api.vercel.app/api/docs/

---

##  Author

<a href="https://github.com/Aline-CROIRE">
  <img src="https://github.com/Aline-CROIRE.png" width="100px;" alt="Aline-CROIRE"/>
  <br />
  <sub><b>Aline-CROIRE</b></sub>
</a>

<br />

**DineFlow** — Restaurant Management System API

Built with **Django, Django REST Framework & PostgreSQL**.
