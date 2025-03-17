import json
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Optional

import redis

from config import Config


class QueueService:
    """Service for managing task queues with Redis backend."""

    def __init__(
        self,
        redis_client: Optional[redis.StrictRedis] = None,
        queue_name: str = "task_queue",
        max_retries: int = 3,
        max_workers: int = 5,
    ):
        self.redis_client = redis_client or redis.StrictRedis.from_url(Config.REDIS_URL)
        self.queue_name = queue_name
        self.max_retries = max_retries
        self.task_processors: Dict[str, Callable[[Dict[str, Any]], bool]] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._shutdown_flag = False

    def register_task_processor(
        self, task_type: str, processor: Callable[[Dict[str, Any]], bool]
    ) -> None:
        """Registers a processor function for a specific task type."""
        self.task_processors[task_type] = processor

    def enqueue_task(
        self, task_type: str, data: Dict[str, Any], retry_count: int = 0
    ) -> None:
        """Enqueues a task with the specified task type and data."""
        task = {
            "task_type": task_type,
            "data": data,
            "retry_count": retry_count,
        }
        try:
            self.redis_client.rpush(self.queue_name, json.dumps(task))
            logging.info(
                "Enqueued task '%s' with retry count %d", task_type, retry_count
            )
        except redis.RedisError as e:
            logging.error("Failed to enqueue task '%s': %s", task_type, e)

    def _retry_or_log_failure(
        self, task_type: str, data: Dict[str, Any], retry_count: int
    ) -> None:
        """Retries the task if below max retries or logs a failure."""
        if retry_count < self.max_retries:
            logging.warning(
                "Retrying task '%s', attempt %d", task_type, retry_count + 1
            )
            self.enqueue_task(task_type, data, retry_count + 1)
        else:
            logging.error("Max retries reached for task '%s'", task_type)

    def process_task(self, task: Dict[str, Any]) -> None:
        """Processes a single task."""
        task_type = task.get("task_type")
        data = task.get("data")
        retry_count = task.get("retry_count", 0)

        # Validate task structure
        if not task_type or data is None:
            logging.error("Invalid task format")
            return

        # Process the task
        processor = self.task_processors.get(task_type)
        if processor:
            logging.info("Processing task '%s'", task_type)
            try:
                success = processor(data)
                if not success:
                    self._retry_or_log_failure(task_type, data, retry_count)
            except Exception as e:
                logging.error("Error processing task '%s': %s", task_type, e)
                self._retry_or_log_failure(task_type, data, retry_count)
            else:
                logging.info("Successfully processed task '%s'", task_type)
        else:
            logging.error("No registered processor for task type '%s'", task_type)

    def process_queue(self) -> None:
        """
        Continuously processes tasks from the queue.

        This method runs in a loop, waiting for tasks to be available in the queue.
        It uses `blpop`, a blocking operation that removes and returns an item from the queue
        when available, preventing unnecessary CPU usage when the queue is empty.
        Retrieved tasks are processed asynchronously using a thread pool executor.

        Logs errors if there are issues with Redis or JSON decoding.
        """
        while not self._shutdown_flag:
            try:
                _, job = self.redis_client.blpop([self.queue_name])
                if job:
                    task = json.loads(job)
                    self.executor.submit(self.process_task, task)
            except redis.RedisError as e:
                logging.error("Redis error during queue processing: %s", e)
            except json.JSONDecodeError:
                logging.error("Failed to decode task from queue")
            except Exception as e:
                logging.error("Unexpected error during queue processing: %s", e)

    def shutdown(self) -> None:
        """Gracefully shuts down the queue worker."""
        logging.info("Shutting down queue worker...")
        self._shutdown_flag = True
        self.executor.shutdown(wait=True)  # Wait for all tasks to complete
        logging.info("Queue worker shutdown complete.")
