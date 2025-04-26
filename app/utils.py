import re
from urllib.parse import quote

def wrap_links(body: str, email_id: str, tracking_domain: str) -> str:
    url_pattern = re.compile(
        r'((https?://)?(www\.)?[\w\-\.]+\.[a-zA-Z]{2,}(/[^\s"<]*)?)'
    )
    def replacer(match):
        url = match.group(0)
        if not url.startswith("http"):
            url_for_tracking = "https://" + url
        else:
            url_for_tracking = url
        tracked_url = (
            f"{tracking_domain}/api/track/click"
            f"?email_id={email_id}&url={quote(url_for_tracking)}"
        )
        visible_text = re.sub(r'^https?://', '', url)
        return f'<a href="{tracked_url}">{visible_text}</a>'
    return url_pattern.sub(replacer, body)

def get_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                return part.get_payload(decode=True).decode(errors="replace")
    else:
        return msg.get_payload(decode=True).decode(errors="replace")
    return ""

def extract_email(addr: str) -> str:
    match = re.search(r'<([^>]+)>', addr)
    if match:
        return match.group(1)
    return addr.strip()