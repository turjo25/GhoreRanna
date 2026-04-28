# GhorerRanna - Home Cook Food Ordering Platform

A Django-based web application that connects students, bachelor employees, and other customers with home cooks for convenient, affordable, and home-cooked meal delivery.

## Overview

GhorerRanna is an e-commerce platform designed to facilitate food ordering from verified home cooks. The system supports multiple user roles with different permissions, allowing for a complete order management workflow including menu browsing, cart management, checkout, payment processing, delivery tracking, and role-specific dashboards.

## Features

### User Roles & Capabilities
- **Students & Bachelor Employees (Customers)**: Browse menus, filter by category, add items to cart, apply discount coupons, secure checkout, track live order status, and cancel pending orders.
- **Home Cooks**: Create and manage their meal offerings, manage their availability, view incoming orders in their dashboard, update order statuses (Accepted, Preparing, Out for Delivery), and assign delivery staff.
- **Delivery Staff**: Dedicated delivery dashboard to manage assigned deliveries, track active and past deliveries, and update delivery statuses (Assigned, Picked Up, Handed Over).
- **Admin**: Master platform dashboard. Can manage users, create and manage Home Cook accounts, manage system-wide coupons, and view all orders, revenues, and platform statistics.

### Core Functionality
- **User Authentication & Profiles**: Role-based registration and secure login. Dedicated profile pages with statistics (e.g., total orders, total revenue, food sold) tailored to each user's role.
- **Menu Management**: CRUD operations for menu items with images, pricing, and availability toggles.
- **Shopping Cart**: Session-based cart with quantity adjustments and dynamic total calculations.
- **Checkout & Payment Workflow**: Secure checkout process supporting Cash, Card, and Online payment methods (demo processing). 
- **Coupon System**: Dynamic discount application via AJAX with expiration and status validation.
- **Order Management & Tracking**: Real-time tracking of order statuses (`Pending`, `Accepted`, `Preparing`, `Out for Delivery`, `Handed Over`, `Delivered`, `Cancelled`).
- **Delivery System**: Dedicated tracking and assignment workflow for delivery personnel.

## Technical Stack

- **Backend**: Django (Python 3.x)
- **Database**: SQLite (default, production-ready for PostgreSQL/MySQL via config)
- **Frontend**: HTML5, CSS3, JavaScript, Django Templates
- **Styling**: Vanilla CSS with modern aesthetics

## Project Structure

```text
GhorerRanna/
├── manage.py                 # Django management script
├── db.sqlite3                # SQLite database
├── Ghoreranna/               # Main project configuration
│   ├── settings.py           # Django settings
│   ├── urls.py               # Main URL routing
│   ├── asgi.py               
│   └── wsgi.py               
├── ghoreranna_app/           # Main application module
│   ├── models.py             # Database schemas (User, Menu, Order, etc.)
│   ├── views.py              # Application logic and view controllers
│   ├── forms.py              # Django forms for validation
│   ├── urls.py               # App-level URL definitions
│   ├── admin.py              # Django admin registrations
│   ├── context_processors.py # Global template variables
│   └── tests.py              # Application tests
└── templates/                # Frontend HTML templates
    ├── base.html             # Master layout
    ├── home.html             # Landing page
    ├── profile.html          # Role-based user dashboards
    ├── delivery_dashboard.html # Delivery staff portal
    ├── menu_list.html        # Menu catalog
    ├── cart.html             # Shopping cart interface
    ├── checkout.html         # Checkout and payment
    └── ...                   # Forms and other views
```

## Database Models

- **User**: Custom user model with role-based access control (Student, Bachelor Employee, Home Cook, Delivery Staff, Admin).
- **Menu**: Food items tied to a specific Home Cook, including pricing, images, and availability.
- **Order**: Customer orders containing total amounts, payment methods, delivery times, and current statuses.
- **OrderDetails**: Pivot table linking multiple Menu items to a single Order with quantities and subtotals.
- **Coupon**: Discount codes with percentage reductions, statuses, and expiration dates.
- **Payment**: Records of payment transactions linked to orders.
- **Delivery**: Delivery tracking records linking orders to assigned Delivery Staff.
- **Feedback**: Rating and review system for completed orders.
- **Subscription**: Management model for recurring meal plans (future capability).

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/turjo25/GhoreRanna.git
   cd GhorerRanna
   ```

2. **Set up a virtual environment (Recommended)**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   # or
   source venv/bin/activate      # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   - Copy `.env.example` to `.env` and configure your local settings.

5. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create an Admin account**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```
   Access the platform at `http://127.0.0.1:8000/`.

## Usage Guide

### For Customers (Students/Employees)
1. Register and log in.
2. Browse menus, filter by meal type, and add items to your cart.
3. Apply any valid coupons during checkout.
4. Track your order status in real-time from your Profile dashboard.
5. Acknowledge delivery once your food arrives.

### For Home Cooks
1. Log in to your Home Cook account (created by Admins).
2. Use the Profile dashboard to add and manage your Menu items.
3. Monitor the "Incoming Orders" tab.
4. Update statuses (e.g., Preparing, Out for Delivery) and assign Delivery Staff.

### For Delivery Staff
1. Log in to access the dedicated Delivery Dashboard.
2. View actively assigned orders and update statuses as you pick up and hand over meals.

### For Admins
1. Log in with an Admin account.
2. Use the Profile dashboard to view system-wide stats, manage all Home Cooks, and control platform coupons.

## License

This project is open-source. Please refer to the LICENSE file for details.
