from rest_framework import serializers


class GetAvailableTagsSerializer(serializers.Serializer):
    in_use_only = serializers.BooleanField(required=False, default=True)


class GetAvailableCuisinesSerializer(serializers.Serializer):
    in_use_only = serializers.BooleanField(required=False, default=True)


class GetAvailableCategoriesSerializer(serializers.Serializer):
    in_use_only = serializers.BooleanField(required=False, default=True)


class SearchMenuSerializer(serializers.Serializer):
    query = serializers.CharField(required=False, allow_blank=True, default="")
    max_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True, default=None
    )
    is_vegetarian = serializers.BooleanField(required=False, allow_null=True, default=None)
    is_vegan = serializers.BooleanField(required=False, allow_null=True, default=None)
    cuisine = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, default=None
    )
    category = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, default=None
    )
    limit = serializers.IntegerField(required=False, min_value=1, max_value=50, default=20)


class SearchRestaurantsSerializer(serializers.Serializer):
    query = serializers.CharField(required=False, allow_blank=True, default="")
    cuisine = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, default=None
    )
    min_rating = serializers.FloatField(required=False, allow_null=True, default=None)
    is_open_now = serializers.BooleanField(required=False, allow_null=True, default=None)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=50, default=20)


class GetMenuItemSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField()


class GetRestaurantSerializer(serializers.Serializer):
    restaurant_id = serializers.IntegerField()


class GetUserOrderHistorySerializer(serializers.Serializer):
    """
    Intentionally has NO user id field. The user is always taken from
    the authenticated ToolContext (see domain_tools.GetUserOrderHistoryTool),
    so there is no argument through which the model could request
    another user's order history.
    """

    limit = serializers.IntegerField(required=False, min_value=1, max_value=50, default=10)