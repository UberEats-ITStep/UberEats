from django.contrib import admin

from .models import RecommendationEvent


@admin.register(RecommendationEvent)
class RecommendationEventAdmin(admin.ModelAdmin):
	list_display = ("event_type", "request_id", "user", "menu_item", "position", "created_at")
	list_filter = ("event_type", "created_at")
	search_fields = ("request_id", "query", "user__email", "menu_item__name")
	readonly_fields = ("created_at",)
