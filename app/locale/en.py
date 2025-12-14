"""
English localization messages for VisionCrafterAI Backend API
All error messages, success messages, and API responses are centralized here
"""

# ============================================================================
# AUTHENTICATION MESSAGES
# ============================================================================

AUTH_MESSAGES = {
    # Registration
    "user_registered_successfully": "User registered successfully",
    "email_already_exists": "Email or username already registered",
    "registration_failed": "Failed to register user",
    
    # Login
    "login_successful": "Login successful",
    "invalid_credentials": "Invalid email or password",
    
    # Token
    "token_expired": "Token has expired",
    "token_invalid": "Invalid or expired token",
    "token_missing_user_id": "Invalid token - missing user ID",
    "refresh_token_invalid": "Invalid or expired refresh token",
    "token_refreshed": "Token refreshed successfully",
}

# ============================================================================
# USER MESSAGES
# ============================================================================

USER_MESSAGES = {
    # Profile
    "user_not_found": "User not found",
    "profile_retrieved": "Profile retrieved successfully",
    "profile_updated": "Profile updated successfully",
    "profile_update_failed": "Failed to update profile",
    
    # Account status
    "account_inactive": "Account is inactive",
    "account_suspended": "Account has been suspended",
}

# ============================================================================
# VALIDATION MESSAGES
# ============================================================================

VALIDATION_MESSAGES = {
    # General
    "required_field": "This field is required",
    "invalid_format": "Invalid format",
    
    # Email
    "email_invalid": "Invalid email format",
    "email_required": "Email is required",
    
    # Password
    "password_too_short": "Password must be at least 8 characters",
    "password_required": "Password is required",
    
    # Username
    "username_too_short": "Username must be at least 3 characters",
    "username_too_long": "Username cannot exceed 50 characters",
    "username_required": "Username is required",
    
    # Full name
    "fullname_required": "Full name is required",
    "fullname_too_long": "Full name cannot exceed 100 characters",
}

# ============================================================================
# HTTP STATUS MESSAGES
# ============================================================================

HTTP_MESSAGES = {
    # Success
    "success": "Request completed successfully",
    "created": "Resource created successfully",
    "updated": "Resource updated successfully",
    "deleted": "Resource deleted successfully",
    
    # Client Errors
    "bad_request": "Bad request",
    "unauthorized": "Authentication required",
    "forbidden": "Access forbidden",
    "not_found": "Resource not found",
    "conflict": "Resource already exists",
    
    # Server Errors
    "internal_error": "Internal server error",
    "service_unavailable": "Service temporarily unavailable",
}

# ============================================================================
# DATABASE MESSAGES
# ============================================================================

DATABASE_MESSAGES = {
    "connection_failed": "Database connection failed",
    "query_failed": "Database query failed",
    "transaction_failed": "Database transaction failed",
    "integrity_error": "Database integrity constraint violated",
}

# ============================================================================
# GENERAL MESSAGES
# ============================================================================

GENERAL_MESSAGES = {
    "welcome": "Welcome to VisionCrafterAI Backend API",
    "service_healthy": "Service is running",
    "maintenance_mode": "Service is under maintenance",
}

# ============================================================================
# HELPER FUNCTION TO GET MESSAGES
# ============================================================================

def get_message(category: str, key: str) -> str:
    """
    Get a message by category and key
    
    Args:
        category: Message category (e.g., 'auth', 'user', 'validation')
        key: Message key within the category
        
    Returns:
        str: The message text, or a default message if not found
    """
    categories = {
        'auth': AUTH_MESSAGES,
        'user': USER_MESSAGES,
        'validation': VALIDATION_MESSAGES,
        'http': HTTP_MESSAGES,
        'database': DATABASE_MESSAGES,
        'general': GENERAL_MESSAGES,
    }
    
    category_messages = categories.get(category, {})
    return category_messages.get(key, f"Message not found: {category}.{key}")
