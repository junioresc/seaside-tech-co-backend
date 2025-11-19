from __future__ import annotations

from apps.customers.models import Customer


def auto_link_customer_for_user(user, create_if_missing: bool = True) -> Customer | None:
    """
    Link a Customer to the given auth user based on email match.
    If no Customer exists and create_if_missing, create a minimal one.
    """
    email = (user.email or "").strip().lower()
    if not email:
        return None
    existing = Customer.objects.filter(email__iexact=email).first()
    if existing:
        if existing.user_id is None:
            existing.user = user
            # backfill names if empty
            if not existing.first_name:
                existing.first_name = getattr(user, "first_name", "") or existing.first_name
            if not existing.last_name:
                existing.last_name = getattr(user, "last_name", "") or existing.last_name
            existing.save(update_fields=["user", "first_name", "last_name"])
        return existing
    if create_if_missing:
        return Customer.objects.create(
            user=user,
            email=email,
            first_name=getattr(user, "first_name", "") or "",
            last_name=getattr(user, "last_name", "") or "",
        )
    return None


