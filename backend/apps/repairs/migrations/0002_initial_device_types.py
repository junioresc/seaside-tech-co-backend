# Generated migration for initial Device Types data

from django.db import migrations


def populate_device_types(apps, schema_editor):
    """Create initial Device Types"""
    DeviceType = apps.get_model('repairs', 'DeviceType')
    
    # Idempotency check
    if DeviceType.objects.exists():
        print("Device Types already exist, skipping...")
        return
    
    device_types = [
        {
            "code": "laptop",
            "name": "Laptop",
            "description": "Portable computer with integrated display and keyboard",
            "help_text": "Common repair types: screen replacement, keyboard repair, battery replacement, motherboard issues, charging port repair"
        },
        {
            "code": "desktop-pc",
            "name": "Desktop PC",
            "description": "Stationary computer with separate display and peripherals",
            "help_text": "Common repair types: power supply replacement, motherboard issues, RAM upgrades, hard drive replacement, graphics card installation"
        },
        {
            "code": "phone",
            "name": "Phone",
            "description": "Mobile smartphone device (iPhone, Android, etc.)",
            "help_text": "Common repair types: screen replacement, battery replacement, charging port repair, camera repair, water damage"
        },
        {
            "code": "tablet",
            "name": "Tablet",
            "description": "Touch-screen tablet device (iPad, Android tablet, etc.)",
            "help_text": "Common repair types: screen replacement, battery replacement, charging port repair, digitizer replacement"
        },
        {
            "code": "smartwatch",
            "name": "Smartwatch",
            "description": "Wearable smartwatch device (Apple Watch, Android Wear, etc.)",
            "help_text": "Common repair types: screen replacement, battery replacement, band replacement, water damage"
        },
        {
            "code": "smart-tv",
            "name": "Smart TV",
            "description": "Smart television device (Samsung, LG, etc.)",
            "help_text": "Common repair types: screen replacement, motherboard repair, power supply issues, software updates"
        },
        {
            "code": "smart-speaker",
            "name": "Smart Speaker",
            "description": "Smart speaker device (Amazon Echo, Google Home, etc.)",
            "help_text": "Common repair types: speaker replacement, microphone issues, power supply repair, software reset"
        },
        {
            "code": "gaming-console",
            "name": "Gaming Console",
            "description": "Gaming console (PlayStation, Xbox, Nintendo Switch, etc.)",
            "help_text": "Common repair types: disc drive replacement, power supply issues, HDMI port repair, controller repair, overheating issues"
        },
        {
            "code": "other",
            "name": "Other",
            "description": "Other electronic device requiring repair",
            "help_text": "For devices that don't fit into standard categories. Please provide detailed description of device and issue."
        },
    ]
    
    for device_type_data in device_types:
        DeviceType.objects.create(**device_type_data)
    
    print(f"✅ Created {len(device_types)} Device Types")


def reverse_device_types(apps, schema_editor):
    """Reverse migration - delete all device types"""
    DeviceType = apps.get_model('repairs', 'DeviceType')
    count = DeviceType.objects.count()
    DeviceType.objects.all().delete()
    print(f"✅ Deleted {count} Device Types")


class Migration(migrations.Migration):

    dependencies = [
        ('repairs', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_device_types, reverse_device_types),
    ]
