from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.shortcuts import redirect
from datetime import datetime
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
User = get_user_model()

CATEGORY_CHOICES = (
    ('FR', 'Fruits'), ('VG', 'Vegetables'), ('JU', 'Juices'), ('DR', 'Dried')
)
LABEL_CHOICES = (
    ('P', 'primary'), ('S', 'secondary'), ('D', 'danger')
)

SIZE_CHOICES = (
    ('S', 'small'), ('M', 'medium'), ('L', 'large'), ('E', 'extra_large'), 
)

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    item_image = models.ImageField(upload_to='media/images/', blank=True, null=True)
    percentage_discount = models.FloatField(null=True, blank=True)
    price_before_discount = models.FloatField(null=True, blank=True)  # Changed to FloatField
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2, default='VG')
    label = models.CharField(choices=LABEL_CHOICES, max_length=1, default='P')
    slug = models.SlugField(default='test-products', unique=True)
    rating = models.FloatField(default=4.6, blank=True, null=True)
    description = models.TextField(blank=True, null=True, default='This is test description for items')
    size = models.CharField(choices=SIZE_CHOICES, max_length=2, default='M')

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('shop:product-single', kwargs={'slug': self.slug})
    
    def get_add_to_cart_url(self):
        return reverse("shop:add-to-cart", kwargs={'slug': self.slug}) 

    def get_remove_from_cart_url(self):
        return reverse("shop:remove-from-cart", kwargs={'slug': self.slug}) 

    def get_remove_item_from_cart_url(self):
        return reverse("shop:remove-item-from-cart", kwargs={'slug': self.slug}) 

    def calculate_percentage_discount(self):
        """Calculate and save the percentage discount if there's a previous price"""
        if self.price_before_discount is not None and self.price_before_discount > 0:
            discount_amount = self.price_before_discount - self.price
            self.percentage_discount = (discount_amount / self.price_before_discount) * 100
            self.save()
        return self.percentage_discount
    
    def get_display_price(self):
        """Returns the formatted price with currency symbol (adjust as needed)"""
        return f"${self.price:.2f}"
    
    def get_display_original_price(self):
        """Returns the formatted original price if it exists"""
        if self.price_before_discount:
            return f"${self.price_before_discount:.2f}"
        return None
    
    def save(self, *args, **kwargs):
        """Override save to automatically calculate discount percentage"""
        if self.price_before_discount and self.price_before_discount > self.price:
            self.calculate_percentage_discount()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ordered_date = models.DateTimeField(null=True, blank=True)
    ordered = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.quantity} of {self.item.title}"
    
    def get_total_item_price(self):
        """Calculate total price for this order item"""
        return self.quantity * self.item.price
    
    def get_total_discount_amount(self):
        """Calculate total discount amount if there's a previous price"""
        if self.item.price_before_discount is not None:
            return (self.item.price_before_discount - self.item.price) * self.quantity
        return 0
    
    def get_total_before_discount(self):
        """Calculate total price before discount if available"""
        if self.item.price_before_discount is not None:
            return self.quantity * self.item.price_before_discount
        return self.get_total_item_price()
    
    def get_percentage_saved(self):
        """Calculate percentage saved for this order item"""
        if self.item.price_before_discount is not None and self.item.price_before_discount > 0:
            return ((self.item.price_before_discount - self.item.price) / self.item.price_before_discount) * 100
        return 0


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username
    
    def get_total(self):
        """Calculate total for all items in the order"""
        return sum(order_item.get_total_item_price() for order_item in self.items.all())
    
    def get_total_discount(self):
        """Calculate total discount for all items in the order"""
        return sum(order_item.get_total_discount_amount() for order_item in self.items.all())
    
    def get_total_before_discount(self):
        """Calculate total before discount for all items in the order"""
        return sum(order_item.get_total_before_discount() for order_item in self.items.all())
    

class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, )
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='billing_address', null=True, blank=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    street_address = models.CharField(max_length=30, null=True, blank=True)    
    apartment_suite = models.CharField(max_length=30, null=True, blank=True)    
    town_city = models.CharField(max_length=30, null=True, blank=True)    
    state_country = CountryField(multiple=False)
    email = models.EmailField()
    phone = PhoneNumberField(region='KE', null=True, blank=True)
    postcode = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username

class Customer(models.Model):
    pass