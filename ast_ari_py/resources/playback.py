from .base import Resource

class Playback(Resource):
    def __init__(self, transport, data):
        super().__init__(transport, data)
        self.id = data.get('id')
        self.media_uri = data.get('media_uri')
        self.state = data.get('state')

    async def stop(self):
        """Menghentikan pemutaran."""
        return await self.transport.request('DELETE', f'/playbacks/{self.id}')

    async def control(self, operation):
        """
        Mengontrol pemutaran.
        Args:
            operation (str): 'pause', 'unpause', 'reverse', 'forward'.
        """
        params = {'operation': operation}
        return await self.transport.request('POST', f'/playbacks/{self.id}/control', params=params)
