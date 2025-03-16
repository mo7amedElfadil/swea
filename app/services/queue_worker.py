import logging

from app.services.mailing import EmailService
from app.services.queue_service import QueueService

# Initialize Mongo connection

email_service = EmailService()
queue_service = QueueService()


def main():
    """Worker function to process tasks from the queue"""
    logging.basicConfig(level=logging.INFO)

    # Here we register the task processor, name the job 'task_type' and assign the function to be called
    queue_service.register_task_processor("send_email", email_service.send_email)

    logging.info("Starting task queue worker...")
    queue_service.process_queue()


if __name__ == "__main__":
    main()
