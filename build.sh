#!/usr/bin/env bash
# build.sh - Fixed directory navigation

set -o errexit

echo " Starting TrendMart deployment build..."

# Show current directory and contents for debugging
echo " Current directory: $(pwd)"
echo " Directory contents:"
ls -la

# Find manage.py location
echo " Looking for manage.py..."
find . -name "manage.py" -type f

# Navigate to Django project directory (if nested)
if [ -f "./manage.py" ]; then
    echo " manage.py found in root"
elif [ -f "./trendmart/manage.py" ]; then
    echo " Entering trendmart directory..."
    cd trendmart
elif [ -d "./trendmart" ]; then
    echo " Entering trendmart directory..."
    cd trendmart
else
    echo " Cannot find manage.py"
    exit 1
fi

# Upgrade pip first
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo " Installing dependencies..."
pip install -r requirements.txt

# Verify gunicorn installation
echo " Verifying gunicorn installation..."
pip show gunicorn

# Collect static files
echo " Collecting static files..."
python manage.py collectstatic --no-input

# Run database migrations
echo "  Running database migrations..."
python manage.py migrate

# Sync products from external API
echo " Syncing products from Fake Store API..."
python manage.py sync_products

# Create superuser if doesn't exist
echo "👤 Creating superuser account..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
    print(' Superuser created successfully: admin/admin')
else:
    print('  Superuser already exists')
"

echo " Build completed successfully!"
