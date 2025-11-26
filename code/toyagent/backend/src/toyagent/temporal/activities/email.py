"""Email tool using exchangelib."""

import logging
from dataclasses import dataclass
from typing import Any

from temporalio import activity

from toyagent.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class EmailParams:
    """Parameters for sending an email."""

    to: list[str]
    subject: str
    body: str
    cc: list[str] | None = None
    bcc: list[str] | None = None
    html_body: str | None = None


@activity.defn
async def send_email(params: dict[str, Any]) -> dict[str, Any]:
    """
    Send an email using Exchange Web Services.

    Args:
        params: Dictionary containing:
            - to: List of recipient email addresses
            - subject: Email subject
            - body: Email body (plain text)
            - cc: Optional list of CC recipients
            - bcc: Optional list of BCC recipients
            - html_body: Optional HTML body

    Returns:
        Dictionary with success status and message_id or error
    """
    settings = get_settings()

    # Validate settings
    if not all([settings.email_server, settings.email_username, settings.email_primary_smtp_address, settings.email_password]):
        logger.error("Email configuration is incomplete")
        return {
            "success": False,
            "error": "Email configuration is incomplete. Please set EMAIL_SERVER, EMAIL_USERNAME, EMAIL_PRIMARY_SMTP_ADDRESS, and EMAIL_PASSWORD.",
        }

    try:
        # Import here to avoid import errors if exchangelib is not installed
        from zoneinfo import ZoneInfo
        from exchangelib import (
            Account,
            Configuration,
            Credentials,
            DELEGATE,
            Message,
            Mailbox,
            HTMLBody,
        )

        # Parse parameters - handle both string and list formats
        to_param = params.get("to", [])
        if isinstance(to_param, str):
            to_list = [to_param] if to_param else []
        else:
            to_list = to_param

        subject = params.get("subject", "")
        body = params.get("body", "")

        cc_param = params.get("cc", [])
        if isinstance(cc_param, str):
            cc_list = [cc_param] if cc_param else []
        else:
            cc_list = cc_param or []

        bcc_param = params.get("bcc", [])
        if isinstance(bcc_param, str):
            bcc_list = [bcc_param] if bcc_param else []
        else:
            bcc_list = bcc_param or []

        html_body = params.get("html_body")

        if not to_list:
            return {"success": False, "error": "No recipients specified"}

        # Set up credentials (RWTH format: ab123456@rwth-aachen.de)
        credentials = Credentials(
            username=settings.email_username,
            password=settings.email_password,
        )

        # Configure Exchange server
        config = Configuration(
            server=settings.email_server,
            credentials=credentials,
        )

        # Create account with primary SMTP address (actual email address)
        account = Account(
            primary_smtp_address=settings.email_primary_smtp_address,
            credentials=credentials,
            config=config,
            autodiscover=False,
            access_type=DELEGATE,
            default_timezone=ZoneInfo("Europe/Berlin"),
        )

        # Create message
        message = Message(
            account=account,
            subject=subject,
            body=HTMLBody(html_body) if html_body else body,
            to_recipients=[Mailbox(email_address=addr) for addr in to_list],
        )

        if cc_list:
            message.cc_recipients = [Mailbox(email_address=addr) for addr in cc_list]

        if bcc_list:
            message.bcc_recipients = [Mailbox(email_address=addr) for addr in bcc_list]

        # Send the message
        message.send()

        logger.info(f"Email sent successfully to {to_list}")
        return {
            "success": True,
            "message": f"Email sent successfully to {', '.join(to_list)}",
            "recipients": to_list,
            "subject": subject,
        }

    except ImportError:
        logger.error("exchangelib is not installed")
        return {
            "success": False,
            "error": "exchangelib is not installed. Please install it with: pip install exchangelib",
        }
    except Exception as e:
        logger.exception(f"Failed to send email: {e}")
        return {
            "success": False,
            "error": f"Failed to send email: {str(e)}",
        }
