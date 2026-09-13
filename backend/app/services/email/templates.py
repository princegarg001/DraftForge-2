"""Email templates.

Rendered with Jinja2 autoescaping on. Names, class titles and institution
labels are all teacher-supplied free text, and they land in HTML that arrives
in someone's inbox - unescaped, that is stored XSS delivered by email.

Every template returns both HTML and a plain-text alternative. Text-only
clients are a real minority, and a message with no text part scores worse with
spam filters.
"""

from __future__ import annotations

from dataclasses import dataclass

from jinja2 import Environment, select_autoescape

_env = Environment(
    autoescape=select_autoescape(default_for_string=True, default=True),
    trim_blocks=True,
    lstrip_blocks=True,
)

# Inline styles only, and a table-based shell: email clients strip <style>
# blocks and support little modern CSS.
_LAYOUT = """
<!doctype html>
<html lang="en">
<body style="margin:0;padding:0;background:#f4f5f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f5f7;padding:32px 12px;">
    <tr><td align="center">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#ffffff;border-radius:12px;border:1px solid #e3e5e9;overflow:hidden;">
        <tr><td style="padding:28px 32px 8px;border-bottom:1px solid #eef0f3;">
          <span style="font-size:19px;font-weight:700;color:#1c2434;letter-spacing:-0.3px;">Draft<span style="color:#4f46e5;">Forge</span></span>
        </td></tr>
        <tr><td style="padding:28px 32px 32px;color:#2c3444;font-size:15px;line-height:1.62;">
          {{ body }}
        </td></tr>
        <tr><td style="padding:18px 32px;background:#fafbfc;border-top:1px solid #eef0f3;color:#7a8397;font-size:12px;line-height:1.5;">
          {{ footer }}
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
"""

_BUTTON = (
    'display:inline-block;padding:12px 26px;background:#4f46e5;color:#ffffff;'
    "text-decoration:none;border-radius:8px;font-weight:600;font-size:14px;"
)


@dataclass(frozen=True)
class RenderedEmail:
    subject: str
    html: str
    text: str


def _shell(body_html: str, footer_html: str) -> str:
    # body and footer are pre-escaped fragments, so they are marked safe here
    # rather than re-escaped into visible entities.
    from markupsafe import Markup

    return _env.from_string(_LAYOUT).render(body=Markup(body_html), footer=Markup(footer_html))


def _render(template: str, **context: object) -> str:
    return _env.from_string(template).render(**context)


_STUDENT_INVITE_BODY = """
<p style="margin:0 0 16px;">Hello{% if full_name %} {{ full_name }}{% endif %},</p>
<p style="margin:0 0 16px;">
  <strong>{{ teacher_name }}</strong> has added you to
  <strong>{{ class_name }}</strong>{% if institution %} at {{ institution }}{% endif %}
  on DraftForge, a platform for practising and assessing legal drafting.
</p>
<p style="margin:0 0 24px;">Set your password to get started:</p>
<p style="margin:0 0 24px;"><a href="{{ invite_url }}" style="{{ button_style }}">Accept invitation</a></p>
<p style="margin:0 0 8px;color:#7a8397;font-size:13px;">
  If the button does not work, paste this link into your browser:
</p>
<p style="margin:0 0 20px;word-break:break-all;font-size:13px;">
  <a href="{{ invite_url }}" style="color:#4f46e5;">{{ invite_url }}</a>
</p>
<p style="margin:0;color:#7a8397;font-size:13px;">
  This invitation expires in {{ expires_in_days }} day{{ '' if expires_in_days == 1 else 's' }}.
</p>
"""

_INVITE_FOOTER = """
If you were not expecting this invitation you can safely ignore it - no account
is created until the link is used. This message was sent to {{ email }}.
"""

_STUDENT_INVITE_TEXT = """
Hello{% if full_name %} {{ full_name }}{% endif %},

{{ teacher_name }} has added you to {{ class_name }}{% if institution %} at {{ institution }}{% endif %}
on DraftForge, a platform for practising and assessing legal drafting.

Set your password to get started:
{{ invite_url }}

This invitation expires in {{ expires_in_days }} day{{ '' if expires_in_days == 1 else 's' }}.

If you were not expecting this invitation you can safely ignore it - no account
is created until the link is used. This message was sent to {{ email }}.
"""


def render_student_invitation(
    *,
    email: str,
    full_name: str | None,
    teacher_name: str,
    class_name: str,
    institution: str | None,
    invite_url: str,
    expires_in_days: int,
) -> RenderedEmail:
    context = {
        "email": email,
        "full_name": full_name,
        "teacher_name": teacher_name,
        "class_name": class_name,
        "institution": institution,
        "invite_url": invite_url,
        "expires_in_days": expires_in_days,
        "button_style": _BUTTON,
    }
    return RenderedEmail(
        subject=f"{teacher_name} invited you to {class_name} on DraftForge",
        html=_shell(_render(_STUDENT_INVITE_BODY, **context), _render(_INVITE_FOOTER, **context)),
        text=_render(_STUDENT_INVITE_TEXT, **context).strip(),
    )


_WELCOME_BODY = """
<p style="margin:0 0 16px;">Welcome{% if full_name %}, {{ full_name }}{% endif %}.</p>
<p style="margin:0 0 16px;">
  You have joined <strong>{{ class_name }}</strong>. Your workspace is ready.
</p>
<p style="margin:0 0 24px;"><a href="{{ app_url }}" style="{{ button_style }}">Open DraftForge</a></p>
"""

_WELCOME_TEXT = """
Welcome{% if full_name %}, {{ full_name }}{% endif %}.

You have joined {{ class_name }}. Your workspace is ready.

{{ app_url }}
"""


def render_welcome(
    *, email: str, full_name: str | None, class_name: str, app_url: str
) -> RenderedEmail:
    context = {
        "email": email,
        "full_name": full_name,
        "class_name": class_name,
        "app_url": app_url,
        "button_style": _BUTTON,
    }
    return RenderedEmail(
        subject=f"You have joined {class_name} on DraftForge",
        html=_shell(
            _render(_WELCOME_BODY, **context),
            _render("This message was sent to {{ email }}.", **context),
        ),
        text=_render(_WELCOME_TEXT, **context).strip(),
    )


TEMPLATES = {
    "student_invitation": render_student_invitation,
    "welcome": render_welcome,
}
