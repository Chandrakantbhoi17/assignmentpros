#!/bin/bash

# Static Files Debugging Script
echo "🔍 Debugging static files issue..."

# Check if static files exist
echo "1. Checking if static files exist:"
if [ -f "/root/assignmentpros/staticfiles/images/hero.png" ]; then
    echo "✅ Hero image exists: /root/assignmentpros/staticfiles/images/hero.png"
    ls -la /root/assignmentpros/staticfiles/images/hero.png
else
    echo "❌ Hero image NOT found: /root/assignmentpros/staticfiles/images/hero.png"
fi

if [ -f "/root/assignmentpros/staticfiles/accounts/images/admin.png" ]; then
    echo "✅ Admin image exists: /root/assignmentpros/staticfiles/accounts/images/admin.png"
    ls -la /root/assignmentpros/staticfiles/accounts/images/admin.png
else
    echo "❌ Admin image NOT found: /root/assignmentpros/staticfiles/accounts/images/admin.png"
fi

# Check nginx configuration
echo -e "\n2. Checking nginx configuration:"
sudo nginx -t

# Check nginx static file location
echo -e "\n3. Checking nginx static file location:"
if [ -d "/root/assignmentpros/staticfiles" ]; then
    echo "✅ Static files directory exists"
    echo "Directory contents:"
    ls -la /root/assignmentpros/staticfiles/
else
    echo "❌ Static files directory does NOT exist"
fi

# Test direct file access
echo -e "\n4. Testing direct file access:"
if [ -f "/root/assignmentpros/staticfiles/images/hero.png" ]; then
    echo "✅ File is readable by current user"
    file /root/assignmentpros/staticfiles/images/hero.png
else
    echo "❌ File is not readable"
fi

# Check nginx error logs
echo -e "\n5. Recent nginx error logs:"
sudo tail -10 /var/log/nginx/error.log

# Test HTTP access
echo -e "\n6. Testing HTTP access to static files:"
echo "Testing hero.png:"
curl -I http://localhost/static/images/hero.png 2>/dev/null | head -1
echo "Testing admin.png:"
curl -I http://localhost/static/accounts/images/admin.png 2>/dev/null | head -1

# Check file permissions
echo -e "\n7. File permissions:"
ls -la /root/assignmentpros/staticfiles/
ls -la /root/assignmentpros/staticfiles/images/
ls -la /root/assignmentpros/staticfiles/accounts/images/

echo -e "\n8. Nginx process info:"
ps aux | grep nginx

echo -e "\n🔍 Debugging complete!"

