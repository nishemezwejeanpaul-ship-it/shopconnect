from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            "success": False,
            "error": {
                "code": "ERROR",
                "message": "Une erreur est survenue.",
            }
        }
        
        # Check if it's a validation error (field-specific errors instead of a generic 'detail')
        if isinstance(response.data, dict) and 'detail' not in response.data:
            field = next(iter(response.data))
            error_data["error"]["field"] = field
            
            field_errors = response.data[field]
            msg = field_errors[0] if isinstance(field_errors, list) else field_errors
            error_data["error"]["message"] = str(msg)
            error_data["error"]["code"] = "VALIDATION_ERROR"
        else:
            # Standard DRF 'detail' errors
            msg = str(response.data.get('detail', exc))
            error_data["error"]["message"] = msg
            
            if response.status_code == 401:
                # Map token expiration error
                if "invalid or expired" in msg.lower() or "token is invalid" in msg.lower():
                    error_data["error"]["code"] = "TOKEN_EXPIRED"
                    error_data["error"]["message"] = "Votre session a expiré. Veuillez vous reconnecter."
                else:
                    error_data["error"]["code"] = "UNAUTHORIZED"
            elif response.status_code == 403:
                error_data["error"]["code"] = "FORBIDDEN"
            elif response.status_code == 404:
                error_data["error"]["code"] = "NOT_FOUND"

        response.data = error_data

    return response
