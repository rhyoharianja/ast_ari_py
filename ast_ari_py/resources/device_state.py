class DeviceStateRepository:
    def __init__(self, transport):
        self.transport = transport

    async def update(self, device_name, state):
        """
        Memperbarui status perangkat kustom.
        
        Args:
            device_name (str): Nama perangkat, biasanya 'Custom:NamaStatus'.
            state (str): Salah satu dari: 
                         NOT_INUSE, INUSE, BUSY, INVALID, UNAVAILABLE, 
                         RINGING, RINGINUSE, ONHOLD.
        """
        # ARI mengharapkan objek JSON dengan kunci 'deviceState' atau 'state'
        # tergantung versi. Implementasi modern menggunakan body JSON.
        data = {'deviceState': state}
        return await self.transport.request('PUT', f'/deviceStates/{device_name}', data=data)
    
    async def get(self, device_name):
        """Mengambil status saat ini."""
        return await self.transport.request('GET', f'/deviceStates/{device_name}')
    
    async def delete(self, device_name):
        """Menghapus/menghancurkan status perangkat kustom."""
        return await self.transport.request('DELETE', f'/deviceStates/{device_name}')
