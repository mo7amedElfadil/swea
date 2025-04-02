import logging
import signal
import sys

from app.queue.queue_service import QueueService
from app.services.mailing import EmailService

# Initialize services
email_service = EmailService()
queue_service = QueueService()


def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown."""
    logging.info("Received signal %s. Shutting down gracefully...", signum)
    queue_service.shutdown()
    sys.exit(0)


def main():
    """Worker function to process tasks from the queue."""
    logging.basicConfig(level=logging.INFO)

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Register task processors
    queue_service.register_task_processor(
        "send_email", email_service.send_email
    )

    logging.info("Starting task queue worker...")
    queue_service.process_queue()


if __name__ == "__main__":
    main()
