from django.contrib import admin
from core import models


# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "advertiser", "is_active")
    list_filter = ("advertiser", "email")
    search_fields = ("email", "advertiser")
    ordering = ("-created_at",)
    list_per_page = 25

    fieldsets = (
        (
            "Personal Info",
            {"fields": ("first_name", "last_name", "email", "advertiser")},
        ),
        ("Account Info", {"fields": ("is_active", "is_staff", "created_at")}),
    )


class AdvertiserAdmin(admin.ModelAdmin):
    list_display = [
        "advertiser_id",
        "name",
        "industry",
        "country",
        "is_active",
        "created_at",
    ]
    list_filter = ["industry", "country", "is_active"]
    search_fields = ["name", "industry"]


class AdAdmin(admin.ModelAdmin):
    list_display = [
        "ad_id",
        "advertiser",
        "ad_title",
        "ad_format",
        "is_active",
        "created_at",
    ]
    list_filter = ["ad_format", "is_active", "advertiser"]
    search_fields = ["ad_title"]


class TimeHierarchyAdmin(admin.ModelAdmin):
    list_display = ["time_key", "hour", "day", "week", "month", "weekday_name"]
    list_filter = ["month", "weekday_name"]


class ClickEventAdmin(admin.ModelAdmin):
    list_display = ["click_id", "advertiser", "ad", "click_time", "amount", "is_valid"]
    list_filter = ["is_valid", "click_time", "advertiser"]
    readonly_fields = ["click_id"]


class SpendSummaryAdmin(admin.ModelAdmin):
    list_display = [
        "advertiser",
        "window_start",
        "window_end",
        "gross_spend",
        "net_spend",
        "can_serve",
    ]
    list_filter = ["can_serve", "advertiser"]


class BudgetEventAdmin(admin.ModelAdmin):
    list_display = [
        "event_id",
        "advertiser",
        "new_budget_value",
        "event_time",
        "source",
    ]
    list_filter = ["source", "advertiser"]
    readonly_fields = ["event_id"]


# Register models
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Advertiser, AdvertiserAdmin)
admin.site.register(models.Ad, AdAdmin)
admin.site.register(models.TimeHierarchy, TimeHierarchyAdmin)
admin.site.register(models.ClickEvent, ClickEventAdmin)
admin.site.register(models.SpendSummary, SpendSummaryAdmin)
admin.site.register(models.BudgetEvent, BudgetEventAdmin)
