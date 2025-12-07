# Generated migration for initial Seaside Tech Co data

from django.db import migrations


def populate_orgs_stores(apps, schema_editor):
    """Create initial Organization and Stores for Seaside Tech Co"""
    Organization = apps.get_model('orgs', 'Organization')
    Store = apps.get_model('orgs', 'Store')
    
    # Idempotency check
    if Organization.objects.filter(name="Seaside Tech Co").exists():
        print("Organization 'Seaside Tech Co' already exists, skipping...")
        return
    
    # Create Organization
    org = Organization.objects.create(
        name="Seaside Tech Co",
        contact_email="contact@seasidetech.co",
        contact_phone="+1 (831) 555-0100",
        description="Multi-location computer repair shop chain"
    )
    print(f"✅ Created Organization: {org.name}")
    
    # Create Stores
    stores_data = [
        {
            "name": "Seaside Tech Co - Main Street",
            "address": {
                "street": "123 Main St",
                "city": "Seaside",
                "state": "CA",
                "zip": "93955"
            },
            "phone": "+1 (831) 555-0101",
            "business_hours": "Mon-Fri 9AM-6PM, Sat 10AM-4PM, Sun Closed",
            "timezone": "America/Los_Angeles",
            "is_active": True,
        },
        {
            "name": "Seaside Tech Co - Downtown",
            "address": {
                "street": "456 Downtown Ave",
                "city": "Seaside",
                "state": "CA",
                "zip": "93955"
            },
            "phone": "+1 (831) 555-0102",
            "business_hours": "Mon-Fri 9AM-7PM, Sat 10AM-5PM, Sun Closed",
            "timezone": "America/Los_Angeles",
            "is_active": True,
        },
        {
            "name": "Seaside Tech Co - West Side",
            "address": {
                "street": "789 West Blvd",
                "city": "Seaside",
                "state": "CA",
                "zip": "93955"
            },
            "phone": "+1 (831) 555-0103",
            "business_hours": "Mon-Sat 9AM-6PM, Sun Closed",
            "timezone": "America/Los_Angeles",
            "is_active": True,
        },
    ]
    
    created_stores = []
    for store_data in stores_data:
        store = Store.objects.create(organization=org, **store_data)
        created_stores.append(store.name)
    
    print(f"✅ Created {len(created_stores)} Stores")
    print(f"   - Main Street, Downtown, West Side")


def reverse_orgs_stores(apps, schema_editor):
    """Reverse migration - delete Seaside Tech Co organization and stores"""
    Organization = apps.get_model('orgs', 'Organization')
    
    try:
        org = Organization.objects.get(name="Seaside Tech Co")
        org.delete()  # Cascades to stores
        print("✅ Deleted Seaside Tech Co organization and stores")
    except Organization.DoesNotExist:
        print("Organization 'Seaside Tech Co' not found, nothing to delete")


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_orgs_stores, reverse_orgs_stores),
    ]
