# tests/test_tcp_server.py
import socket
import json
import pytest

TCP_HOST = "localhost"
TCP_PORT = 9999

def test_tcp_server_ingest_and_error_handling():
    """Test sending both valid and invalid JSON payloads over a socket to the TCP server."""
    try:
        with socket.create_connection((TCP_HOST, TCP_PORT), timeout=2) as sock:
            # 1. Send a valid article record
            valid_record = {
                "source_id": 1,
                "title": "Test Article Title",
                "url": "http://example.com/test-article",
                "snippet": "This is a test snippet.",
                "published_at": "2026-10-12T12:00:00"
            }
            sock.sendall((json.dumps(valid_record) + "\n").encode("utf-8"))

            # 2. Send a malformed/bad record (invalid JSON string)
            bad_record = "{ this is not valid json }\n"
            sock.sendall(bad_record.encode("utf-8"))

            # 3. Send another valid record to prove the server didn't crash from the bad record
            valid_record_2 = {
                "source_id": 1,
                "title": "Second Test Article",
                "url": "http://example.com/test-article-2",
                "snippet": "Another snippet.",
                "published_at": "2026-10-12T12:05:00"
            }
            sock.sendall((json.dumps(valid_record_2) + "\n").encode("utf-8"))

    except ConnectionRefusedError:
        pytest.fail("TCP server is not running! Make sure python -m app.tcp_server is active during tests.")
