#!/usr/bin/env bash

set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate

# Crear superusuario automáticamente
echo "Creando superusuario..."
DJANGO_SUPERUSER_USERNAME=Kevin \
DJANGO_SUPERUSER_EMAIL=kevxn_garcxa@outlook.com \
DJANGO_SUPERUSER_PASSWORD=julianpan123 \
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='Kevin').exists():
    User.objects.create_superuser(
        username=os.environ.get('DJANGO_SUPERUSER_USERNAME'),
        email=os.environ.get('DJANGO_SUPERUSER_EMAIL'),
        password=os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    );
    print('Superusuario creado exitosamente.');
else:
    print('El superusuario ya existe.');
"