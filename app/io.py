from __future__ import annotations

import logging

from requests import Response

from app import config

logger = logging.getLogger(__name__)
url = f"https://api.telegram.org/bot{config.token}/sendMessage"


def safe_reply(payload: dict) -> Response | None:
    if config.is_production:
        try:
            return config.session.post(url, json=payload)
        except Exception as exception:
            logger.error(exception)
    else:
        logger.info(payload)
        logger.info(f"Characters in payload['text']: {len(payload['text'])}")
