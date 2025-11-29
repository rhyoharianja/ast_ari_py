from .transport import ARITransport
from ..resources.channel import ChannelRepository
from ..resources.bridge import BridgeRepository
from ..resources.device_state import DeviceStateRepository
from ..resources.endpoint import EndpointRepository
from ..resources.user import UserManager
from ..resources.call_group import CallGroupManager
from ..resources.trunk import TrunkManager

class ARIClient:
    def __init__(self, base_url, username, password):
        self.transport = ARITransport(base_url, username, password)
        self.channels = ChannelRepository(self.transport)
        self.bridges = BridgeRepository(self.transport)
        self.device_states = DeviceStateRepository(self.transport)
        self.endpoints = EndpointRepository(self.transport)
        self.users = UserManager(self)
        self.call_groups = CallGroupManager(self)
        self.trunks = TrunkManager(self)

    async def connect(self):
        await self.transport.connect()

    async def close(self):
        await self.transport.close()

    async def run_app(self, app_name, handler):
        """Menjalankan aplikasi dengan menghubungkan WebSocket."""
        await self.transport.connect_websocket(app_name, handler)
