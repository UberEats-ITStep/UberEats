from rest_framework import status
from rest_framework.views import exception_handler

_DEFAULT_CODES = {
    status.HTTP_401_UNAUTHORIZED: "not_authenticated",
    status.HTTP_403_FORBIDDEN: "permission_denied",
}


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None or response.status_code not in _DEFAULT_CODES:
        return response

    data = response.data
    if isinstance(data, dict):
        payload = dict(data)
    else:
        items = data if isinstance(data, list) else [data]
        payload = {"detail": " ".join(str(item) for item in items)}

    detail = payload.get("detail", "Authentication or permission error.")
    if not payload.get("code"):
        payload["code"] = getattr(detail, "code", None) or _DEFAULT_CODES[response.status_code]
    payload["detail"] = str(detail)

    response.data = payload
    return response