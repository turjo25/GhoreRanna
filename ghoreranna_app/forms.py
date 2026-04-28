from django import forms
from .models import User, Menu, Coupon

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'}))
    
    # Exclude 'Admin' from role choices on registration; Delivery Staff can self-register
    ROLE_CHOICES_REGISTER = [
        ('Student', 'Student'),
        ('Bachelor Employee', 'Bachelor Employee'),
        ('Home Cook', 'Home Cook'),
        ('Delivery Staff', 'Delivery Staff'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES_REGISTER, widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'}))

    class Meta:
        model = User
        fields = ['name', 'phone', 'email', 'address', 'role']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'}),
            'address': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
            
class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'}))

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['meal_type', 'item_name', 'description', 'price', 'image', 'availability_status']
        widgets = {
            'meal_type': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'}),
            'item_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'}),
            'availability_status': forms.CheckboxInput(attrs={'class': 'h-5 w-5 text-primary focus:ring-primary border-gray-300 rounded'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'}),
            'address': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary', 'rows': 3}),
        }

class CookManagementForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary', 'placeholder': 'Leave blank to keep current password'}))
    
    class Meta:
        model = User
        fields = ['name', 'phone', 'email', 'address', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'}),
            'address': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'}),
        }

class CheckoutForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash on Delivery'),
        ('Card', 'Credit / Debit Card'),
        ('Online', 'Mobile Banking (bKash / Nagad)'),
    ]

    delivery_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary resize-none',
            'rows': 3,
            'placeholder': 'Enter your full delivery address…',
        })
    )
    coupon_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary uppercase tracking-widest',
            'placeholder': 'PROMO CODE (optional)',
        })
    )
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'payment-radio'}),
        initial='Cash',
    )
    # Card fields (shown/hidden by JS)
    card_number = forms.CharField(
        required=False,
        max_length=19,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary font-mono tracking-widest',
            'placeholder': '1234  5678  9012  3456',
            'maxlength': '19',
            'id': 'id_card_number',
        })
    )
    card_expiry = forms.CharField(
        required=False,
        max_length=5,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary font-mono tracking-widest',
            'placeholder': 'MM/YY',
            'maxlength': '5',
            'id': 'id_card_expiry',
        })
    )
    card_cvv = forms.CharField(
        required=False,
        max_length=4,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary font-mono tracking-widest',
            'placeholder': 'CVV',
            'maxlength': '4',
            'id': 'id_card_cvv',
        })
    )
    card_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary',
            'placeholder': 'Name on Card',
            'id': 'id_card_name',
        })
    )
    # Mobile banking field
    mobile_number = forms.CharField(
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary font-mono',
            'placeholder': '01XXXXXXXXX',
            'id': 'id_mobile_number',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('payment_method')
        if method == 'Card':
            if not cleaned_data.get('card_number'):
                self.add_error('card_number', 'Card number is required.')
            if not cleaned_data.get('card_expiry'):
                self.add_error('card_expiry', 'Expiry date is required.')
            if not cleaned_data.get('card_cvv'):
                self.add_error('card_cvv', 'CVV is required.')
            if not cleaned_data.get('card_name'):
                self.add_error('card_name', 'Cardholder name is required.')
        elif method == 'Online':
            if not cleaned_data.get('mobile_number'):
                self.add_error('mobile_number', 'Mobile banking number is required.')
        return cleaned_data

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_percentage', 'expiry_date', 'status']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary', 'placeholder': 'e.g., SAVE20'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary', 'step': '0.01'}),
            'expiry_date': forms.DateTimeInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary', 'type': 'datetime-local'}),
            'status': forms.CheckboxInput(attrs={'class': 'h-5 w-5 text-primary focus:ring-primary border-gray-300 rounded'}),
        }