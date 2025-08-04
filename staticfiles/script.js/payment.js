// Payment Gateway Integration JavaScript

console.log('PaymentGateway JS loaded');

class PaymentGateway {
    constructor() {
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const paymentForm = document.getElementById('payment-form');
        if (paymentForm) {
            // Temporarily disable JavaScript form interception to allow Django form submission
            // paymentForm.addEventListener('submit', this.handlePaymentSubmission.bind(this));
        }
        const decreaseBtn = document.querySelector('.decrease-room');
        const increaseBtn = document.querySelector('.increase-room');
        if (decreaseBtn) decreaseBtn.addEventListener('click', this.decreaseRoomCount.bind(this));
        if (increaseBtn) increaseBtn.addEventListener('click', this.increaseRoomCount.bind(this));
    }

    async handlePaymentSubmission(event) {
        event.preventDefault();
        console.log('Form submit intercepted');
        const form = event.target;
        const roomId = form.getAttribute('data-room-id');
        this.showLoading();

        try {
            const formData = {
                guest_name: form.querySelector('[name="guest_name"]').value,
                guest_email: form.querySelector('[name="guest_email"]').value,
                guest_phone: form.querySelector('[name="guest_phone"]').value,
                check_in: form.querySelector('[name="check_in"]').value,
                check_out: form.querySelector('[name="check_out"]').value,
                num_adults: parseInt(form.querySelector('[name="num_adults"]').value) || 1,
                num_children: parseInt(form.querySelector('[name="num_children"]').value) || 0,
                num_rooms: parseInt(form.querySelector('[name="num_rooms"]').value) || 1,
            };

            if (!this.validateFormData(formData)) {
                this.hideLoading();
                return;
            }

            const response = await this.createPaymentOrder(roomId, formData);
            console.log('Payment order response:', response);

            if (response.success) {
                window.location.href = `/payment/process/${response.order_id}/`;
            } else {
                this.showError('Payment initialization failed: ' + response.error);
                this.hideLoading();
            }
        } catch (error) {
            console.error('Payment error:', error);
            this.showError('An error occurred while processing your payment. Please try again.');
            this.hideLoading();
        }
    }

    async createPaymentOrder(roomId, formData) {
        const response = await fetch(`/payment/create-order/${roomId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(formData)
        });
        return await response.json();
    }

    validateFormData(data) {
        const errors = [];
        if (!data.guest_name.trim()) errors.push('Guest name is required');
        if (!data.guest_email.trim()) errors.push('Email is required');
        else if (!this.isValidEmail(data.guest_email)) errors.push('Please enter a valid email address');
        if (!data.guest_phone.trim()) errors.push('Phone number is required');
        if (!data.check_in) errors.push('Check-in date is required');
        if (!data.check_out) errors.push('Check-out date is required');
        if (data.check_in && data.check_out && new Date(data.check_in) >= new Date(data.check_out)) errors.push('Check-out date must be after check-in date');
        if (errors.length > 0) {
            this.showError(errors.join('<br>'));
            return false;
        }
        return true;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    showLoading() {
        const submitBtn = document.querySelector('#payment-form button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
        }
    }

    hideLoading() {
        const submitBtn = document.querySelector('#payment-form button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Checkout';
        }
    }

    showError(message) {
        const existingAlert = document.querySelector('.alert-danger');
        if (existingAlert) existingAlert.remove();
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        const form = document.getElementById('payment-form');
        if (form) form.parentNode.insertBefore(alertDiv, form);
    }

    increaseRoomCount() {
        const roomCountElement = document.querySelector('.room-count');
        const numRoomsInput = document.querySelector('[name="num_rooms"]');
        if (roomCountElement && numRoomsInput) {
            let currentCount = parseInt(roomCountElement.textContent);
            currentCount += 1;
            roomCountElement.textContent = currentCount;
            numRoomsInput.value = currentCount;
            this.updateTotalAmount();
        }
    }

    decreaseRoomCount() {
        const roomCountElement = document.querySelector('.room-count');
        const numRoomsInput = document.querySelector('[name="num_rooms"]');
        if (roomCountElement && numRoomsInput) {
            let currentCount = parseInt(roomCountElement.textContent);
            if (currentCount > 1) {
                currentCount -= 1;
                roomCountElement.textContent = currentCount;
                numRoomsInput.value = currentCount;
                this.updateTotalAmount();
            }
        }
    }

    updateTotalAmount() {
        const roomCount = parseInt(document.querySelector('.room-count').textContent);
        const pricePerRoom = parseFloat(document.querySelector('.room-price').getAttribute('data-price'));
        const totalElement = document.querySelector('.total-amount');
        if (totalElement) {
            totalElement.textContent = `₹${(roomCount * pricePerRoom).toFixed(2)}`;
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    new PaymentGateway();
    const numRoomsInput = document.querySelector('[name="num_rooms"]');
    const roomCountElement = document.querySelector('.room-count');
    if (numRoomsInput && roomCountElement) {
        roomCountElement.textContent = numRoomsInput.value || "1";
    }
});

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

// Utility function to validate date range
function validateDateRange(checkIn, checkOut) {
    const checkInDate = new Date(checkIn);
    const checkOutDate = new Date(checkOut);
    const today = new Date();
    
    if (checkInDate < today) {
        return 'Check-in date cannot be in the past';
    }
    
    if (checkOutDate <= checkInDate) {
        return 'Check-out date must be after check-in date';
    }
    
    return null;
} 

