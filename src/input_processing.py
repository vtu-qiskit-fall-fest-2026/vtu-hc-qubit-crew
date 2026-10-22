
import ipaddress
import socket
from io import BytesIO
from urllib.parse import urlparse

import requests
import pytesseract
from bs4 import BeautifulSoup
from PIL import Image, ImageOps


FEATURES = [
    "upfront_fee",
    "unverified_sender",
    "unrealistic_pay",
    "pressure_tactics",
    "missing_details",
]

FEATURE_LABELS = {
    "upfront_fee": "Requests an upfront payment",
    "unverified_sender": "Sender identity is unverified",
    "unrealistic_pay": "Payment or rewards seem unusually high",
    "pressure_tactics": "Uses pressure or urgency tactics",
    "missing_details": "Important opportunity details are missing",
}


def extract_screenshot_text(image_file):
    """Extract readable text from an uploaded screenshot."""
    try:
        image = Image.open(image_file)
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        text = pytesseract.image_to_string(image)
    except Exception as exc:
        raise ValueError(
            "Could not read this image. Please upload a valid screenshot."
        ) from exc

    if not text.strip():
        raise ValueError(
            "No readable text was found. Try a clearer screenshot."
        )

    return text.strip()


def validate_public_url(url):
    """Allow public HTTP(S) URLs and reject private or local destinations."""
    if not isinstance(url, str) or len(url) > 2048:
        raise ValueError("Please provide a valid webpage URL.")

    parsed = urlparse(url.strip())

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Use a complete public URL starting with http:// or https://.")

    if parsed.username or parsed.password:
        raise ValueError("URLs containing embedded login credentials are not allowed.")

    hostname = parsed.hostname.lower()

    if hostname == "localhost" or hostname.endswith(".localhost"):
        raise ValueError("Localhost URLs are not allowed.")

    try:
        addresses = socket.getaddrinfo(
            hostname, parsed.port or (443 if parsed.scheme == "https" else 80)
        )
    except socket.gaierror as exc:
        raise ValueError("The website address could not be resolved.") from exc

    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])

        if not ip.is_global:
            raise ValueError("Private or non-public network addresses are not allowed.")

    return parsed.geturl()


def extract_webpage_text(url):
    """Fetch and extract readable text from a public webpage."""
    safe_url = validate_public_url(url)

    try:
        response = requests.get(
            safe_url,
            timeout=10,
            headers={"User-Agent": "QuantumShield/1.0"},
            allow_redirects=False,
            stream=True,
        )
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()

        if "text/html" not in content_type:
            raise ValueError("This link does not appear to point to an HTML webpage.")

        content = response.raw.read(1_000_001, decode_content=True)

        if len(content) > 1_000_000:
            raise ValueError("The webpage is too large to analyze (maximum 1 MB).")

        soup = BeautifulSoup(content, "html.parser")

        for element in soup(["script", "style", "noscript", "svg"]):
            element.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if not text:
            raise ValueError("No readable webpage text was found.")

        return text[:20_000]

    except requests.RequestException as exc:
        raise ValueError(
            "Could not retrieve this webpage. It may be unavailable or block automated access."
        ) from exc


def suggest_indicators(text):
    """Suggest reviewable warning indicators from extracted text."""
    text = text.lower()

    keyword_groups = {
        "upfront_fee": [
            "upfront fee", "registration fee", "pay first",
            "processing fee", "deposit required",
        ],
        "unverified_sender": [
            "unverified sender", "unknown recruiter",
            "unofficial email", "contact me on telegram",
        ],
        "unrealistic_pay": [
            "guaranteed income", "earn thousands daily",
            "unlimited earnings", "get rich quick",
        ],
        "pressure_tactics": [
            "act now", "limited time", "immediate action",
            "urgent", "only today",
        ],
        "missing_details": [
            "no experience needed", "details after payment",
            "job description coming soon",
        ],
    }

    suggestions = {}

    for feature, keywords in keyword_groups.items():
        suggestions[feature] = int(
            any(keyword in text for keyword in keywords)
        )

    return suggestions
