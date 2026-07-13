#!/usr/bin/env python
"""Ponto de entrada de gestão do backend Django do VentureOps AI."""
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:  # pragma: no cover - ambiente sem Django
        raise ImportError(
            "Django não está instalado ou o ambiente virtual não está activo. "
            "Consulte backend/README.md."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
