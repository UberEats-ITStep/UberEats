from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class Cuisine(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    image_url = models.CharField(max_length=500, blank=True, default="")
    address = models.TextField(blank=True, default="")
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    cuisine = models.ForeignKey(
        Cuisine,
        on_delete=models.PROTECT,
        related_name="restaurants",
    )
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    review_count = models.PositiveIntegerField(default=0)
    delivery_time = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValidationError(
                "Latitude and longitude must both be set, or both be empty."
            )

    @property
    def is_open_now(self) -> bool:
        time = timezone.localtime()
        is_weekend = time.weekday() >= 5  # 5=субота, 6=неділя
        day_type = "weekend" if is_weekend else "weekday"
        hours = next((h for h in self.opening_hours.all() if h.day_type == day_type), None)
        if hours is None:
            return False
        return hours.opens_at <= time.time() <= hours.closes_at

    def update_rating(self):
        from django.db.models import Avg, Count
        aggregation = self.reviews.aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        self.rating = aggregation['avg_rating']
        self.review_count = aggregation['total_reviews']
        self.save(update_fields=['rating', 'review_count'])

    def __str__(self) -> str:
        return self.name


class OpeningHours(models.Model):
    DAY_TYPE_CHOICE = [
        ("weekday", "Робочий день"),
        ("weekend", "Вихідний"),
    ]

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="opening_hours",
    )
    day_type = models.CharField(
        max_length=10,
        choices=DAY_TYPE_CHOICE,
        default="weekday",
    )
    opens_at = models.TimeField(default="09:00")
    closes_at = models.TimeField(default="22:00")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["restaurant", "day_type"],
                name="unique_restaurant_day_type",
            )
        ]

    def __str__(self) -> str:
        return f"{self.get_day_type_display()}: {self.opens_at}-{self.closes_at}"


class MenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="menu_items",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="menu_items",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, blank=True)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    image = models.ImageField(upload_to="menu_items/%Y/%m/", null=True, blank=True)

    is_available = models.BooleanField(default=True)
    unavailable_reason = models.CharField(max_length=255, blank=True, default="")

    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    calories = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["restaurant", "slug"],
                name="unique_menu_item_slug_per_restaurant",
            )
        ]

    def clean(self):
        if self.price is not None and self.price <= 0:
            raise ValidationError({"price": "Price must be greater than zero."})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name