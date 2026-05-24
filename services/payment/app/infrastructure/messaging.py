import os
import socket

class MessageBroker:
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

    def send_event(self, topic, message):
        # Graceful sandbox fallback
        return False

    def check_health(self):
        try:
            # Non-blocking TCP socket check for Kafka bootstrap servers
            primary_server = self.bootstrap_servers.split(",")[0]
            host, port = primary_server.split(":")
            port = int(port)
            s = socket.create_connection((host, port), timeout=0.5)
            s.close()
            return True
        except Exception:
            return False
