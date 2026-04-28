from django.contrib import admin
from django import forms
from django.contrib.auth.hashers import make_password
from .models import User, Coupon, Menu, Order, OrderDetails, Payment, Delivery, Feedback, Subscription


# ─── Custom form for User in admin ───────────────────────────────────────────
class UserAdminForm(forms.ModelForm):
    """
    Shows a plain-text password input in the admin.
    On save, it automatically hashes the value using Django's make_password()
    so the app's login view (which uses check_password) works correctly.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=True),
        help_text="Enter the password in plain text. It will be securely hashed on save.",
        required=False,
    )

    class Meta:
        model = User
        fields = '__all__'

    def save(self, commit=True):
        user = super().save(commit=False)
        raw_password = self.cleaned_data.get('password')
        if raw_password:
            # Only hash if the value isn't already a hashed string
            if not raw_password.startswith('pbkdf2_') and not raw_password.startswith('bcrypt'):
                user.password = make_password(raw_password)
            else:
                user.password = raw_password  # Already hashed, keep as-is
        if commit:
            user.save()
        return user


# ─── Custom ModelAdmin ────────────────────────────────────────────────────────
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm
    list_display = ('user_id', 'name', 'email', 'role', 'status')
    list_filter = ('role', 'status')
    search_fields = ('name', 'email')
    ordering = ('name',)


# ─── Register remaining models ────────────────────────────────────────────────
admin.site.register(Coupon)
admin.site.register(Menu)
admin.site.register(Order)
admin.site.register(OrderDetails)
admin.site.register(Payment)
admin.site.register(Delivery)
admin.site.register(Feedback)
admin.site.register(Subscription)
