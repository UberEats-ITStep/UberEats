from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from decimal import Decimal

from orders.models import Order
from restaurants.models import Cuisine, Restaurant
from .models import Review

User = get_user_model()


class ReviewModelTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(username='client', email='client@test.com', password='pwd')
        self.cuisine = Cuisine.objects.create(name='Italian')
        self.restaurant = Restaurant.objects.create(name='Pizza Place', cuisine=self.cuisine)
        self.order = Order.objects.create(client=self.client_user, restaurant=self.restaurant, status=Order.STATUS_COMPLETED, total_price=10)

    def test_review_updates_restaurant_rating(self):
        # Initial
        self.assertIsNone(self.restaurant.rating)

        # Create 1st review
        review1 = Review.objects.create(client=self.client_user, restaurant=self.restaurant, order=self.order, rating=4)
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.rating, 4.0)

        # Create 2nd review (need another order)
        other_user = User.objects.create_user(username='other', email='other@test.com', password='pwd')
        other_order = Order.objects.create(client=other_user, restaurant=self.restaurant, status=Order.STATUS_COMPLETED, total_price=20)
        review2 = Review.objects.create(client=other_user, restaurant=self.restaurant, order=other_order, rating=2)
        
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.rating, 3.0)  # (4+2)/2 = 3

        # Update review
        review1.rating = 5
        review1.save()
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.rating, 3.5)  # (5+2)/2 = 3.5

        # Delete review
        review2.delete()
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.rating, 5.0)


class ReviewApiTests(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(username='client', email='client@test.com', password='pwd')
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='pwd')
        
        self.cuisine = Cuisine.objects.create(name='Sushi')
        self.restaurant = Restaurant.objects.create(name='Sushi Bar', cuisine=self.cuisine)
        self.other_restaurant = Restaurant.objects.create(name='Burger Joint', cuisine=self.cuisine)
        
        self.order = Order.objects.create(client=self.client_user, restaurant=self.restaurant, status=Order.STATUS_COMPLETED, total_price=50)
        
        self.url = reverse('review-list')

    def test_create_review(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.post(self.url, {
            'restaurant': self.restaurant.id,
            'order': self.order.id,
            'rating': 5,
            'comment': 'Great food!'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(response.data['rating'], 5)

    def test_cannot_review_uncompleted_order(self):
        self.order.status = Order.STATUS_PENDING
        self.order.save()
        self.client.force_authenticate(user=self.client_user)

        response = self.client.post(self.url, {
            'restaurant': self.restaurant.id,
            'order': self.order.id,
            'rating': 5
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('completed orders', response.data['order'][0])

    def test_cannot_review_someone_elses_order(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(self.url, {
            'restaurant': self.restaurant.id,
            'order': self.order.id,
            'rating': 5
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('own orders', response.data['order'][0])

    def test_restaurant_must_match_order(self):
        self.client.force_authenticate(user=self.client_user)

        response = self.client.post(self.url, {
            'restaurant': self.other_restaurant.id,
            'order': self.order.id,
            'rating': 5
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('must match', response.data['restaurant'][0])

    def test_cannot_review_twice(self):
        Review.objects.create(client=self.client_user, restaurant=self.restaurant, order=self.order, rating=4)
        self.client.force_authenticate(user=self.client_user)

        response = self.client.post(self.url, {
            'restaurant': self.restaurant.id,
            'order': self.order.id,
            'rating': 5
        }, format='json')

        # ModelOneToOne will also throw error, but validation catches it first
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('exists', response.data['order'][0])

    def test_update_own_review(self):
        review = Review.objects.create(client=self.client_user, restaurant=self.restaurant, order=self.order, rating=4)
        self.client.force_authenticate(user=self.client_user)
        
        detail_url = reverse('review-detail', args=[review.id])
        response = self.client.patch(detail_url, {'rating': 2}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.rating, 2)

    def test_cannot_update_others_review(self):
        review = Review.objects.create(client=self.client_user, restaurant=self.restaurant, order=self.order, rating=4)
        self.client.force_authenticate(user=self.other_user)
        
        detail_url = reverse('review-detail', args=[review.id])
        response = self.client.patch(detail_url, {'rating': 2}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_review(self):
        review = Review.objects.create(client=self.client_user, restaurant=self.restaurant, order=self.order, rating=4)
        self.client.force_authenticate(user=self.client_user)
        
        detail_url = reverse('review-detail', args=[review.id])
        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)

    def test_list_restaurant_reviews(self):
        Review.objects.create(client=self.client_user, restaurant=self.restaurant, order=self.order, rating=4)
        
        response = self.client.get(self.url, {'restaurant': self.restaurant.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_invalid_rating_bounds(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.post(self.url, {
            'restaurant': self.restaurant.id,
            'order': self.order.id,
            'rating': 6
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', response.data)

    def test_delete_last_review_clears_rating(self):
        review = Review.objects.create(client=self.client_user, restaurant=self.restaurant, order=self.order, rating=4)
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.rating, 4.0)

        self.client.force_authenticate(user=self.client_user)
        detail_url = reverse('review-detail', args=[review.id])
        response = self.client.delete(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.restaurant.refresh_from_db()
        self.assertIsNone(self.restaurant.rating)

    def test_anonymous_access_can_read(self):
        Review.objects.create(client=self.client_user, restaurant=self.restaurant, order=self.order, rating=4)
        
        # Test GET is allowed without auth
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test POST is blocked
        response = self.client.post(self.url, {
            'restaurant': self.restaurant.id,
            'order': self.order.id,
            'rating': 5
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ordering_by_created_at_desc(self):
        review1 = Review.objects.create(client=self.client_user, restaurant=self.restaurant, order=self.order, rating=4)
        
        other_user = User.objects.create_user(username='ordering', email='order@test.com', password='pwd')
        other_order = Order.objects.create(client=other_user, restaurant=self.restaurant, status=Order.STATUS_COMPLETED, total_price=50)
        review2 = Review.objects.create(client=other_user, restaurant=self.restaurant, order=other_order, rating=5)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Assuming Meta.ordering = ["-created_at"], the newest review (review2) should be first
        self.assertEqual(response.data[0]['id'], review2.id)
        self.assertEqual(response.data[1]['id'], review1.id)

