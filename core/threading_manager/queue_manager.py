"""
Queue Manager for Thread Communication

This module manages the queue-based communication between the main UI thread
and background processing threads.
"""

import queue
import threading
from typing import Any, Callable, Dict, List, Optional
from enum import Enum


class MessageType(Enum):
    """Enumeration for message types"""
    PROGRESS = "progress"
    COMPLETE = "complete"
    ERROR = "error"
    STATUS = "status"
    RESULT = "result"


class QueueMessage:
    """Data class for queue messages"""
    
    def __init__(self, msg_type: MessageType, data: Any = None, tile_index: Optional[int] = None):
        self.msg_type = msg_type
        self.data = data
        self.tile_index = tile_index
        self.timestamp = threading.current_thread().ident


class QueueManager:
    """
    Manages queue-based communication between threads.
    
    This class provides a thread-safe way to send messages from background
    threads to the main UI thread for updates and status changes.
    """
    
    def __init__(self):
        """Initialize the queue manager"""
        self._queue = queue.Queue()
        self._callbacks: Dict[MessageType, List[Callable]] = {
            msg_type: [] for msg_type in MessageType
        }
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
    
    def start_monitoring(self):
        """Start the queue monitoring thread"""
        if self._running:
            return
        
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_queue,
            daemon=True,
            name="QueueMonitor"
        )
        self._monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the queue monitoring thread"""
        self._running = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)
    
    def send_message(self, msg_type: MessageType, data: Any = None, tile_index: Optional[int] = None):
        """
        Send a message to the queue.
        
        Args:
            msg_type: Type of message
            data: Message data
            tile_index: Optional tile index for tile-specific messages
        """
        message = QueueMessage(msg_type, data, tile_index)
        try:
            self._queue.put_nowait(message)
        except queue.Full:
            # If queue is full, try to clear old messages
            try:
                while not self._queue.empty():
                    self._queue.get_nowait()
                self._queue.put_nowait(message)
            except queue.Full:
                print(f"Warning: Could not send {msg_type.value} message - queue full")
    
    def send_progress(self, current: int, total: int, tile_index: Optional[int] = None):
        """
        Send a progress update message.
        
        Args:
            current: Current progress value
            total: Total progress value
            tile_index: Optional tile index
        """
        progress_data = {
            'current': current,
            'total': total,
            'percentage': (current / total * 100) if total > 0 else 0
        }
        self.send_message(MessageType.PROGRESS, progress_data, tile_index)
    
    def send_complete(self, data: Any = None):
        """
        Send a completion message.
        
        Args:
            data: Completion data
        """
        self.send_message(MessageType.COMPLETE, data)
    
    def send_error(self, error_message: str, tile_index: Optional[int] = None):
        """
        Send an error message.
        
        Args:
            error_message: Error description
            tile_index: Optional tile index where error occurred
        """
        self.send_message(MessageType.ERROR, error_message, tile_index)
    
    def send_status(self, status_message: str):
        """
        Send a status message.
        
        Args:
            status_message: Status description
        """
        self.send_message(MessageType.STATUS, status_message)
    
    def send_result(self, result_data: Any, tile_index: Optional[int] = None):
        """
        Send a result message.
        
        Args:
            result_data: Result data
            tile_index: Optional tile index
        """
        self.send_message(MessageType.RESULT, result_data, tile_index)
    
    def register_callback(self, msg_type: MessageType, callback: Callable):
        """
        Register a callback for a specific message type.
        
        Args:
            msg_type: Message type to listen for
            callback: Function to call when message is received
        """
        if msg_type not in self._callbacks:
            self._callbacks[msg_type] = []
        self._callbacks[msg_type].append(callback)
    
    def unregister_callback(self, msg_type: MessageType, callback: Callable):
        """
        Unregister a callback for a specific message type.
        
        Args:
            msg_type: Message type
            callback: Function to remove
        """
        if msg_type in self._callbacks and callback in self._callbacks[msg_type]:
            self._callbacks[msg_type].remove(callback)
    
    def _monitor_queue(self):
        """Monitor the queue for messages and dispatch to callbacks"""
        while self._running:
            try:
                # Wait for message with timeout to allow checking running flag
                message = self._queue.get(timeout=0.1)
                self._dispatch_message(message)
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in queue monitor: {e}")
    
    def _dispatch_message(self, message: QueueMessage):
        """
        Dispatch a message to registered callbacks.
        
        Args:
            message: Message to dispatch
        """
        if message.msg_type in self._callbacks:
            for callback in self._callbacks[message.msg_type]:
                try:
                    callback(message)
                except Exception as e:
                    print(f"Error in message callback: {e}")
    
    def get_queue_size(self) -> int:
        """Get the current queue size"""
        return self._queue.qsize()
    
    def is_empty(self) -> bool:
        """Check if the queue is empty"""
        return self._queue.empty()
    
    def clear_queue(self):
        """Clear all messages from the queue"""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except queue.Empty:
                break
