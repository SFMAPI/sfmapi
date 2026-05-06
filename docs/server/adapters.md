# `app.adapters`

The **only** layer that imports heavy ML / native deps. Web process
must not pull these in; lazy import is enforced by tests.

```{eval-rst}
.. automodule:: app.adapters.colmap_adapter
   :members:
   :no-index:

.. automodule:: app.adapters.sam_adapter
   :members:
   :no-index:
```
