"""Provider registry and base types.

The registry is a class-level store keyed by ``(protocol_type, provider_id)``.
Providers register themselves at import time so that the registry is populated
as soon as the package is loaded.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypeVar

T = TypeVar("T")


@dataclass
class ProviderInfo:
    """Metadata about a registered provider."""

    provider_id: str
    display_name: str
    protocol_type: type
    requires_gpu: bool = False
    requires_software: list[str] = field(default_factory=list)
    description: str = ""


class ProviderRegistry:
    """Global registry of available provider implementations.

    Providers register with ``ProviderRegistry.register(protocol, instance)``.
    Callers resolve providers with ``get`` (by id) or ``auto_select`` (best
    match given detected hardware).
    """

    _providers: dict[tuple[type, str], Any] = {}
    _info: dict[tuple[type, str], ProviderInfo] = {}

    # -- Registration -------------------------------------------------------

    @classmethod
    def register(
        cls,
        protocol_type: type,
        provider: Any,
        info: ProviderInfo | None = None,
    ) -> None:
        """Register a provider instance under its protocol type."""
        pid = getattr(provider, "provider_id", None)
        if pid is None:
            raise ValueError("Provider must have a 'provider_id' attribute")
        key = (protocol_type, pid)
        cls._providers[key] = provider
        if info:
            cls._info[key] = info

    # -- Lookup -------------------------------------------------------------

    @classmethod
    def get(cls, protocol_type: type, provider_id: str) -> Any:
        """Return a specific provider or raise ``KeyError``."""
        return cls._providers[(protocol_type, provider_id)]

    @classmethod
    def get_default(cls, protocol_type: type) -> Any:
        """Return the first registered provider for *protocol_type*."""
        for (pt, _pid), prov in cls._providers.items():
            if pt is protocol_type:
                return prov
        raise KeyError(f"No providers registered for {protocol_type.__name__}")

    @classmethod
    def list_available(cls, protocol_type: type) -> list[str]:
        """List provider IDs registered under *protocol_type*."""
        return [pid for (pt, pid) in cls._providers if pt is protocol_type]

    @classmethod
    def list_info(cls, protocol_type: type) -> list[ProviderInfo]:
        """Return ``ProviderInfo`` objects for every provider of this type."""
        return [
            info
            for (pt, _pid), info in cls._info.items()
            if pt is protocol_type
        ]

    @classmethod
    def auto_select(cls, protocol_type: type, hardware: Any = None) -> Any:
        """Pick the best available provider for *protocol_type*.

        If *hardware* is supplied (a ``HardwareProfile``), GPU-capable
        providers are preferred when a CUDA/ROCm GPU is detected.
        """
        candidates = [
            (pid, prov)
            for (pt, pid), prov in cls._providers.items()
            if pt is protocol_type
        ]
        if not candidates:
            raise KeyError(f"No providers registered for {protocol_type.__name__}")

        # Prefer GPU-enabled when GPU detected
        if hardware and getattr(hardware, "cuda_available", False):
            for pid, prov in candidates:
                if getattr(prov, "requires_gpu", False):
                    return prov

        # Prefer non-mock, non-gpu providers
        for pid, prov in candidates:
            if "mock" not in pid:
                return prov

        # Fallback to first candidate
        return candidates[0][1]

    @classmethod
    def resolve_from_config(
        cls,
        protocol_type: type,
        providers_config: dict[str, Any],
        category: str,
        hardware: Any = None,
    ) -> Any:
        """Resolve a provider from a project's ``providers:`` YAML config.

        Args:
            protocol_type: The Protocol class (e.g., CFDProvider).
            providers_config: The ``providers`` dict from ``aeroforge.yaml``.
            category: Config key (e.g., ``"cfd"``, ``"fea"``).
            hardware: Optional HardwareProfile for auto-selection.

        Returns:
            The resolved provider instance.
        """
        cat_cfg = providers_config.get(category, {})
        selected_id = cat_cfg.get("selected")

        if selected_id and selected_id != "auto":
            try:
                return cls.get(protocol_type, selected_id)
            except KeyError:
                pass  # Fall through to auto-select

        return cls.auto_select(protocol_type, hardware)

    @classmethod
    def clear(cls) -> None:
        """Remove all registrations (for testing)."""
        cls._providers.clear()
        cls._info.clear()
