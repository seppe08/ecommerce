/**
 * Theme & UI Interactions Script
 * Handles dark/light theme switching with zero FOUC, password visibility toggle,
 * form submission loading indicators, and dismissible alerts.
 */

(function () {
  'use strict';

  // 1. Theme Toggle Engine
  const THEME_KEY = 'ecommerce_theme_preference';

  function getPreferredTheme() {
    const savedTheme = localStorage.getItem(THEME_KEY);
    if (savedTheme) {
      return savedTheme;
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    if (theme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }

    const toggleBtns = document.querySelectorAll('.theme-toggle-btn');
    toggleBtns.forEach((btn) => {
      btn.setAttribute(
        'aria-label',
        theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'
      );
      btn.setAttribute('title', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    });
  }

  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    localStorage.setItem(THEME_KEY, newTheme);
    applyTheme(newTheme);
  }

  // Listen for system theme changes if user has not set a preference
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem(THEME_KEY)) {
      applyTheme(e.matches ? 'dark' : 'light');
    }
  });

  // 2. DOM Ready Initializations
  document.addEventListener('DOMContentLoaded', () => {
    // Attach event listeners to all theme toggle buttons
    const toggleBtns = document.querySelectorAll('.theme-toggle-btn');
    toggleBtns.forEach((btn) => {
      btn.addEventListener('click', toggleTheme);
    });

    // 3. Password Visibility Toggle
    const passwordToggleButtons = document.querySelectorAll('.password-toggle-btn');
    passwordToggleButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        const targetId = btn.getAttribute('data-target') || 'id_password';
        const passwordInput = document.getElementById(targetId);
        if (!passwordInput) return;

        const isPassword = passwordInput.getAttribute('type') === 'password';
        passwordInput.setAttribute('type', isPassword ? 'text' : 'password');

        const eyeOpen = btn.querySelector('.icon-eye-open');
        const eyeClosed = btn.querySelector('.icon-eye-closed');

        if (eyeOpen && eyeClosed) {
          if (isPassword) {
            eyeOpen.style.display = 'none';
            eyeClosed.style.display = 'block';
            btn.setAttribute('aria-label', 'Hide password');
            btn.setAttribute('title', 'Hide password');
          } else {
            eyeOpen.style.display = 'block';
            eyeClosed.style.display = 'none';
            btn.setAttribute('aria-label', 'Show password');
            btn.setAttribute('title', 'Show password');
          }
        }
      });
    });

    // 4. Form Submit Loading State
    const authForms = document.querySelectorAll('form.auth-form');
    authForms.forEach((form) => {
      form.addEventListener('submit', function (e) {
        if (!form.checkValidity()) {
          return; // Let standard validation fire if required
        }
        const submitBtn = form.querySelector('.btn-submit');
        if (submitBtn && !submitBtn.disabled) {
          submitBtn.classList.add('btn-loading');
          const submitText = submitBtn.querySelector('.btn-text');
          if (submitText) {
            submitText.setAttribute('data-original-text', submitText.textContent);
            submitText.textContent = 'Signing in...';
          }
          // Note: we do not set submitBtn.disabled = true immediately because
          // some browsers fail to submit the form button name/value if disabled prematurely.
          setTimeout(() => {
            submitBtn.style.pointerEvents = 'none';
          }, 50);
        }
      });
    });

    // 5. Alert Dismissal
    const dismissButtons = document.querySelectorAll('.alert-dismiss');
    dismissButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        const alert = btn.closest('.alert');
        if (alert) {
          alert.style.opacity = '0';
          alert.style.transform = 'translateY(-6px)';
          alert.style.transition = 'all 0.2s ease-out';
          setTimeout(() => alert.remove(), 200);
        }
      });
    });
  });
})();
