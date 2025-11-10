"""
Input sanitization utilities
Prevents injection attacks (XSS, XML injection, CSV injection)
"""

import re
from xml.sax.saxutils import escape as xml_escape
from typing import Any


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and special character issues

    Args:
        filename: Original filename

    Returns:
        Sanitized filename (alphanumeric, dots, dashes, underscores only)
    """
    # Remove any path components
    filename = filename.split('/')[-1].split('\\')[-1]

    # Keep only alphanumeric, dots, dashes, underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

    # Prevent hidden files and parent directory references
    filename = filename.lstrip('.')

    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"

    # Limit length
    if len(filename) > 255:
        name_part = filename[:200]
        ext_part = filename[-50:]
        filename = name_part + ext_part

    return filename


def sanitize_xml_content(value: Any) -> str:
    """
    Sanitize content for XML output

    Escapes XML special characters: &, <, >, ", '

    Args:
        value: Value to sanitize

    Returns:
        XML-safe string
    """
    # Convert to string
    text = str(value).strip()

    # Escape XML special characters
    # & -> &amp;
    # < -> &lt;
    # > -> &gt;
    # " -> &quot;
    # ' -> &apos;
    text = xml_escape(text, entities={
        '"': '&quot;',
        "'": '&apos;'
    })

    return text


def sanitize_csv_cell(value: Any) -> str:
    """
    Sanitize CSV cell value to prevent formula injection

    Excel formulas start with: =, +, -, @, tab, carriage return
    This is a CSV injection vulnerability (CVE-2014-3524)

    Args:
        value: Cell value

    Returns:
        Sanitized string safe for CSV export
    """
    # Convert to string
    text = str(value).strip()

    # Check if value starts with dangerous characters
    dangerous_prefixes = ['=', '+', '-', '@', '\t', '\r']

    if text and text[0] in dangerous_prefixes:
        # Prefix with single quote to force text interpretation
        text = "'" + text

    # Also escape pipe characters used in some formula injections
    text = text.replace('|', '\\|')

    return text


def sanitize_field_name(field_name: str) -> str:
    """
    Sanitize field/column name

    Allows: alphanumeric, underscores, spaces, hyphens
    Prevents: Special characters that could cause issues

    Args:
        field_name: Original field name

    Returns:
        Sanitized field name
    """
    # Replace problematic characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_\s-]', '_', field_name)

    # Trim whitespace
    sanitized = sanitized.strip()

    # Ensure not empty
    if not sanitized:
        sanitized = "unnamed_field"

    return sanitized


def validate_url(url: str) -> bool:
    """
    Validate URL to prevent SSRF attacks

    Blocks:
    - localhost/127.0.0.1
    - Private IP ranges (10.x, 172.16-31.x, 192.168.x)
    - Link-local addresses (169.254.x)
    - File:// protocol

    Args:
        url: URL to validate

    Returns:
        True if URL is safe, False otherwise
    """
    url_lower = url.lower()

    # Block dangerous protocols
    dangerous_protocols = ['file://', 'ftp://', 'gopher://', 'data://', 'dict://']
    for protocol in dangerous_protocols:
        if url_lower.startswith(protocol):
            return False

    # Block localhost
    localhost_patterns = [
        'localhost',
        '127.0.0.1',
        '127.',
        '0.0.0.0',
        '[::1]',
        '::1'
    ]
    for pattern in localhost_patterns:
        if pattern in url_lower:
            return False

    # Block private IP ranges
    private_ip_patterns = [
        r'10\.\d{1,3}\.\d{1,3}\.\d{1,3}',
        r'172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}',
        r'192\.168\.\d{1,3}\.\d{1,3}',
        r'169\.254\.\d{1,3}\.\d{1,3}'  # Link-local
    ]
    for pattern in private_ip_patterns:
        if re.search(pattern, url):
            return False

    return True


def validate_sftp_host(host: str) -> bool:
    """
    Validate SFTP host to prevent SSRF

    Args:
        host: Hostname or IP address

    Returns:
        True if host is safe, False otherwise
    """
    host_lower = host.lower()

    # Block localhost
    if host_lower in ['localhost', '127.0.0.1', '::1', '0.0.0.0']:
        return False

    # Block private IP ranges
    private_ip_patterns = [
        r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$',
        r'^172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}$',
        r'^192\.168\.\d{1,3}\.\d{1,3}$',
        r'^169\.254\.\d{1,3}\.\d{1,3}$'
    ]
    for pattern in private_ip_patterns:
        if re.match(pattern, host):
            return False

    return True


def sanitize_log_message(message: str, sensitive_patterns: list[str] = None) -> str:
    """
    Sanitize log message to prevent sensitive data leakage

    Redacts:
    - API keys
    - Passwords
    - Tokens
    - Email addresses (partial)
    - Custom sensitive patterns

    Args:
        message: Log message
        sensitive_patterns: Additional regex patterns to redact

    Returns:
        Sanitized log message
    """
    # Default sensitive patterns
    patterns = [
        (r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]+)(["\']?)', r'\1REDACTED\3'),
        (r'(password["\']?\s*[:=]\s*["\']?)([^"\']+)(["\']?)', r'\1REDACTED\3'),
        (r'(token["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-\.]+)(["\']?)', r'\1REDACTED\3'),
        (r'(secret["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]+)(["\']?)', r'\1REDACTED\3'),
        # Partial email redaction: user@example.com -> u***r@example.com
        (r'\b([a-zA-Z0-9._%+-])[a-zA-Z0-9._%+-]+([a-zA-Z0-9._%+-])@', r'\1***\2@'),
    ]

    # Add custom patterns
    if sensitive_patterns:
        for pattern in sensitive_patterns:
            patterns.append((pattern, 'REDACTED'))

    # Apply redaction
    sanitized = message
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    return sanitized


# Test function
if __name__ == "__main__":
    # Test filename sanitization
    assert sanitize_filename("../../../etc/passwd") == "etc_passwd"
    assert sanitize_filename("test<script>.csv") == "test_script_.csv"
    print("Filename sanitization: PASS")

    # Test XML sanitization
    assert sanitize_xml_content("<script>alert('xss')</script>") == "&lt;script&gt;alert('xss')&lt;/script&gt;"
    print("XML sanitization: PASS")

    # Test CSV injection prevention
    assert sanitize_csv_cell("=1+1") == "'=1+1"
    assert sanitize_csv_cell("normal text") == "normal text"
    print("CSV injection prevention: PASS")

    # Test URL validation
    assert validate_url("http://localhost:8080") == False
    assert validate_url("http://192.168.1.1") == False
    assert validate_url("http://example.com") == True
    print("URL validation: PASS")

    # Test log sanitization
    log = "API_KEY=sk_test_1234567890 password=secret123"
    sanitized = sanitize_log_message(log)
    assert "sk_test_1234567890" not in sanitized
    assert "secret123" not in sanitized
    print("Log sanitization: PASS")

    print("\nAll sanitization tests passed!")
