import time
import random
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict

class RateLimiter:
    def __init__(self, 
                 base_delay: float = 2.0,
                 max_delay: float = 5.0,
                 jitter_factor: float = 0.5,
                 backoff_factor: float = 2,
                 max_retries: int = 3,
                 min_request_interval: float = 1.0):
        """
        Initialize the rate limiter with configurable parameters.
        
        Args:
            base_delay: Base delay between requests in seconds
            max_delay: Maximum delay between requests in seconds
            jitter_factor: Random jitter factor (0-1) to add to delays
            backoff_factor: Multiplier for exponential backoff
            max_retries: Maximum number of retry attempts
            min_request_interval: Minimum time between requests
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter_factor = jitter_factor
        self.backoff_factor = backoff_factor
        self.max_retries = max_retries
        self.min_request_interval = min_request_interval
        
        self.last_request_time: Optional[datetime] = None
        self.retry_counts: Dict[str, int] = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)

    def add_jitter(self, delay: float) -> float:
        """Add random jitter to the delay."""
        jitter = random.uniform(-self.jitter_factor, self.jitter_factor) * delay
        return max(0, delay + jitter)

    def get_backoff_delay(self, operation_key: str) -> float:
        """Calculate exponential backoff delay based on retry count."""
        retry_count = self.retry_counts.get(operation_key, 0)
        delay = self.base_delay * (self.backoff_factor ** retry_count)
        return min(delay, self.max_delay)

    def wait(self, operation_key: str = "default"):
        """
        Wait for the appropriate amount of time before the next operation.
        
        Args:
            operation_key: Identifier for the operation (used for retry tracking)
        """
        # Ensure minimum interval between requests
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)

        # Calculate delay with backoff if there were retries
        base_delay = self.get_backoff_delay(operation_key)
        
        # Add jitter to make the pattern less predictable
        actual_delay = self.add_jitter(base_delay)
        
        self.logger.debug(f"Waiting for {actual_delay:.2f} seconds before next operation")
        time.sleep(actual_delay)
        
        self.last_request_time = datetime.now()

    def record_success(self, operation_key: str = "default"):
        """Record successful operation and reset retry count."""
        if operation_key in self.retry_counts:
            del self.retry_counts[operation_key]

    def record_failure(self, operation_key: str = "default") -> bool:
        """
        Record operation failure and increment retry count.
        
        Returns:
            bool: True if retry is allowed, False if max retries exceeded
        """
        self.retry_counts[operation_key] = self.retry_counts.get(operation_key, 0) + 1
        
        if self.retry_counts[operation_key] > self.max_retries:
            self.logger.warning(f"Max retries ({self.max_retries}) exceeded for {operation_key}")
            return False
            
        return True

    def reset(self, operation_key: str = "default"):
        """Reset retry count for an operation."""
        if operation_key in self.retry_counts:
            del self.retry_counts[operation_key]