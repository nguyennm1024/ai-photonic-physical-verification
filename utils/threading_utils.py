"""
Threading Utilities
===================

Thread-safe utilities for background processing and UI updates.
"""

from queue import Queue, Empty
from typing import Callable, Tuple, Any


class ThreadSafeQueue:
    """
    Thread-safe queue wrapper for passing messages between threads.
    Typically used for background workers to send updates to UI thread.
    """
    
    def __init__(self):
        """Initialize the queue"""
        self.queue = Queue()
    
    def put(self, msg_type: str, *args):
        """
        Put a message in the queue.
        
        Args:
            msg_type: Type of message ('progress', 'complete', 'error', etc.)
            *args: Additional arguments for the message
        """
        self.queue.put((msg_type, *args))
    
    def get_nowait(self) -> Tuple[str, ...]:
        """
        Get a message from the queue without blocking.
        
        Returns:
            (msg_type, *args) tuple
            
        Raises:
            Empty: If queue is empty
        """
        return self.queue.get_nowait()
    
    def process_all(self, callback: Callable[[str, Tuple[Any, ...]], None]):
        """
        Process all messages currently in the queue.
        
        Args:
            callback: Function to call with (msg_type, args) for each message
        """
        while True:
            try:
                msg = self.queue.get_nowait()
                msg_type = msg[0]
                args = msg[1:] if len(msg) > 1 else ()
                callback(msg_type, args)
            except Empty:
                break
    
    def clear(self):
        """Clear all messages from the queue"""
        while True:
            try:
                self.queue.get_nowait()
            except Empty:
                break
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return self.queue.empty()

