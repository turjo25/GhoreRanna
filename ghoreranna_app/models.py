from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Bachelor Employee', 'Bachelor Employee'),
        ('Home Cook', 'Home Cook'),
        ('Delivery Staff', 'Delivery Staff'),
        ('Admin', 'Admin'),
    ]
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    address = models.TextField()
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.role})"


class Coupon(models.Model):
    coupon_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    expiry_date = models.DateTimeField()
    status = models.BooleanField(default=True)

    class Meta:
        ordering = ['-expiry_date']

    def __str__(self):
        return self.code


class Menu(models.Model):
    menu_id = models.AutoField(primary_key=True)
    homecook = models.ForeignKey(User, on_delete=models.CASCADE, related_name='menus', limit_choices_to={'role': 'Home Cook'})
    meal_type = models.CharField(max_length=100)
    item_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/', null=True, blank=True)
    availability_status = models.BooleanField(default=True)

    class Meta:
        ordering = ['item_name']

    def __str__(self):
        return f"{self.item_name} - {self.homecook.name}"


class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Online', 'Online'),
    ]
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Preparing', 'Preparing'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Handed Over', 'Handed Over'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_time = models.DateTimeField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, default='Pending')
    cancellation_status = models.BooleanField(default=False)

    class Meta:
        ordering = ['-order_date']

    def __str__(self):
        return f"Order #{self.order_id} by {self.user.name}"


class OrderDetails(models.Model):
    order_details_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_details')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='order_details')
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.menu.item_name} (Order #{self.order.order_id})"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    payment_id = models.AutoField(primary_key=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    transaction_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment for Order #{self.order.order_id} - {self.payment_status}"


class Delivery(models.Model):
    DELIVERY_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Assigned', 'Assigned'),
        ('Picked Up', 'Picked Up'),
        ('Handed Over', 'Handed Over'),
        ('Delivered', 'Delivered'),
    ]

    delivery_id = models.AutoField(primary_key=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries', limit_choices_to={'role': 'Delivery Staff'})
    delivery_status = models.CharField(max_length=50, choices=DELIVERY_STATUS_CHOICES, default='Pending')
    delivery_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-delivery_date']

    def __str__(self):
        delivery_staff_name = self.delivery_staff.name if self.delivery_staff else 'Unassigned'
        return f"Delivery for Order #{self.order.order_id} via {delivery_staff_name}"


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(null=True, blank=True)
    feedback_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-feedback_date']

    def __str__(self):
        return f"Feedback by {self.user.name} for Order #{self.order.order_id} - {self.rating}/5"


class Subscription(models.Model):
    SUBSCRIPTION_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Expired', 'Expired'),
        ('Cancelled', 'Cancelled'),
    ]

    subscription_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan_type = models.CharField(max_length=100)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    subscription_status = models.CharField(max_length=50, choices=SUBSCRIPTION_STATUS_CHOICES, default='Active')

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.plan_type} - {self.user.name} ({self.subscription_status})"