/**
 * AuraStore Theme & UI Interactions Script
 * ------------------------------------------------------------------
 * Calm, product-first retail interaction layer.
 * Includes:
 *  - Theme switching & synchronization (blocking head script handles initial load)
 *  - IntersectionObserver staggered reveal on scroll
 *  - Sticky header hairline on scroll
 *  - Flash alerts auto-dismiss with hover/focus pause
 *  - Cart counter bump animation & AJAX quick-add integration
 *  - Mobile search bar toggle
 *  - Accessible password visibility toggling & form submission debounce
 */

(function () {
  'use strict';

  var THEME_KEY = 'ecommerce_theme_preference';

  /* ---------------------------------------------------------
     1. Theme Management (Zero-FOUC + accessible toggle)
     --------------------------------------------------------- */
  function getPreferredTheme() {
    var savedTheme = localStorage.getItem(THEME_KEY);
    if (savedTheme) {
      return savedTheme;
    }
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
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

  /* ---------------------------------------------------------
     2. Staggered Scroll Reveal (IntersectionObserver)
     --------------------------------------------------------- */
  function initScrollReveal() {
    var reveals = document.querySelectorAll('.reveal-on-scroll');
    if (!reveals.length) return;

    var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion || !('IntersectionObserver' in window)) {
      reveals.forEach(function (el) {
        el.classList.add('is-visible');
      });
      return;
    }

    var observer = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        }
      });
    }, {
      rootMargin: '0px 0px -40px 0px',
      threshold: 0.1
    });

    reveals.forEach(function (el) {
      observer.observe(el);
    });
  }

  /* ---------------------------------------------------------
     3. Header Hairline Border on Scroll
     --------------------------------------------------------- */
  function initHeaderScroll() {
    var header = document.getElementById('app-header');
    if (!header) return;

    var onScroll = function () {
      if (window.scrollY > 12) {
        header.classList.add('header-scrolled');
      } else {
        header.classList.remove('header-scrolled');
      }
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ---------------------------------------------------------
     4. Cart Counter Bump & AJAX Quick-Add Support
     --------------------------------------------------------- */
  function bumpCartCounter() {
    var counter = document.getElementById('global-cart-counter');
    if (!counter) return;
    counter.classList.remove('counter-bump');
    // Force reflow
    void counter.offsetWidth;
    counter.classList.add('counter-bump');
    setTimeout(function () {
      counter.classList.remove('counter-bump');
    }, 300);
  }

  function initQuickAdd() {
    document.querySelectorAll('.quick-add-form').forEach(function (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.disabled = true;

        var formData = new FormData(form);
        fetch(form.action, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
          }
        })
        .then(function (res) {
          return res.json();
        })
        .then(function (data) {
          if (data && data.success) {
            var counter = document.getElementById('global-cart-counter');
            if (counter && data.cart_count !== undefined) {
              counter.textContent = data.cart_count;
              bumpCartCounter();
            }
            if (submitBtn) {
              var origText = submitBtn.innerHTML;
              submitBtn.innerHTML = '<span>Added &#10003;</span>';
              setTimeout(function () {
                submitBtn.innerHTML = origText;
                submitBtn.disabled = false;
              }, 1600);
            }
          } else {
            form.submit(); // fallback to standard POST
          }
        })
        .catch(function () {
          form.submit();
        });
      });
    });
  }

  /* ---------------------------------------------------------
     5. Accessible Flash Alerts (Auto-dismiss with pause)
     --------------------------------------------------------- */
  function initAlertDismissal() {
    document.querySelectorAll('.alert').forEach(function (alert) {
      var dismissBtn = alert.querySelector('.alert-dismiss');
      var timerId = null;
      var remaining = 5000;
      var startTime = Date.now();

      function dismiss() {
        alert.classList.add('is-dismissing');
        window.setTimeout(function () {
          alert.remove();
        }, 220);
      }

      function startTimer() {
        startTime = Date.now();
        timerId = window.setTimeout(dismiss, remaining);
      }

      function pauseTimer() {
        if (timerId) {
          window.clearTimeout(timerId);
          remaining -= (Date.now() - startTime);
          timerId = null;
        }
      }

      if (dismissBtn) {
        dismissBtn.addEventListener('click', function () {
          pauseTimer();
          dismiss();
        });
      }

      // Pause auto-dismiss when user is actively reading/focusing
      alert.addEventListener('mouseenter', pauseTimer);
      alert.addEventListener('mouseleave', function () {
        if (remaining > 0) startTimer();
      });
      alert.addEventListener('focusin', pauseTimer);
      alert.addEventListener('focusout', function () {
        if (remaining > 0) startTimer();
      });

      startTimer();
    });
  }

  /* ---------------------------------------------------------
     6. Password Visibility Toggle
     --------------------------------------------------------- */
  function initPasswordToggles() {
    document.querySelectorAll('.password-toggle-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var targetId = btn.getAttribute('data-target') || 'id_password';
        var passwordInput = document.getElementById(targetId);
        if (!passwordInput) return;

        var isPassword = passwordInput.getAttribute('type') === 'password';
        passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
        btn.setAttribute('aria-pressed', String(isPassword));
        btn.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
        btn.setAttribute('title', isPassword ? 'Hide password' : 'Show password');
      });
    });
  }

  /* ---------------------------------------------------------
     7. Form Double-Submit Prevention & Loading States
     --------------------------------------------------------- */
  function initFormLoading() {
    document.querySelectorAll('form.auth-form').forEach(function (form) {
      form.addEventListener('submit', function () {
        if (!form.checkValidity()) return;

        var submitBtn = form.querySelector('.btn-submit');
        if (!submitBtn || submitBtn.disabled) return;

        form.setAttribute('aria-busy', 'true');
        submitBtn.classList.add('btn-loading');
        var submitText = submitBtn.querySelector('.btn-text');
        if (submitText) {
          submitText.setAttribute('data-original-text', submitText.textContent);
          submitText.textContent = submitBtn.getAttribute('data-loading-text') || 'Processing...';
        }

        setTimeout(function () {
          submitBtn.disabled = true;
        }, 0);
      });
    });
  }

  /* ---------------------------------------------------------
     8. Mobile Search Expand / Collapse
     --------------------------------------------------------- */
  function initMobileSearch() {
    var searchToggle = document.getElementById('search-toggle-btn');
    var searchWrapper = document.getElementById('header-search-wrapper');
    var searchClose = document.getElementById('header-search-close');
    var searchInput = document.getElementById('header-search-input');

    if (!searchToggle || !searchWrapper) return;

    searchToggle.addEventListener('click', function () {
      searchWrapper.classList.toggle('is-open');
      if (searchWrapper.classList.contains('is-open') && searchInput) {
        searchInput.focus();
      }
    });

    if (searchClose) {
      searchClose.addEventListener('click', function () {
        searchWrapper.classList.remove('is-open');
      });
    }
  }

  /* ---------------------------------------------------------
     9. Product Detail Interactions (Zoom, Stepper, Tabs)
     --------------------------------------------------------- */
  function updateMainImage(url, alt, btn) {
    var mainImg = document.getElementById('main-product-img');
    var zoomStage = document.getElementById('zoom-stage');
    if (mainImg) {
      mainImg.src = url;
      mainImg.alt = alt;
    }
    if (zoomStage) {
      zoomStage.classList.remove('is-zoomed');
    }
    document.querySelectorAll('.product-thumb-btn').forEach(function (b) {
      b.classList.remove('active');
    });
    if (btn) {
      btn.classList.add('active');
    }
  }

  function switchProductTab(tabId, btn) {
    document.querySelectorAll('.product-tab-btn').forEach(function (b) {
      b.classList.remove('active');
      b.setAttribute('aria-selected', 'false');
    });
    document.querySelectorAll('.product-tab-panel').forEach(function (panel) {
      panel.classList.remove('active');
      panel.hidden = true;
    });

    if (btn) {
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
    }
    var targetPanel = document.getElementById(tabId + '-panel');
    if (targetPanel) {
      targetPanel.classList.add('active');
      targetPanel.hidden = false;
    }
  }

  function initProductDetailInteractions() {
    // 1. Click to Zoom on Product Main Image
    var zoomTrigger = document.getElementById('zoom-toggle-btn');
    var zoomStage = document.getElementById('zoom-stage');
    if (zoomStage) {
      var toggleZoom = function () {
        zoomStage.classList.toggle('is-zoomed');
      };
      zoomStage.addEventListener('click', toggleZoom);
      if (zoomTrigger) {
        zoomTrigger.addEventListener('click', function (e) {
          e.stopPropagation();
          toggleZoom();
        });
      }
    }

    // 2. Quantity Stepper
    var decBtn = document.getElementById('qty-dec-btn');
    var incBtn = document.getElementById('qty-inc-btn');
    var qtyInput = document.getElementById('product-qty-input');

    if (qtyInput) {
      var minVal = parseInt(qtyInput.getAttribute('min'), 10) || 1;
      var maxVal = parseInt(qtyInput.getAttribute('max'), 10) || 9999;

      if (decBtn) {
        decBtn.addEventListener('click', function () {
          var current = parseInt(qtyInput.value, 10) || 1;
          if (current > minVal) {
            qtyInput.value = current - 1;
          }
        });
      }

      if (incBtn) {
        incBtn.addEventListener('click', function () {
          var current = parseInt(qtyInput.value, 10) || 1;
          if (current < maxVal) {
            qtyInput.value = current + 1;
          }
        });
      }
    }
  }

  /* ---------------------------------------------------------
     10. Mobile Collapsible Order Summary
     --------------------------------------------------------- */
  function initSummaryToggle() {
    var toggleBtn = document.getElementById('summary-toggle-btn');
    if (!toggleBtn) return;
    var panel = toggleBtn.closest('.checkout-summary-panel');
    if (!panel) return;

    var toggleText = toggleBtn.querySelector('.toggle-text');

    toggleBtn.addEventListener('click', function () {
      var isExpanded = toggleBtn.getAttribute('aria-expanded') === 'true';
      var newState = !isExpanded;
      toggleBtn.setAttribute('aria-expanded', String(newState));
      panel.classList.toggle('is-expanded', newState);
      if (toggleText) {
        toggleText.textContent = newState ? 'Hide order summary' : 'Show order summary';
      }
    });
  }

  /* ---------------------------------------------------------
     DOM Ready Bootstrapper
     --------------------------------------------------------- */
  document.addEventListener('DOMContentLoaded', function () {
    initTheme();
    initScrollReveal();
    initHeaderScroll();
    initQuickAdd();
    initAlertDismissal();
    initPasswordToggles();
    initFormLoading();
    initMobileSearch();
    initProductDetailInteractions();
    initSummaryToggle();
  });

  // Expose helpers on window for external triggers
  window.AuraStore = {
    bumpCartCounter: bumpCartCounter,
    updateMainImage: updateMainImage,
    switchProductTab: switchProductTab
  };
})();
