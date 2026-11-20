/**
 * Theme & UI Interactions Script
 * ------------------------------------------------------------------
 * Theme tokens live in CSS (DESIGN_SYSTEM.md §2). This script only
 * toggles the theme attributes/classes and wires up micro-interactions.
 * The initial theme is applied synchronously in <head> to avoid FOUC.
 */

(function () {
  'use strict';

  var THEME_KEY = 'ecommerce_theme_preference';

  function getPreferredTheme() {
    var savedTheme = localStorage.getItem(THEME_KEY);
    if (savedTheme) {
      return savedTheme;
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function isDark() {
    return document.documentElement.getAttribute('data-theme') === 'dark' ||
      document.documentElement.classList.contains('dark');
  }

  function applyTheme(theme) {
    var dark = theme === 'dark';
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
    document.documentElement.classList.toggle('dark', dark);

    var nextLabel = dark ? 'Switch to light mode' : 'Switch to dark mode';
    document.querySelectorAll('.theme-toggle-btn').forEach(function (btn) {
      btn.setAttribute('aria-label', nextLabel);
      btn.setAttribute('title', nextLabel);
      btn.setAttribute('aria-pressed', String(dark));
    });
  }

  function toggleTheme() {
    var newTheme = isDark() ? 'light' : 'dark';
    localStorage.setItem(THEME_KEY, newTheme);
    applyTheme(newTheme);
  }

  function initTheme() {
    // Re-apply the theme chosen by the blocking <head> script so the
    // button labels/state stay in sync (and `.dark` classes are set).
    applyTheme(getPreferredTheme());

    var mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    var onSystemChange = function (event) {
      if (!localStorage.getItem(THEME_KEY)) {
        applyTheme(event.matches ? 'dark' : 'light');
      }
    };
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', onSystemChange);
    } else if (mediaQuery.addListener) {
      mediaQuery.addListener(onSystemChange);
    }

    document.querySelectorAll('.theme-toggle-btn').forEach(function (btn) {
      btn.addEventListener('click', toggleTheme);
    });
  }

  function initPasswordToggles() {
    document.querySelectorAll('.password-toggle-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var targetId = btn.getAttribute('data-target') || 'id_password';
        var passwordInput = document.getElementById(targetId);
        if (!passwordInput) return;

        var isPassword = passwordInput.getAttribute('type') === 'password';
        passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
        // CSS drives the eye icons from aria-pressed — no inline styles.
        btn.setAttribute('aria-pressed', String(isPassword));
        btn.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
        btn.setAttribute('title', isPassword ? 'Hide password' : 'Show password');
      });
    });
  }

  function initFormLoading() {
    document.querySelectorAll('form.auth-form').forEach(function (form) {
      form.addEventListener('submit', function () {
        if (!form.checkValidity()) return; // native required validation handles it

        var submitBtn = form.querySelector('.btn-submit');
        if (!submitBtn || submitBtn.disabled) return;

        form.setAttribute('aria-busy', 'true');
        submitBtn.classList.add('btn-loading');
        var submitText = submitBtn.querySelector('.btn-text');
        if (submitText) {
          submitText.setAttribute('data-original-text', submitText.textContent);
          submitText.textContent = submitBtn.getAttribute('data-loading-text') || 'Processing...';
        }

        // Disable after the current event loop tick so the button's
        // name/value (if any) still ships with the request, while
        // duplicate clicks are blocked immediately afterwards.
        setTimeout(function () {
          submitBtn.disabled = true;
        }, 0);
      });
    });
  }

  function initAlertDismissal() {
    document.querySelectorAll('.alert-dismiss').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var alert = btn.closest('.alert');
        if (!alert) return;
        alert.classList.add('is-dismissing');
        window.setTimeout(function () { alert.remove(); }, 220);
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initTheme();
    initPasswordToggles();
    initFormLoading();
    initAlertDismissal();
  });
})();
