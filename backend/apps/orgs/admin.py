from django.contrib import admin

from .models import Membership, Organization, Store


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "legal_name", "billing_email")


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "timezone")
    list_filter = ("organization",)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "store", "role", "is_default")
    list_filter = ("role", "store")
