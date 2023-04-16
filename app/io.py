import logging
from os import environ

from requests import Response

from app import Config, config

logger = logging.getLogger(__name__)
url = f"https://api.telegram.org/bot{Config.token}/sendMessage"


def safe_reply(payload: dict) -> Response | None:
    if config.is_production:
        logger.info(payload)
    else:
        try:    
            return config.session.post(url, json=payload)
        except Exception as exception:
            logger.error(str(exception))
