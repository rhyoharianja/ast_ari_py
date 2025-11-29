from .base import BaseResource

class Sound(BaseResource):
    def __init__(self, transport, data):
        super().__init__(transport, data)

class SoundRepository:
    def __init__(self, transport):
        self.transport = transport

    async def list(self, lang=None, format=None):
        """List all sounds."""
        params = {}
        if lang:
            params['lang'] = lang
        if format:
            params['format'] = format
        data = await self.transport.request('GET', '/sounds', params=params)
        return [Sound(self.transport, s) for s in data]

    async def get(self, sound_id):
        """Get a sound's details."""
        data = await self.transport.request('GET', f'/sounds/{sound_id}')
        return Sound(self.transport, data)
