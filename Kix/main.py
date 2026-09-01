"""Entry point: `python Kix/main.py` abre o app.

Uso:
    python Kix/main.py
"""

from Kix.core.app import KixApp


def main() -> None:
    KixApp().run()


if __name__ == "__main__":
    main()