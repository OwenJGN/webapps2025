from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Creates initial admin user if no admin exists'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(is_staff=True).exists():
            try:
                if not User.objects.filter(username='admin1').exists():
                    admin = User.objects.create_user(
                        username='admin1',
                        email='admin1@example.com',
                        password='admin1',
                        first_name='Admin',
                        last_name='User',
                        is_staff=True
                    )

                    # The profile is created by the signal, just update the balance
                    if hasattr(admin, 'profile'):
                        admin.profile.balance = 750.00
                        admin.profile.save()

                    self.stdout.write(self.style.SUCCESS('Admin user created successfully'))
                else:
                    self.stdout.write(self.style.WARNING('Admin user already exists'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating admin user: {e}'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))