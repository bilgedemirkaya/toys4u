# 🧸 Toys4U – Toy Store Management System

Toys4U is a Django-based web application for managing a toy manufacturing and sales business. It supports user registration with roles (customer, staff, administrator), toy browsing, ordering, custom toy creation, production reporting, and administrative staff management.

---

## Features

- User registration with address and profile picture
- Role-based access control: Customer, Staff, Administrator
- Browse standard toys and create custom toys
- Add to cart and place orders
- Leave reviews for completed orders
- Staff dashboard with production reports and validation
- Admin dashboard for managing staff roles
- Order management and order history tracking
- Users can review toys and see average ratings
- System will hide bad rating toys
- Managers can see daily, monthly and yearly reports of sales

---

## Tech Stack

- **Backend:** Django 5.1
- **Database:** SQLite (for local development)
- **Frontend:** HTML5, CSS (within Django templates)

---

## Setup Instructions

```bash

# Clone the repo
git clone https://github.com/your-username/toys4u.git
cd toys4u

## Create virtual environment to run the app (Optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt

## Run mugrations for database
python manage.py makemigrations
python manage.py migrate

## Create a superuser (for admin access)
python manage.py createsuperuser

## Run the server
python manage.py runserver

