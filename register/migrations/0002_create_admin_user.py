from django.db import migrations


def create_admin(apps, schema_editor):
    # Import the Command class from your existing file
    from register.create_admin import Command

    # Create an instance and run its handle method
    command = Command()
    command.handle()


class Migration(migrations.Migration):
    dependencies = [
        ('register', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_admin),
    ]