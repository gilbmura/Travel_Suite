import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import User

# Delete existing admin user if it exists
User.objects.filter(username='admin').delete()

# Create new admin user
admin_user = User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin123'
)

print(f"✅ Admin user created successfully!")
print(f"Username: admin")
print(f"Password: admin123")
print(f"Is superuser: {admin_user.is_superuser}")
print(f"Is staff: {admin_user.is_staff}")
