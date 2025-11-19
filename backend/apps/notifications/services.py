from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import boto3
from botocore.config import Config
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self, use_ses: bool | None = None) -> None:
        self.use_ses = use_ses if use_ses is not None else not settings.DEBUG
        if self.use_ses:
            self._ses = boto3.client(
                "ses",
                region_name=getattr(settings, "AWS_REGION_NAME", None),
                config=Config(retries={"max_attempts": 3, "mode": "standard"}),
            )
        else:
            self._ses = None

    def send_template(
        self,
        to: List[str],
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        from_email: Optional[str] = None,
    ) -> None:
        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        html_body = render_to_string(template_name, context)
        text_body = render_to_string(template_name.replace(".html", ".txt"), context)
        if self._ses:
            logger.info("Sending email via SES to %s", to)
            self._ses.send_email(
                Source=from_email,
                Destination={"ToAddresses": to},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {
                        "Text": {"Data": text_body},
                        "Html": {"Data": html_body},
                    },
                },
            )
        else:
            logger.info("Sending email via SMTP to %s", to)
            msg = EmailMultiAlternatives(subject=subject, body=text_body, from_email=from_email, to=to)
            msg.attach_alternative(html_body, "text/html")
            msg.send(fail_silently=False)


class SMSSender:
    def __init__(self, enabled: bool | None = None) -> None:
        self.enabled = enabled if enabled is not None else not settings.DEBUG
        if self.enabled:
            self._sns = boto3.client(
                "sns",
                region_name=getattr(settings, "AWS_REGION_NAME", None),
                config=Config(retries={"max_attempts": 3, "mode": "standard"}),
            )
        else:
            self._sns = None

    def send(self, to_e164: str, message: str) -> None:
        if self._sns:
            logger.info("Sending SMS via SNS to %s", to_e164)
            self._sns.publish(PhoneNumber=to_e164, Message=message)
        else:
            logger.info("[DEV] SMS to %s: %s", to_e164, message)


