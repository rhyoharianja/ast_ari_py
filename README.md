# ast_ari_py

A high-performance, asynchronous Python library for the Asterisk REST Interface (ARI). Built with `asyncio` and `aiohttp`.

## Features
- **Async I/O**: Non-blocking architecture for handling thousands of concurrent calls.
- **Resource Objects**: Pythonic abstractions for Channels, Bridges, Playbacks, and Recordings.
- **User Management**: Logical management of Agents, Supervisors, and Roles.
- **Advanced Call Control**: Call Groups, Trunking, Redirects, Snoop/Whisper.
- **Event Driven**: Simple event loop integration.

## Installation
```bash
pip install -r requirements.txt
python setup.py install
```

## Quick Start

### 1. Configuration
Ensure your Asterisk `ari.conf` is configured and the HTTP server is enabled.

### 2. Basic Application (`examples/simple_stasis.py`)
```python
from ast_ari_py import ARIClient

async def main():
    client = ARIClient("http://localhost:8088/ari", "asterisk", "asterisk")
    await client.connect()
    
    # Register an app handler
    await client.run_app("hello-world", event_handler)
```

## Advanced Usage

### User & Role Management
```python
# Add an agent
client.users.add_user("101", "Agent Smith", "1001", "PJSIP", "1001", role="agent")

# Add a supervisor
client.users.add_user("900", "Boss", "9000", "PJSIP", "9000", role="supervisor")

# Supervisor Whisper (Coaching)
await client.users.whisper_user("900", "1001")
```

### Call Groups (Parallel Dialing)
```python
sales = client.call_groups.create_group("sales")
sales.add_member(agent_smith)
# Dial all members at once
await client.call_groups.dial_group("sales", app="ivr-app")
```

### Trunking (Outbound Calls)
```python
# Register a SIP trunk
client.trunks.add_trunk("provider", "PJSIP", "my_sip_trunk", max_channels=10)

# Dial out
await client.trunks.dial_out("provider", "08123456789", app="outbound-app")
```

### IVR (Interactive Voice Response)
See `examples/ivr_menu.py` for a full example of handling DTMF (keypress) events to build menu systems.

## Database Integration
The library uses in-memory repositories by default. You can easily extend this to use a database. See `examples/custom_repository.py` for an SQLite integration pattern.

## Project Structure
- `ast_ari_py/core`: Transport and Client logic.
- `ast_ari_py/resources`: Domain objects (Channel, User, etc.).
- `ast_ari_py/utils`: Helpers (SMTP, etc.).
- `examples/`: Usage scripts.
