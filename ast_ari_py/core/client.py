from .transport import ARITransport
from ..resources.mailbox import MailboxRepository
from ..resources.sound import SoundRepository
from ..resources.event import EventRepository

class ARIClient:
    def __init__(self, base_url, username, password):
        self.transport = ARITransport(base_url, username, password)
        self.channels = ChannelRepository(self.transport)
        self.bridges = BridgeRepository(self.transport)
        self.endpoints = EndpointRepository(self.transport)
        self.device_states = DeviceStateRepository(self.transport)
        self.users = UserManager(self.transport, self.channels, self.endpoints)
        self.call_groups = CallGroupManager(self.transport, self.users)
        self.trunks = TrunkManager(self.transport, self.channels)
        
        # New Resources for Full Coverage
        self.applications = ApplicationRepository(self.transport)
        self.asterisk = AsteriskRepository(self.transport)
        self.mailboxes = MailboxRepository(self.transport)
        self.sounds = SoundRepository(self.transport)
        self.events = EventRepository(self.transport)

    async def connect(self):
        await self.transport.connect()

    async def close(self):
        await self.transport.close()

    async def run_app(self, app_name, handler):
        """Menjalankan aplikasi dengan menghubungkan WebSocket."""
        await self.transport.connect_websocket(app_name, handler)
