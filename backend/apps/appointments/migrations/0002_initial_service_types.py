# Generated migration for initial Service Types data

from decimal import Decimal

from django.db import migrations


def populate_service_types(apps, schema_editor):
    """Create initial Service Types"""
    ServiceType = apps.get_model('appointments', 'ServiceType')
    
    # Idempotency check
    if ServiceType.objects.exists():
        print("Service Types already exist, skipping...")
        return
    
    service_types = [
        {
            "code": "virus-removal",
            "name": "Virus Removal",
            "estimated_price": Decimal("99.99"),
            "default_duration_minutes": 120,
            "description": "Malware and virus removal, system cleanup"
        },
        {
            "code": "data-recovery",
            "name": "Data Recovery",
            "estimated_price": Decimal("149.99"),
            "default_duration_minutes": 180,
            "description": "Recover lost or deleted data from damaged drives"
        },
        {
            "code": "hardware-repair",
            "name": "Hardware Repair",
            "estimated_price": Decimal("129.99"),
            "default_duration_minutes": 120,
            "description": "Repair or replace damaged hardware components"
        },
        {
            "code": "memory-upgrade",
            "name": "Memory Upgrade",
            "estimated_price": Decimal("199.99"),
            "default_duration_minutes": 180,
            "description": "Add more RAM or storage to improve performance"
        },
        {
            "code": "screen-replacement",
            "name": "Screen Replacement",
            "estimated_price": Decimal("529.99"),
            "default_duration_minutes": 60,
            "description": "Replace cracked or damaged display screen"
        },
        {
            "code": "keyboard-replacement",
            "name": "Keyboard Replacement",
            "estimated_price": Decimal("149.99"),
            "default_duration_minutes": 60,
            "description": "Replace worn or damaged keyboard"
        },
        {
            "code": "trackpad-replacement",
            "name": "Trackpad Replacement",
            "estimated_price": Decimal("139.99"),
            "default_duration_minutes": 60,
            "description": "Replace worn or damaged trackpad"
        },
        {
            "code": "touchscreen-replacement",
            "name": "Touchscreen Replacement",
            "estimated_price": Decimal("159.99"),
            "default_duration_minutes": 60,
            "description": "Replace worn or damaged touchscreen"
        },
        {
            "code": "battery-replacement",
            "name": "Battery Replacement",
            "estimated_price": Decimal("89.99"),
            "default_duration_minutes": 60,
            "description": "Replace worn or damaged battery"
        },
        {
            "code": "camera-repair",
            "name": "Camera Repair",
            "estimated_price": Decimal("129.99"),
            "default_duration_minutes": 60,
            "description": "Repair or replace damaged camera lens or sensor"
        },
        {
            "code": "audio-repair",
            "name": "Audio Repair",
            "estimated_price": Decimal("79.99"),
            "default_duration_minutes": 60,
            "description": "Repair or replace damaged audio components"
        },
        {
            "code": "software-installation",
            "name": "Software Installation",
            "estimated_price": Decimal("69.99"),
            "default_duration_minutes": 60,
            "description": "Install operating system or software applications"
        },
        {
            "code": "diagnostic",
            "name": "Diagnostic",
            "estimated_price": Decimal("59.99"),
            "default_duration_minutes": 30,
            "description": "Diagnose hardware or software issues"
        },
        {
            "code": "network-setup",
            "name": "Network Setup",
            "estimated_price": Decimal("229.99"),
            "default_duration_minutes": 120,
            "description": "Set up network connections and configurations"
        },
        {
            "code": "security-scan",
            "name": "Security Scan",
            "estimated_price": Decimal("99.99"),
            "default_duration_minutes": 120,
            "description": "Scan for malware and security vulnerabilities"
        },
        {
            "code": "data-backup",
            "name": "Data Backup",
            "estimated_price": Decimal("129.99"),
            "default_duration_minutes": 120,
            "description": "Backup important data to external storage"
        },
        {
            "code": "performance-optimization",
            "name": "Performance Optimization",
            "estimated_price": Decimal("129.99"),
            "default_duration_minutes": 120,
            "description": "Optimize system performance and speed"
        },
        {
            "code": "os-upgrade",
            "name": "Operating System Upgrade",
            "estimated_price": Decimal("109.99"),
            "default_duration_minutes": 60,
            "description": "Upgrade to a newer operating system version"
        },
        {
            "code": "software-update",
            "name": "Software Update",
            "estimated_price": Decimal("99.99"),
            "default_duration_minutes": 60,
            "description": "Update software applications to the latest version"
        },
        {
            "code": "software-removal",
            "name": "Software Removal",
            "estimated_price": Decimal("119.99"),
            "default_duration_minutes": 120,
            "description": "Remove unwanted software applications"
        },
    ]
    
    for service_type_data in service_types:
        ServiceType.objects.create(**service_type_data)
    
    print(f"✅ Created {len(service_types)} Service Types")
    print()
    
    # Print complete summary after all migrations
    Organization = apps.get_model('orgs', 'Organization')
    Store = apps.get_model('orgs', 'Store')
    DeviceType = apps.get_model('repairs', 'DeviceType')
    
    org_count = Organization.objects.filter(name="Seaside Tech Co").count()
    store_count = Store.objects.filter(organization__name="Seaside Tech Co").count()
    device_type_count = DeviceType.objects.count()
    service_type_count = ServiceType.objects.count()
    
    if org_count > 0:
        print("✅ Initial data migration complete!")
        print(f"   - {org_count} Organization: Seaside Tech Co")
        print(f"   - {store_count} Stores (Main Street, Downtown, West Side)")
        print(f"   - {device_type_count} Device Types")
        print(f"   - {service_type_count} Service Types")
        print()
        print("⚠️  Remember to create superuser:")
        print("    python manage.py createsuperuser")


def reverse_service_types(apps, schema_editor):
    """Reverse migration - delete all service types"""
    ServiceType = apps.get_model('appointments', 'ServiceType')
    count = ServiceType.objects.count()
    ServiceType.objects.all().delete()
    print(f"✅ Deleted {count} Service Types")


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_service_types, reverse_service_types),
    ]
