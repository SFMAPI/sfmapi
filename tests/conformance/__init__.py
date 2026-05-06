"""sfmapi conformance suite.

Runnable two ways:

  1. As a normal pytest module against the in-process reference impl.
  2. As a standalone CLI against any HTTP base URL:
        python -m tests.conformance --base-url http://other-impl --api-key sfm_xxx
"""
