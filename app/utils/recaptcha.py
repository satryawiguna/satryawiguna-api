"""
reCAPTCHA Enterprise verification utility.

Calls the Google Cloud reCAPTCHA Enterprise assessment REST API
via the public endpoint using an API key.

Reference:
https://cloud.google.com/recaptcha-enterprise/docs/create-assessment
"""
import logging

import httpx

from app.core.config import settings
from app.core.exceptions import BusinessLogicError

logger = logging.getLogger(__name__)

_RECAPTCHA_API_URL = (
    "https://recaptchaenterprise.googleapis.com/v1/projects/"
    "{project_id}/assessments?key={api_key}"
)
_DEFAULT_ACTION = "contact_form"
_HTTP_TIMEOUT_SECONDS = 10


async def verify_recaptcha_token(
    token: str,
    expected_action: str = _DEFAULT_ACTION,
) -> bool:
    """
    Verify a reCAPTCHA Enterprise token by calling the Google assessment API.

    Args:
        token: The reCAPTCHA Enterprise token received from the frontend.
        expected_action: The action name that the token should be bound to
                         (must match what was passed to
                          ``grecaptcha.enterprise.execute()``).

    Returns:
        ``True`` when the token is valid and the risk score meets the
        configured threshold.

    Raises:
        BusinessLogicError: If the token is invalid, the action mismatches,
                            the score is too low, or the API call itself fails.
    """
    if not settings.RECAPTCHA_API_KEY:
        logger.warning("RECAPTCHA_API_KEY is not configured — skipping verification")
        return True

    url = _RECAPTCHA_API_URL.format(
        project_id=settings.RECAPTCHA_PROJECT_ID,
        api_key=settings.RECAPTCHA_API_KEY,
    )

    payload = {
        "event": {
            "token": token,
            "siteKey": settings.RECAPTCHA_SITE_KEY,
            "expectedAction": expected_action,
        }
    }

    try:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT_SECONDS) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            assessment = response.json()
    except httpx.TimeoutException:
        logger.error("reCAPTCHA Enterprise API timed out")
        raise BusinessLogicError(
            "reCAPTCHA verification timed out. Please try again."
        )
    except httpx.HTTPStatusError as exc:
        logger.error(
            "reCAPTCHA Enterprise API returned %s: %s",
            exc.response.status_code,
            exc.response.text,
        )
        raise BusinessLogicError("reCAPTCHA verification failed. Please try again.")
    except httpx.RequestError as exc:
        logger.error("reCAPTCHA Enterprise connection error: %s", exc)
        raise BusinessLogicError(
            "Unable to verify reCAPTCHA. Please try again later."
        )

    # --- Token validity check ---
    token_props = assessment.get("tokenProperties", {})
    if not token_props.get("valid"):
        invalid_reason = token_props.get("invalidReason", "unknown")
        logger.warning("reCAPTCHA token invalid — reason: %s", invalid_reason)
        raise BusinessLogicError("Invalid reCAPTCHA token. Please try again.")

    # --- Action check ---
    actual_action = token_props.get("action")
    if actual_action != expected_action:
        logger.warning(
            "reCAPTCHA action mismatch — expected=%s, actual=%s",
            expected_action,
            actual_action,
        )
        raise BusinessLogicError("reCAPTCHA verification failed. Please try again.")

    # --- Risk score check ---
    risk_analysis = assessment.get("riskAnalysis", {})
    score = risk_analysis.get("score", 0.0)
    if score < settings.RECAPTCHA_SCORE_THRESHOLD:
        logger.warning(
            "reCAPTCHA score %.2f below threshold %.2f",
            score,
            settings.RECAPTCHA_SCORE_THRESHOLD,
        )
        raise BusinessLogicError(
            "reCAPTCHA verification failed. Please try again."
        )

    logger.debug("reCAPTCHA verification passed (score=%.2f)", score)
    return True
