# In your project root directory
cat > build.sh << 'EOF'
#!/usr/bin/env bash
# build.sh - Render deployment script

# Exit on error
set -o errexit

echo "🚀 Starting TrendMart deployment build..."

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

# Run database migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Sync products from external API
echo "🔄 Syncing products from Fake Store API..."
python manage.py sync_products

# Create superuser if doesn't exist
echo "👤 Creating superuser account..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@trendmart.com', 'admin')
    print('✅ Superuser created successfully: admin/admin')
else:
    print('ℹ️  Superuser already exists')
"

echo "🎉 Build completed successfully!"
EOF

# Make it executable
chmod +x build.sh
