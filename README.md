# Lokal Python

Library for interacting with Lokal Client REST API

```python
from lokal import new_default, TunnelType

lokal = new_default()
tunnel = (lokal.new_tunnel()
    .set_local_address("localhost:8000")
    .set_tunnel_type(TunnelType.HTTP)
    .set_lan_address("myflask-backend.local")
    .set_name("My App")
    .show_startup_banner()
    .create())

print(tunnel.get_lan_address())
```
