from .base import Resource

class Bridge(Resource):
    def __init__(self, transport, data):
        super().__init__(transport, data)
        self.id = data.get('id')
        self.technology = data.get('technology')
        self.bridge_type = data.get('bridge_type')
        self.channels = data.get('channels', [])

    async def add_channel(self, channel_id, role=None, mute=False):
        """
        Menambahkan saluran ke jembatan.
        
        Args:
            role (str): 'participant' or 'announcer'. Krusial untuk Holding Bridge.
            mute (bool): Jika True, audio saluran tidak akan masuk ke jembatan.
        """
        params = {'channel': channel_id}
        if role:
            params['role'] = role
        if mute:
            params['mute'] = 'true'
            
        return await self.transport.request('POST', f'/bridges/{self.id}/addChannel', params=params)

    async def remove_channel(self, channel_id):
        """Menghapus saluran dari jembatan."""
        params = {'channel': channel_id}
        return await self.transport.request('POST', f'/bridges/{self.id}/removeChannel', params=params)

    async def start_moh(self, moh_class=None):
        """
        Memulai Music on Hold di jembatan.
        Hanya satu sumber MOH yang bisa aktif sekaligus.
        """
        params = {}
        if moh_class:
            params['mohClass'] = moh_class
        return await self.transport.request('POST', f'/bridges/{self.id}/moh', params=params)

    async def stop_moh(self):
        """Menghentikan MOH."""
        return await self.transport.request('DELETE', f'/bridges/{self.id}/moh')

    async def destroy(self):
        """Menghancurkan jembatan dan melepaskan semua saluran di dalamnya."""
        return await self.transport.request('DELETE', f'/bridges/{self.id}')

class BridgeRepository:
    def __init__(self, transport):
        self.transport = transport

    async def create(self, type='mixing', bridge_id=None, name=None):
        """
        Membuat jembatan baru.
        Args:
            type (str): 'mixing' atau 'holding'.
            bridge_id (str): ID opsional.
            name (str): Nama opsional.
        """
        params = {'type': type}
        if bridge_id:
            params['bridgeId'] = bridge_id
        if name:
            params['name'] = name
            
        data = await self.transport.request('POST', '/bridges', params=params)
        return Bridge(self.transport, data)

    async def get(self, bridge_id):
        """Mengambil detail jembatan."""
        data = await self.transport.request('GET', f'/bridges/{bridge_id}')
        return Bridge(self.transport, data)

    async def list(self):
        """Mendaftar semua jembatan aktif."""
        data = await self.transport.request('GET', '/bridges')
        return [Bridge(self.transport, d) for d in data]
