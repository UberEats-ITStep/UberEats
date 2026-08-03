from datetime import timedelta
from decimal import Decimal

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
        super().clean()
        if (self.latitude is None) != (self.longitude is None):
            missing_field = "longitude" if self.longitude is None else "latitude"
            raise ValidationError({
                missing_field: "Latitude and longitude must both be set, or both be empty."
            })

    @property
    def is_open_now(self) -> bool:
        current = timezone.localtime(timezone.now())
        schedules = {hours.day_type: hours for hours in self.opening_hours.all()}
        current_type = "weekend" if current.weekday() >= 5 else "weekday"
        previous_day = current.date() - timedelta(days=1)
        previous_type = "weekend" if previous_day.weekday() >= 5 else "weekday"
        current_time = current.time().replace(tzinfo=None)

        hours = schedules.get(current_type)
        if hours and hours.opens_at < hours.closes_at:
            if hours.opens_at <= current_time < hours.closes_at:
                return True
        elif hours and current_time >= hours.opens_at:
            return True

        previous_hours = schedules.get(previous_type)
        return bool(
            previous_hours
            and previous_hours.opens_at > previous_hours.closes_at
            and current_time < previous_hours.closes_at
        )

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

    def clean(self):
        super().clean()
        if self.opens_at == self.closes_at:
            raise ValidationError({
                "closes_at": "Closing time must differ from opening time."
            })

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
        validators=[MinValueValidator(Decimal("0.01"))],
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
        super().clean()
        if self.price is not None and self.price <= 0:
            raise ValidationError({"price": "Price must be greater than zero."})
        if self.is_available and self.unavailable_reason:
            raise ValidationError({
                "unavailable_reason": "Available items cannot have an unavailable reason."
            })
        if not self.is_available and not self.unavailable_reason.strip():
            raise ValidationError({
                "unavailable_reason": "Unavailable items must include a reason."
            })

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "menu-item"
            slug = base_slug
            suffix = 2
            existing = type(self).objects.filter(restaurant=self.restaurant)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            while existing.filter(slug=slug).exists():
                slug = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
