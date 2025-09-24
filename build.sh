#!/usr/bin/env bash
# build.sh - Handle your specific directory structure

set -o errexit

echo "     Starting TrendMart deployment build..."

# Check current location
echo "📁 Current directory: $(pwd)"
echo "    Contents:"
ls -la


# Django project is in ./trendmart/
if [ -d "./trendmart" ] && [ ! -f "./manage.py" ]; then
    echo "📂 Found trendmart directory, entering..."
    cd trendmart
    echo "📍 Now in: $(pwd)"
    ls -la
elif [ ! -f "./manage.py" ]; then
    echo "  Cannot find Django project structure"
    find . -name "manage.py" -type f
    exit 1
fi

# Verify Django structure
if [ ! -f "manage.py" ]; then
    echo "  manage.py not found"
    exit 1
fi

if [ ! -f "trendmart/wsgi.py" ]; then
    echo "wsgi.py not found"
    find . -name "wsgi.py" -type f
    exit 1
fi

echo "Django structure verified"

# Install dependencies (requirements.txt should be in parent or current directory)
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
elif [ -f "../requirements.txt" ]; then
    pip install -r ../requirements.txt
else
    echo "requirements.txt not found"
    find .. -name "requirements.txt" -type f
    exit 1
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Sync products
echo " Syncing products..."
python manage.py sync_products

# Create superuser
echo " Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@gmail.com.com', 'admin')
    print(' Superuser created: admin/admin')
else:
    print('  Superuser already exists')
"

echo " Build completed successfully!"
