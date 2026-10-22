class BlastoError(Exception):  # base class for errors blasto raises on purpose
    status_code: int = 500  # HTTP status to return; subclasses override it
    code: str = "internal_error"  # short machine-readable name; subclasses override it

    def __init__(self, message: str) -> None:
        super().__init__(message)  # normal Exception setup, so logs show the message
        self.message = message  # kept for the JSON response


class ApplicationNotFound(BlastoError):
    status_code = 404
    code = "application_not_found"

    def __init__(self, application_id: int) -> None:
        super().__init__(f"Application {application_id} not found")


class NotAuthorized(BlastoError):
    status_code = 401
    code = "not_authorized"

    def __init__(self) -> None:
        super().__init__("Missing or invalid API key")
