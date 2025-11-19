from django.contrib import admin

from .models import Customer


class LinkedFilter(admin.SimpleListFilter):
    title = "linked"
    parameter_name = "linked"

    def lookups(self, request, model_admin):
        return (("yes", "Linked"), ("no", "Unlinked"))

    def queryset(self, request, queryset):
        val = self.value()
        if val == "yes":
            return queryset.filter(user__isnull=False)
        if val == "no":
            return queryset.filter(user__isnull=True)
        return queryset


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "user_linked")
    list_filter = (LinkedFilter,)
    search_fields = ("first_name", "last_name", "email")

    def user_linked(self, obj: Customer) -> bool:
        return bool(obj.user_id)
    user_linked.boolean = True


