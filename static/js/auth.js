/**
 * Authentication JavaScript
 * Handles login and registration forms
 */

// ===============================
// Premium Particle Animation
// ===============================

function createParticles() {
    const container = document.getElementById('particlesContainer');
    if (!container) return;
    
    const particleCount = 50;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Random position
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        
        // Random size (2-6px)
        const size = 2 + Math.random() * 4;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        // Random animation duration (10-30s)
        const duration = 10 + Math.random() * 20;
        particle.style.animationDuration = `${duration}s`;
        
        // Random delay
        const delay = Math.random() * 5;
        particle.style.animationDelay = `${delay}s`;
        
        container.appendChild(particle);
    }
}

// Initialize particles on load
document.addEventListener('DOMContentLoaded', createParticles);

const API_BASE = '/api/auth';

// DOM Elements
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const authTabs = document.querySelectorAll('.auth-tab');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');
const errorText = document.getElementById('errorText');
const successText = document.getElementById('successText');

// Tab switching
authTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const tabName = tab.dataset.tab;
        
        // Update active tab
        authTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // Show/hide forms
        if (tabName === 'login') {
            loginForm.style.display = 'block';
            registerForm.style.display = 'none';
        } else {
            loginForm.style.display = 'none';
            registerForm.style.display = 'block';
        }
        
        // Clear messages
        hideMessages();
    });
});

// Login form submission
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessages();
    
    const loginBtn = document.getElementById('loginBtn');
    const loginBtnText = document.getElementById('loginBtnText');
    const loginSpinner = document.getElementById('loginSpinner');
    
    // Get form data
    const formData = new FormData(loginForm);
    const data = {
        username: formData.get('username').trim(),
        password: formData.get('password')
    };
    
    // Validate
    if (!data.username || !data.password) {
        showError('Please fill in all fields');
        return;
    }
    
    // Show loading
    loginBtn.disabled = true;
    loginBtnText.style.display = 'none';
    loginSpinner.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Login failed');
        }
        
        // Store token
        localStorage.setItem('auth_token', result.access_token);
        localStorage.setItem('user', JSON.stringify(result.user));
        
        // Show success and redirect
        showSuccess('Login successful! Redirecting...');
        setTimeout(() => {
            window.location.href = '/app';
        }, 1000);
        
    } catch (error) {
        showError(error.message);
        loginBtn.disabled = false;
        loginBtnText.style.display = 'inline';
        loginSpinner.style.display = 'none';
    }
});

// Register form submission
registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessages();
    
    const registerBtn = document.getElementById('registerBtn');
    const registerBtnText = document.getElementById('registerBtnText');
    const registerSpinner = document.getElementById('registerSpinner');
    
    // Get form data
    const formData = new FormData(registerForm);
    const data = {
        email: formData.get('email').trim(),
        username: formData.get('username').trim(),
        password: formData.get('password'),
        confirm_password: formData.get('confirm_password')
    };
    
    // Validate
    if (!data.email || !data.username || !data.password || !data.confirm_password) {
        showError('Please fill in all fields');
        return;
    }
    
    if (data.password !== data.confirm_password) {
        showError('Passwords do not match');
        return;
    }
    
    if (data.password.length < 8) {
        showError('Password must be at least 8 characters');
        return;
    }
    
    if (data.username.length < 3) {
        showError('Username must be at least 3 characters');
        return;
    }
    
    // Show loading
    registerBtn.disabled = true;
    registerBtnText.style.display = 'none';
    registerSpinner.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Registration failed');
        }
        
        // Show success and auto-login
        showSuccess('Account created! Logging you in...');
        
        // Auto-login
        setTimeout(async () => {
            try {
                const loginResponse = await fetch(`${API_BASE}/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        username: data.email,
                        password: data.password
                    })
                });
                
                const loginResult = await loginResponse.json();
                
                if (loginResponse.ok) {
                    localStorage.setItem('auth_token', loginResult.access_token);
                    localStorage.setItem('user', JSON.stringify(loginResult.user));
                    window.location.href = '/app';
                }
            } catch (error) {
                // If auto-login fails, switch to login tab
                authTabs[0].click();
                showSuccess('Account created! Please login.');
            }
        }, 1500);
        
    } catch (error) {
        showError(error.message);
        registerBtn.disabled = false;
        registerBtnText.style.display = 'inline';
        registerSpinner.style.display = 'none';
    }
});

// Helper functions
function showError(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'flex';
    successMessage.style.display = 'none';
}

function showSuccess(message) {
    successText.textContent = message;
    successMessage.style.display = 'flex';
    errorMessage.style.display = 'none';
}

function hideMessages() {
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';
}

// Check if already logged in
if (localStorage.getItem('auth_token')) {
    window.location.href = '/app';
}
