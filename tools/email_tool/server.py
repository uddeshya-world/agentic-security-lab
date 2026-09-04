import os
import smtplib
import uuid
from email.mime.text import MIMEText

from tools.base import InvokeResult, is_secure, make_tool_app
from tools.email_tool.schema import get_schema

MAILHOG_SMTP_HOST = os.environ.get("MAILHOG_SMTP_HOST", "mailhog")
MAILHOG_SMTP_PORT = int(os.environ.get("MAILHOG_SMTP_PORT", "1025"))

ALLOWED_DOMAINS_SECURE = {"example.test"}


def _send(to: str, subject: str, body: str) -> str:
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "agent@lab.local"
    msg["To"] = to
    msg_id = f"<{uuid.uuid4()}@lab.local>"
    msg["Message-ID"] = msg_id
    with smtplib.SMTP(MAILHOG_SMTP_HOST, MAILHOG_SMTP_PORT) as smtp:
        smtp.send_message(msg)
    return msg_id


def _invoke(args: dict) -> InvokeResult:
    to = args.get("to", "")
    subject = args.get("subject", "")
    body = args.get("body", "")

    if is_secure():
        domain = to.split("@")[-1].lower()
        if domain not in ALLOWED_DOMAINS_SECURE:
            return InvokeResult(
                result={"error": f"recipient domain '{domain}' not allow-listed"},
                side_effects=[],
            )

    msg_id = _send(to, subject, body)
    return InvokeResult(
        result={"sent": True, "message_id": msg_id},
        side_effects=[{"type": "email_sent", "to": to, "message_id": msg_id}],
    )


app = make_tool_app("email_tool", get_schema, _invoke)
