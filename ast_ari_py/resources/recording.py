from .base import Resource

class LiveRecording(Resource):
    def __init__(self, transport, data):
        super().__init__(transport, data)
        self.name = data.get('name')
        self.target_uri = data.get('target_uri')

    async def stop(self):
        """Menghentikan perekaman dan menyimpannya ke disk."""
        return await self.transport.request('POST', f'/recordings/live/{self.name}/stop')

    async def pause(self):
        """Menjeda perekaman."""
        return await self.transport.request('POST', f'/recordings/live/{self.name}/pause')

    async def unpause(self):
        """Melanjutkan perekaman."""
        return await self.transport.request('DELETE', f'/recordings/live/{self.name}/pause')

    async def mute(self):
        """Membisukan rekaman (merekam keheningan)."""
        return await self.transport.request('POST', f'/recordings/live/{self.name}/mute')
