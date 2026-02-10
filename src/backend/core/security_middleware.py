import secrets
import base64
    Uses nonce-based CSP for enhanced security.
        # Generate unique nonce for this request
        nonce_bytes = secrets.token_bytes(16)
        nonce = base64.b64encode(nonce_bytes).decode('utf-8')
        
        # Store nonce in request state for use in templates
        request.state.csp_nonce = nonce
        
        # Content Security Policy - Nonce-based (OWASP best practice)
        # Removed 'unsafe-inline' and 'unsafe-eval' for better security
            f"script-src 'self' 'nonce-{nonce}'; "  # Nonce-based script loading
            f"style-src 'self' 'nonce-{nonce}' https://fonts.googleapis.com; "  # Nonce-based styles