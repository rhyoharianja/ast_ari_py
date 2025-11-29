from .base import Resource

class Endpoint(Resource):
    def __init__(self, transport, data):
        super().__init__(transport, data)
        self.technology = data.get('technology')
        self.resource = data.get('resource')
        self.state = data.get('state')
        self.channel_ids = data.get('channel_ids', [])

    async def send_message(self, body, variables=None):
        """
        Mengirim pesan teks ke endpoint (misal: SIP MESSAGE).
        """
        params = {'body': body}
        if variables:
            # variables harus di-encode sebagai JSON string dalam query param untuk beberapa versi ARI,
            # atau body JSON. ARI standar menggunakan body untuk variables.
            # Namun, endpoint sendMessage seringkali menggunakan body text.
            # Referensi API: POST /endpoints/{tech}/{resource}/sendMessage
            pass 
        
        # Implementasi dasar:
        return await self.transport.request(
            'PUT', 
            f'/endpoints/{self.technology}/{self.resource}/sendMessage', 
            params=params,
            data={'variables': variables} if variables else None
        )

class EndpointRepository:
    def __init__(self, transport):
        self.transport = transport

    async def list(self):
        """Mendaftar semua endpoint."""
        data = await self.transport.request('GET', '/endpoints')
        return [Endpoint(self.transport, d) for d in data]

    async def get(self, technology, resource):
        """
        Mengambil detail endpoint.
        Args:
            technology (str): misal 'PJSIP'
            resource (str): misal '1001'
        """
        data = await self.transport.request('GET', f'/endpoints/{technology}/{resource}')
        return Endpoint(self.transport, data)
