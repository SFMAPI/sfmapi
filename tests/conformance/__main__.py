"""Allow `python -m tests.conformance ...`."""

from tests.conformance.runner import main

if __name__ == "__main__":
    import sys

    sys.exit(main())
