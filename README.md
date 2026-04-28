# GhorerRanna - Home Cook Food Ordering Platform

A Django-based web application that connects students, bachelor employees, and other customers with home cooks for convenient, affordable, and home-cooked meal delivery.

## Overview

GhorerRanna is an e-commerce platform designed to facilitate food ordering from verified home cooks. The system supports multiple user roles with different permissions, allowing for a complete order management workflow including menu browsing, cart management, checkout, payment processing, and delivery tracking.

## Features

### User Roles
- **Students & Bachelor Employees**: Browse menus, place orders, track deliveries
- **Home Cooks**: Create and manage meal offerings, view orders, update order status
- **Delivery Staff**: Manage order deliveries and delivery status
- **Admin**: Oversee the platform, manage users and system operations

### Core Functionality
- **User Management**: Registration, authentication, user profile management
- **Menu Management**: Home cooks can create, update, and manage their menu items
- **Shopping Cart**: Add items to cart and manage quantities
- **Checkout & Payment**: Secure checkout process with multiple payment methods:
  - Cash on Delivery
  - Card Payment
  - Online Payment
- **Order Management**: Track order status from pending to delivered
- **Coupon System**: Apply discount coupons at checkout
- **Order Tracking**: Real-time order status updates
- **Delivery Management**: Assign and track deliveries

## Technical Stack

- **Backend**: Django 6.0.3
- **Database**: SQLite (default, can be configured for production databases)
- **Frontend**: HTML, CSS, JavaScript
- **Python Version**: 3.x

## Project Structure

```
GhorerRanna/
├── manage.py                 # Django management script
├── db.sqlite3               # SQLite database
├── Ghoreranna/              # Main project settings
│   ├── __init__.py
│   ├── asgi.py              # ASGI configuration
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL configuration
│   └── wsgi.py              # WSGI configuration
├── ghoreranna_app/          # Main application
│   ├── models.py            # Database models
│   ├── views.py             # View controllers
│   ├── forms.py             # Django forms
│   ├── urls.py              # App-specific URL routing
│   ├── admin.py             # Django admin configuration
│   ├── context_processors.py # Template context processors
│   ├── tests.py             # Unit tests
│   ├── migrations/          # Database migrations
│   └── __init__.py
└── templates/               # HTML templates
    ├── base.html            # Base template
    ├── home.html            # Home page
    ├── login.html           # Login page
    ├── register.html        # Registration page
    ├── profile.html         # User profile
    ├── menu_list.html       # Browse menus
    ├── menu_detail.html     # Menu item details
    ├── menu_form.html       # Create/edit menu
    ├── cart.html            # Shopping cart
    ├── checkout.html        # Checkout page
    ├── order_confirmation.html # Order confirmation
    ├── cook_list.html       # List of home cooks
    ├── cook_form.html       # Cook profile form
    ├── cook_confirm_delete.html # Delete confirmation
    ├── coupon_form.html     # Coupon management
    └── coupon_confirm_delete.html # Delete confirmation
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone/Navigate to the project directory**
   ```bash
   cd GhorerRanna
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # or
   source venv/bin/activate      # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   If `requirements.txt` doesn't exist, install Django:
   ```bash
   pip install django pillow
   ```

4. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (admin account)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```
   
   The application will be available at `http://127.0.0.1:8000/`

## Database Models

### Core Models

- **User**: Manages user accounts with role-based access control
  - Roles: Student, Bachelor Employee, Home Cook, Delivery Staff, Admin

- **Menu**: Represents food items offered by home cooks
  - Links to User (Home Cook)
  - Includes item name, description, price, availability

- **Order**: Tracks customer orders
  - Links to User (Customer) and Coupon (optional)
  - Includes order date, delivery time, total amount, payment method, status

- **OrderDetails**: Individual items in an order
  - Links to Order and Menu
  - Tracks quantity and subtotal

- **Coupon**: Discount codes for orders
  - Includes discount percentage and expiry date

- **Payment**: Payment transaction records

- **Delivery**: Delivery information for orders

## Usage

### For Customers
1. Register or log in to your account
2. Browse available menu items from home cooks
3. Add items to your cart
4. Proceed to checkout
5. Select payment method and apply coupons (if available)
6. Confirm order and track its status

### For Home Cooks
1. Register with "Home Cook" role
2. Create and manage your menu items
3. View incoming orders in your dashboard
4. Update order status as you prepare and deliver meals
5. Manage your availability

### For Admins
1. Access Django admin panel at `/admin/`
2. Manage users, menus, orders, and coupons
3. Monitor platform activity and user roles

## Admin Panel

Access the Django admin interface at `http://127.0.0.1:8000/admin/` with superuser credentials to:
- Manage users and assign roles
- View and manage orders
- Monitor menu items
- Manage coupons and discounts

## Security Considerations

- Passwords are hashed before storage
- CSRF protection is enabled
- User sessions are managed securely
- Admin registration is restricted and cannot be done through normal registration

## Future Enhancements

- Email notifications for order updates
- SMS alerts for delivery
- Rating and review system
- Advanced analytics dashboard
- Payment gateway integration (Stripe, PayPal)
- Mobile application
- Real-time order tracking with GPS
- Chef ratings and filtering

## Contributing

Contributions are welcome! Please ensure:
- Code follows Django best practices
- All features are tested
- Database migrations are included
- Documentation is updated

## License

[Add your license information here]

## Support

For issues or questions, please contact the development team or file an issue in the project repository.

## Deployment Notes

Before deploying to production:
- Set `DEBUG = False` in settings.py
- Configure allowed hosts properly
- Use a production-grade database (PostgreSQL, MySQL)
- Set up environment variables for sensitive data
- Use HTTPS
- Configure proper logging
- Run security checks: `python manage.py check --deploy`
