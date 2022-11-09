ALREADY_VERIFIED_ERROR: dict[str, str] = {"error": "Your account is already verified"}

CONFIGURATION_IS_REQUIRED_ERROR: dict[str, str] = {
    "error": "Сonfiguration should contain fields like: email,phone,show_my_planned_events"
}

GET_PLANNED_IVENTS_ERROR: dict[str, str] = {
    "error": "Get planned ivents can only contain: day(d), month(m) and year(y)"
}

MAX_AGE_VALUE_ERROR: dict[str, str] = {"error": "Age must not exceed 100 years old"}
MIN_AGE_VALUE_ERROR: dict[str, str] = {"error": "Age must be at least 6 years old"}

WRONG_PASSWORD_ERROR: dict[str, str] = {"error": "Wrong old password"}
PASSWORDS_DO_NOT_MATCH_ERROR: dict[str, str] = {"error": "Passwords do not match"}
NO_EMAIL_REGISTRATION_ERROR: dict[str, str] = {"error": "Users should have a Email"}
INVALID_CREDENTIALS_ERROR: dict[str, str] = {"error": "Invalid credentials, try again"}
NOT_VERIFIED_BY_EMAIL_ERROR: dict[str, str] = {"error": "Email is not verified"}
NO_SUCH_USER_ERROR: dict[str, str] = {"error": "No such user"}
NO_PERMISSIONS_ERROR: dict[str, str] = {"error": "You have no permissions to do this"}
BAD_CODE_ERROR: dict[str, str] = {"error": "Bad verify code"}

CODE_EXPIRED_ERROR: dict[str, str] = {"error": "This code expired"}
NO_SUCH_IMAGE_ERROR: dict[str, str] = {"error": "Image not found"}

THIS_EMAIL_ALREADY_IN_USE_ERROR: dict[str, str] = {
    "error": "This email is already in use"
}
