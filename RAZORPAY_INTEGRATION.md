# Razorpay Integration Documentation

## Overview
This project integrates Razorpay payment gateway for task payments in the assignment management system. Students can make payments in two halves for their assigned tasks.

## Features
- **Two-phase payment system**: Students can pay in first half and second half
- **Secure payment processing**: Uses Razorpay's secure payment gateway
- **Payment verification**: Server-side verification of payment signatures
- **Payment tracking**: Complete payment history and status tracking
- **User-friendly interface**: Clean UI with payment status indicators

## Setup Requirements

### 1. Install Dependencies
```bash
pip install razorpay django-widget-tweaks
```

### 2. Environment Variables
Add your Razorpay credentials to `settings.py`:
```python
RAZORPAY_KEY_ID = 'your_key_id_here'
RAZORPAY_SECRET_KEY = 'your_secret_key_here'
```

### 3. Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

## How It Works

### 1. Payment Flow
1. **Admin sets task amount**: Admin can set the total amount for a task
2. **Student views payment options**: Student sees two payment buttons (First Half, Second Half)
3. **Payment initiation**: Student clicks a payment button
4. **Order creation**: Backend creates a Razorpay order
5. **Payment processing**: Razorpay handles the payment
6. **Verification**: Backend verifies payment signature
7. **Status update**: Payment status is updated in database

### 2. Models
- **Task**: Added `is_paid` field to track overall payment status
- **TaskPayment**: Tracks individual payment transactions (first_half, second_half)

### 3. Views
- **CreateRazorpayOrderView**: Creates Razorpay orders for payments
- **PaymentSuccessView**: Handles payment verification and status updates
- **TaskDetailView**: Enhanced to show payment status and options

### 4. URLs
- `/create-razorpay-order`: Endpoint for creating payment orders
- `/payment-success`: Endpoint for payment verification

## Usage

### For Students
1. Navigate to a task with an amount set
2. Click "Pay First Half" or "Pay Second Half" button
3. Complete payment through Razorpay gateway
4. Payment status will be updated automatically

### For Admins
1. Set task amount using the amount input field
2. View payment status in task details
3. Monitor payment completion

## Security Features
- **CSRF protection**: All forms and AJAX requests are CSRF protected
- **Payment signature verification**: Server-side verification using Razorpay's utility
- **User authorization**: Only task creators can make payments
- **Duplicate payment prevention**: System prevents duplicate payments for the same phase

## File Structure
```
assignments/
├── models.py              # Task and TaskPayment models
├── views.py               # Payment views and logic
├── urls.py                # Payment URL patterns
├── templatetags/          # Custom template filters
│   └── assignment_filters.py
└── templates/assignments/
    └── task_view.html     # Enhanced with payment UI
```

## Testing
1. Create a task with an amount
2. Login as a student who created the task
3. Navigate to task details
4. Test payment flow using Razorpay test credentials

## Notes
- Uses Razorpay test mode credentials (update for production)
- Payments are split into two equal halves
- Task is marked as fully paid only when both halves are completed
- All payment data is securely stored and verified
