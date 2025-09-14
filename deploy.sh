#!/bin/bash

# AssignmentPros Deployment Script
echo "🚀 Starting AssignmentPros deployment..."

# Set environment variables for production
export DEBUG=False
export ALLOWED_HOSTS="assignmentpros.in,www.assignmentpros.in"

# Navigate to project directory
cd /root/assignmentpros

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Remove old static files
echo "🧹 Cleaning old static files..."
rm -rf /root/assignmentpros/staticfiles/*

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Verify static files were collected
echo "🔍 Verifying static files..."
echo "Hero image location:"
ls -la /root/assignmentpros/staticfiles/images/hero.png
echo "Account images location:"
ls -la /root/assignmentpros/staticfiles/accounts/images/

# Set proper permissions for static files
echo "🔐 Setting permissions..."
chmod -R 755 /root/assignmentpros/staticfiles/
chmod -R 755 /root/assignmentpros/media/
chown -R www-data:www-data /root/assignmentpros/staticfiles/
chown -R www-data:www-data /root/assignmentpros/media/

# Test nginx configuration
echo "🔧 Testing nginx configuration..."
sudo nginx -t

# Restart services
echo "🔄 Restarting services..."
sudo systemctl restart nginx
sudo systemctl restart gunicorn  # if using gunicorn
# OR restart your Docker container if using Docker

# Test static file access
echo "🧪 Testing static file access..."
curl -I http://localhost/static/images/hero.png
curl -I http://localhost/static/accounts/images/admin.png

echo "✅ Deployment completed!"
echo "🌐 Your site should now be accessible at https://assignmentpros.in"
echo "📁 Static files should be accessible at:"
echo "   - http://assignmentpros.in/static/images/hero.png"
echo "   - http://assignmentpros.in/static/accounts/images/admin.png"
