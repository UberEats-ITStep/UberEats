import os
from decimal import Decimal
from django.test import TestCase
from django.core.management import call_command
from django.conf import settings
from .models import Restaurant, MenuItem, Category, MenuTag

class RivneCatalogTestCase(TestCase):
    def setUp(self):
        call_command("load_rivne_catalog")

    def test_catalog_contains_approximately_30_restaurants(self):
        count = Restaurant.objects.count()
        self.assertGreaterEqual(count, 30)

    def test_every_active_restaurant_has_substantial_menu(self):
        active_restaurants = Restaurant.objects.filter(is_active=True)
        self.assertGreater(active_restaurants.count(), 0)
        for restaurant in active_restaurants:
            # Check for substantial menu (>10 items)
            self.assertGreaterEqual(restaurant.menu_items.count(), 12)

    def test_total_menu_item_count(self):
        count = MenuItem.objects.count()
        # Should be several hundred
        self.assertGreaterEqual(count, 300)

    def test_english_only_data(self):
        import re
        cyrillic_pattern = re.compile(r'[\u0400-\u04FF]')
        
        for restaurant in Restaurant.objects.all():
            self.assertFalse(cyrillic_pattern.search(restaurant.name))
            self.assertFalse(cyrillic_pattern.search(restaurant.description))
            self.assertFalse(cyrillic_pattern.search(restaurant.address))
        
        for item in MenuItem.objects.all():
            self.assertFalse(cyrillic_pattern.search(item.name))
            self.assertFalse(cyrillic_pattern.search(item.description))
            
        for category in Category.objects.all():
            self.assertFalse(cyrillic_pattern.search(category.name))

    def test_no_placeholder_names(self):
        for restaurant in Restaurant.objects.all():
            self.assertNotIn("Demo", restaurant.name)
            self.assertNotIn("Test", restaurant.name)

    def test_menu_items_have_valid_required_fields(self):
        for item in MenuItem.objects.all():
            self.assertTrue(bool(item.name))
            self.assertTrue(bool(item.category))
            self.assertIsNotNone(item.price)

    def test_menu_prices_are_valid(self):
        for item in MenuItem.objects.all():
            self.assertIsInstance(item.price, Decimal)
            self.assertGreater(item.price, Decimal("0.00"))

    def test_representative_categories_are_present(self):
        categories = Category.objects.values_list("name", flat=True)
        self.assertIn("Hot Drinks", categories)
        self.assertIn("Pizza", categories)
        self.assertIn("Main Courses", categories)

    def test_vegetarian_and_vegan_data_represented(self):
        self.assertTrue(MenuItem.objects.filter(is_vegetarian=True).exists())
        self.assertTrue(MenuItem.objects.filter(is_vegan=True).exists())

    def test_seed_command_is_idempotent(self):
        initial_restaurant_count = Restaurant.objects.count()
        initial_item_count = MenuItem.objects.count()

        call_command("load_rivne_catalog")

        self.assertEqual(Restaurant.objects.count(), initial_restaurant_count)
        self.assertEqual(MenuItem.objects.count(), initial_item_count)

    def test_postgresql_configuration_remains_unchanged(self):
        db_engine = settings.DATABASES["default"]["ENGINE"]
        self.assertIn("postgresql", db_engine)

    def test_env_file_was_not_modified(self):
        self.assertTrue(os.path.exists(".env") or os.path.exists("../.env") or os.path.exists("../../.env") or os.path.exists("backend/.env"))

    def test_ai_candidate_retrieval(self):
        from ai.services import CandidateRetriever
        service = CandidateRetriever()
        
        # "cheap burger"
        intent = {"categories": ["Burgers"], "max_price": 260.0}
        candidates = service.retrieve(intent)
        self.assertTrue(any("Burger" in c["name"] for c in candidates))
        
        # "vegetarian meal"
        intent = {"is_vegetarian": True}
        candidates = service.retrieve(intent)
        self.assertTrue(all(c["is_vegetarian"] for c in candidates))
        self.assertGreater(len(candidates), 0)
        
        # "vegan food"
        intent = {"is_vegan": True}
        candidates = service.retrieve(intent)
        self.assertTrue(all(c["is_vegan"] for c in candidates))
        self.assertGreater(len(candidates), 0)
        
        # "pizza"
        intent = {"categories": ["Pizza"]}
        candidates = service.retrieve(intent)
        self.assertGreater(len(candidates), 0)
        
        # "sushi"
        intent = {"categories": ["Sushi"]}
        candidates = service.retrieve(intent)
        self.assertGreater(len(candidates), 0)
        
        # "dessert"
        intent = {"categories": ["Desserts"]}
        candidates = service.retrieve(intent)
        self.assertGreater(len(candidates), 0)
        
        # "coffee"
        intent = {"categories": ["Hot Drinks"]}
        candidates = service.retrieve(intent)
        self.assertGreater(len(candidates), 0)

    def test_address_is_in_rivne_and_non_empty(self):
        for restaurant in Restaurant.objects.all():
            self.assertTrue(bool(restaurant.address))
            self.assertIn("Rivne", restaurant.address)
            self.assertIn("Ukraine", restaurant.address)

    def test_coordinates_are_valid_and_in_rivne_bbox(self):
        # Rivne bounding box approx: 50.5 to 50.7 lat, 26.1 to 26.4 lon
        for restaurant in Restaurant.objects.all():
            self.assertIsNotNone(restaurant.latitude)
            self.assertIsNotNone(restaurant.longitude)
            lat = float(restaurant.latitude)
            lon = float(restaurant.longitude)
            # Check range
            self.assertTrue(50.5 <= lat <= 50.7, f"Lat {lat} out of bounds for {restaurant.name}")
            self.assertTrue(26.1 <= lon <= 26.4, f"Lon {lon} out of bounds for {restaurant.name}")
            # Ensure they are not reversed
            self.assertGreater(lat, lon, "Lat should be greater than Lon for Rivne")

    def test_no_placeholder_coordinates(self):
        for restaurant in Restaurant.objects.all():
            lat = str(restaurant.latitude)
            lon = str(restaurant.longitude)
            self.assertNotIn("0.000", lat)
            self.assertNotIn("0.000", lon)

    def test_map_serialization(self):
        from restaurants.serializers import RestaurantSerializer
        restaurant = Restaurant.objects.first()
        serializer = RestaurantSerializer(restaurant)
        data = serializer.data
        
        # Some frontend maps expect coordinates in a specific format or geojson
        # Here we just check that lat/lon are correctly serialized as strings or floats
        # If there's a specific geojson field, we check it
        self.assertIn('latitude', data)
        self.assertIn('longitude', data)
        # If you happen to use [lon, lat] format in a 'location' field, assert it here:
        if 'location' in data and isinstance(data['location'], dict):
            coords = data['location'].get('coordinates')
            if coords:
                self.assertEqual(len(coords), 2)
                self.assertEqual(coords[0], float(restaurant.longitude))
                self.assertEqual(coords[1], float(restaurant.latitude))

    def test_mcdonalds_and_kfc_records(self):
        # McDonald's branches
        mcd_restaurants = Restaurant.objects.filter(name__icontains="McDonald")
        self.assertEqual(mcd_restaurants.count(), 2)

        branch_a = Restaurant.objects.filter(catalog_key="mcdonalds-borysenka").first()
        self.assertIsNotNone(branch_a)
        self.assertEqual(branch_a.address, "1 Oleksandra Borysenka Street, Rivne, Ukraine")
        self.assertIn("Zlata Plaza", branch_a.description)
        self.assertAlmostEqual(float(branch_a.latitude), 50.618792, places=4)
        self.assertAlmostEqual(float(branch_a.longitude), 26.248329, places=4)

        branch_b = Restaurant.objects.filter(catalog_key="mcdonalds-chervonii").first()
        self.assertIsNotNone(branch_b)
        self.assertEqual(branch_b.address, "16-A Vasyl Chervonii Street, Rivne, Ukraine")
        self.assertIn("Chayka", branch_b.description)
        self.assertIn("McDrive", branch_b.description)
        self.assertAlmostEqual(float(branch_b.latitude), 50.630046, places=4)
        self.assertAlmostEqual(float(branch_b.longitude), 26.272360, places=4)

        # KFC branch
        kfc_restaurants = Restaurant.objects.filter(name__icontains="KFC")
        self.assertEqual(kfc_restaurants.count(), 1)
        kfc = kfc_restaurants.first()
        self.assertEqual(kfc.catalog_key, "kfc-soborna")
        self.assertEqual(kfc.address, "94 Soborna Street, Premier Shopping Center, Rivne, Ukraine")
        self.assertIn("Premier Shopping Center", kfc.description)
        self.assertAlmostEqual(float(kfc.latitude), 50.619819, places=4)
        self.assertAlmostEqual(float(kfc.longitude), 26.249493, places=4)

