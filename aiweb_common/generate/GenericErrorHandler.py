"""GenericErrorHandler: A reusable error handling utility with retry and correction logic.

This module provides the `GenericErrorHandler` class for managing iterative error correction
workflows. It is designed to be generic and reusable for operations such as UML generation,
validation, or any process requiring retries and user-driven correction.

Example usage:
    def main_operation():
        # ... perform operation ...
        return result

    def error_predicate(result) -> bool:
        # Return True if result indicates failure
        return isinstance(result, Exception)

    def correction_callback(attempt: int, last_result):
        # Prompt user for correction or log the error
        print(f"Attempt {attempt}: Error detected. Please correct input.")
        # ... user correction logic ...

    handler = GenericErrorHandler(
        operation=main_operation,
        error_predicate=error_predicate,
        correction_callback=correction_callback,
        max_retries=5,
    )
    final_result = handler.run()

Raises:
    RuntimeError: If all retries are exhausted and the operation still fails.
"""

from typing import Callable


class GenericErrorHandler:
    """Generic error handler with retry and correction logic.

    Attributes:
        operation (Callable[[], T]): The main operation to execute.
        error_predicate (Callable[[T], bool]): Function to detect if the result is an error.
        correction_callback (Callable[[int, T], None]): Callback to prompt for user correction.
        max_retries (int): Maximum number of retries (default: 5).
    """

    def __init__(
        self,
        operation: Callable[[], object],
        error_predicate: Callable[[object], bool],
        correction_callback: Callable[[int, object], None],
        max_retries: int = 5,
    ) -> None:
        """
        Initialize the GenericErrorHandler.

        Args:
            operation: Callable that performs the main operation.
            error_predicate: Callable that returns True if the result is an error.
            correction_callback: Callable invoked to prompt for correction after failure.
            max_retries: Maximum number of retries (default: 5).
        """
        self.operation = operation
        self.error_predicate = error_predicate
        self.correction_callback = correction_callback
        self.max_retries = max_retries

    def run(self) -> object:
        """
        Execute the operation with retry and correction logic.

        Returns:
            The successful result of the operation.

        Raises:
            RuntimeError: If all retries are exhausted and the operation still fails.
        """
        attempt = 0
        result: object = self.operation()
        while self.error_predicate(result):
            attempt += 1
            if attempt > self.max_retries:
                raise RuntimeError(
                    f"Operation failed after {self.max_retries} retries. Last result: {result}"
                )
            self.correction_callback(attempt, result)
            result = self.operation()
        return result