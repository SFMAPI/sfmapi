# `app.adapters`

The boundary layer between sfmapi and any concrete SfM engine.
sfmapi ships **no real backend**. It provides layered backend
Protocols, the registry that wires packages in, and a no-op stub for
tests / ephemeral demos.

Action-only packages can satisfy the minimal ``Backend`` Protocol and
expose native tools through backend actions. Complete engines can
satisfy ``SfmBackend`` and implement the full portable feature, match,
mapping, refinement, and export surface.

```{eval-rst}
.. automodule:: app.adapters.backend
   :members:
   :no-index:

.. automodule:: app.adapters.registry
   :members:
   :no-index:

.. automodule:: app.adapters.progress
   :members:
   :no-index:

.. automodule:: app.adapters.backend_actions
   :members:
   :no-index:

.. automodule:: app.adapters.backend_config
   :members:
   :no-index:

.. automodule:: app.adapters.backend_contract
   :members:
   :no-index:

.. automodule:: app.adapters.stub_backend
   :members:
   :no-index:
```
