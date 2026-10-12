import json
import logging
import socketserver
from app.database import SessionLocal
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [TCP Server] %(message)s"
)
logger = logging.getLogger(__name__)

class TCPIngestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        client_ip = self.client_address[0]
        logger.info(f"Connection established from {client_ip}:{self.client_address[1]}")

        db = SessionLocal()
        try:
            # makefile creates a file-like stream for line-by-line reading
            with self.request.makefile('r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    # 1. Handle malformed JSON safely
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        logger.warning(f"Malformed JSON received from {client_ip}: {line}")
                        continue

                    # 2. Validate required fields
                    required_fields = ("source_id", "url", "title")
                    if not all(field in record for field in required_fields):
                        logger.warning(f"Validation failed (missing fields): {record}")
                        continue

                    # 3. Insert into Database with duplicate check
                    try:
                        existing = db.execute(
                            text("SELECT id FROM articles WHERE url = :url"),
                            {"url": record["url"]}
                        ).fetchone()

                        if not existing:
                            db.execute(text("""
                                INSERT INTO articles (source_id, title, url, snippet, published_at)
                                VALUES (:source_id, :title, :url, :snippet, :published_at)
                            """), record)
                            db.commit()
                            logger.info(f"Inserted new article: {record['title'][:50]}...")
                    except Exception as db_err:
                        db.rollback()
                        logger.error(f"Database error during insertion: {db_err}")

        except (ConnectionResetError, BrokenPipeError):
            logger.warning(f"Connection abruptly dropped by client {client_ip}")
        except Exception as e:
            logger.error(f"Unexpected error handling client {client_ip}: {e}")
        finally:
            db.close()
            logger.info(f"Connection closed for {client_ip}")

class ThreadedTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    with ThreadedTCPServer((HOST, PORT), TCPIngestHandler) as server:
        logger.info(f"TCP Ingest Server running on {HOST}:{PORT}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Shutting down TCP server gracefully...")
            server.shutdown()
