import json
from dataclasses import dataclass

import firebase_admin
from django.conf import settings
from django.db import IntegrityError, transaction
from firebase_admin import auth, credentials

from users.models import User


class FirebaseAuthenticationError(Exception):
    """Raised when Firebase cannot prove the caller's identity."""


class FirebaseAccountConflict(Exception):
    """Raised when a verified Firebase identity cannot be linked safely."""


@dataclass(frozen=True)
class FirebaseIdentity:
    uid: str
    email: str
    given_name: str = ""
    family_name: str = ""


def _firebase_app():
    if not settings.FIREBASE_AUTH_ENABLED:
        raise FirebaseAuthenticationError("Firebase authentication is unavailable.")
    if not settings.FIREBASE_PROJECT_ID:
        raise FirebaseAuthenticationError("Firebase authentication is not configured.")

    try:
        return firebase_admin.get_app()
    except ValueError:
        try:
            service_account = json.loads(
                settings.GOOGLE_APPLICATION_CREDENTIALS_JSON
            )
            credential = credentials.Certificate(service_account)
        except (TypeError, ValueError, KeyError) as error:
            raise FirebaseAuthenticationError(
                "Firebase authentication is not configured."
            ) from error
        return firebase_admin.initialize_app(
            credential,
            {"projectId": settings.FIREBASE_PROJECT_ID},
        )


def verify_firebase_id_token(id_token: str) -> FirebaseIdentity:
    if not id_token or not isinstance(id_token, str):
        raise FirebaseAuthenticationError("A Firebase ID token is required.")

    try:
        claims = auth.verify_id_token(
            id_token,
            app=_firebase_app(),
            check_revoked=True,
        )
    except (
        ValueError,
        auth.InvalidIdTokenError,
        auth.ExpiredIdTokenError,
        auth.RevokedIdTokenError,
        auth.UserDisabledError,
    ) as error:
        raise FirebaseAuthenticationError(
            "The Firebase ID token is invalid or expired."
        ) from error

    uid = claims.get("uid") or claims.get("sub")
    email = str(claims.get("email") or "").strip().lower()
    if not uid or not email or claims.get("email_verified") is not True:
        raise FirebaseAuthenticationError(
            "Firebase must provide a verified email address."
        )

    return FirebaseIdentity(
        uid=str(uid),
        email=email,
        given_name=str(claims.get("given_name") or "").strip(),
        family_name=str(claims.get("family_name") or "").strip(),
    )


def _available_username(email: str) -> str:
    base = (email.split("@", 1)[0] or "firebase-user")[:140]
    username = base
    suffix = 1
    while User.objects.filter(username=username).exists():
        suffix += 1
        username = f"{base[:140 - len(str(suffix))]}{suffix}"
    return username


@transaction.atomic
def resolve_firebase_user(identity: FirebaseIdentity) -> User:
    linked_user = User.objects.select_for_update().filter(
        firebase_uid=identity.uid
    ).first()
    if linked_user:
        if linked_user.email.lower() != identity.email:
            raise FirebaseAccountConflict(
                "This Firebase identity is linked to a different account."
            )
        return linked_user

    user = User.objects.select_for_update().filter(
        email__iexact=identity.email
    ).first()
    if user and user.firebase_uid:
        raise FirebaseAccountConflict(
            "This email is already linked to another Firebase identity."
        )

    try:
        if user:
            user.firebase_uid = identity.uid
            user.is_verified = True
            user.save(update_fields=["firebase_uid", "is_verified"])
        else:
            user = User(
                username=_available_username(identity.email),
                email=identity.email,
                firebase_uid=identity.uid,
                is_verified=True,
                first_name=identity.given_name[:150],
                last_name=identity.family_name[:150],
            )
            user.set_unusable_password()
            user.save()
    except IntegrityError as error:
        raise FirebaseAccountConflict(
            "This Firebase identity is already linked to another account."
        ) from error

    return user
