"""
Security middleware for AuraStore.
Applies defense-in-depth HTTP response headers including Content-Security-Policy (CSP),
Referrer-Policy, and Permissions-Policy.
"""

from django.conf import settings


class SecurityHeadersMiddleware:
    """
    Middleware that attaches modern defense-in-depth security headers
    to every outgoing HTTP response:
    - Content-Security-Policy (CSP)
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.csp_header = getattr(
            settings,
            "CONTENT_SECURITY_POLICY",
            (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com data:; "
                "img-src 'self' data: blob:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            ),
        )
        self.referrer_policy = getattr(
            settings,
            "REFERRER_POLICY",
            "strict-origin-when-cross-origin",
        )
        self.permissions_policy = getattr(
            settings,
            "PERMISSIONS_POLICY",
            "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
        )

    def __call__(self, request):
        response = self.get_response(request)

        if "Content-Security-Policy" not in response:
            response["Content-Security-Policy"] = self.csp_header

        if "Referrer-Policy" not in response:
            response["Referrer-Policy"] = self.referrer_policy

        if "Permissions-Policy" not in response:
            response["Permissions-Policy"] = self.permissions_policy

        return response
