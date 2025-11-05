"""
A simple factory registry for creating objects by key.

Style aligned with aiweb_common: module docstring, typing, and concise docstrings.
"""
from __future__ import annotations
from typing import Any, Callable, Dict

class ObjectFactory:
    """
    Register builder callables under keys and create objects via those builders.

    Example:
        factory = ObjectFactory()
        factory.register_builder("svc", lambda **kwargs: Service(**kwargs))
        svc = factory.create("svc", config=config)
    """

    def __init__(self) -> None:
        self._builders: Dict[str, Callable[..., Any]] = {}

    def register_builder(self, key: str, builder: Callable[..., Any]) -> None:
        """
        Register a builder callable under the provided key.

        Args:
            key: Unique string identifier for the builder.
            builder: Callable that returns an instance when called with kwargs.
        """
        self._builders[key] = builder

    def create(self, key: str, **kwargs) -> Any:
        """
        Create an object using the builder registered for `key`.

        Args:
            key: The builder key.
            **kwargs: Forwarded to the builder callable.

        Returns:
            The object returned by the builder.

        Raises:
            ValueError: If no builder is registered for the key.
        """
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(f"No builder registered for key: {key}")
        return builder(**kwargs)
