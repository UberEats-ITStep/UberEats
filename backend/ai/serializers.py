from rest_framework import serializers


class AIRecommendationRequestSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=500, required=True, min_length=3)


# This validates Groq Response that is sent as jSON.
# We do not want to trust qroq, imagine he sends max_price: "hello", delete_db: true :)
class ExtractedIntentSerializer(serializers.Serializer):
    max_price = serializers.IntegerField(allow_null=True, required=False)
    is_vegetarian = serializers.BooleanField(allow_null=True, required=False)
    is_vegan = serializers.BooleanField(allow_null=True, required=False)
    keywords = serializers.ListField(
        child=serializers.CharField(max_length=50), required=False, default=list
    )
    categories = serializers.ListField(
        child=serializers.CharField(max_length=100), required=False, default=list
    )
    cuisines = serializers.ListField(
        child=serializers.CharField(max_length=100), required=False, default=list
    )


class LLMRecommendedItemSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField(required=True)
    reason = serializers.CharField(max_length=500, required=True)


class LLMRecommendationResponseSerializer(serializers.Serializer):
    recommendations = LLMRecommendedItemSerializer(many=True, required=True)
    summary = serializers.CharField(max_length=500, required=True)
