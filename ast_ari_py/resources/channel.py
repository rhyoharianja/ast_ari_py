from .base import Resource
from .playback import Playback
from .recording import LiveRecording

class Channel(Resource):
    def __init__(self, transport, data):
        super().__init__(transport, data)
        self.id = data.get('id')
        self.name = data.get('name')
        self.state = data.get('state')
        self.caller = data.get('caller', {})
        self.dialplan = data.get('dialplan', {})

    async def answer(self):
        """Menjawab panggilan masuk (mengubah state menjadi Up)."""
        return await self.transport.request('POST', f'/channels/{self.id}/answer')

    async def hangup(self, reason='normal'):
        """
        Mengakhiri panggilan.
        Args:
            reason (str): Alasan penutupan (normal, busy, congestion).
        """
        params = {'reason': reason}
        return await self.transport.request('DELETE', f'/channels/{self.id}', params=params)

    async def ring(self):
        """Mulai memainkan nada dering (ringing) ke saluran."""
        return await self.transport.request('POST', f'/channels/{self.id}/ring')

    async def stop_ring(self):
        """Berhenti memainkan nada dering."""
        return await self.transport.request('DELETE', f'/channels/{self.id}/ring')

    async def play(self, media_uri, playback_id=None):
        """
        Memainkan media ke saluran.
        Args:
            media_uri (str): URI media (contoh: 'sound:hello-world').
            playback_id (str): ID opsional untuk melacak pemutaran ini.
        Returns:
            Playback: Objek pemutaran untuk kontrol selanjutnya.
        """
        params = {'media': media_uri}
        if playback_id:
            params['playbackId'] = playback_id
        
        # Permintaan pemutaran mengembalikan objek Playback
        data = await self.transport.request('POST', f'/channels/{self.id}/play', params=params)
        return Playback(self.transport, data)

    async def record(self, name, format='wav', max_duration=0, if_exists='fail'):
        """
        Merekam audio dari saluran ini.
        """
        params = {
            'name': name,
            'format': format,
            'maxDurationSeconds': max_duration,
            'ifExists': if_exists
        }
        data = await self.transport.request('POST', f'/channels/{self.id}/record', params=params)
        return LiveRecording(self.transport, data)

    async def snoop(self, app_name, spy='none', whisper='none', snoop_id=None, app_args=None):
        """
        Membuat saluran snoop yang melekat pada saluran ini.
        
        Args:
            app_name (str): Aplikasi Stasis yang akan mengontrol saluran snoop.
            spy (str): Arah penyadapan ('in', 'out', 'both', 'none').
            whisper (str): Arah pembisikan ('in', 'out', 'both', 'none').
        
        Returns:
            Channel: Objek saluran baru yang merepresentasi koneksi snoop.
        """
        endpoint = f'/channels/{self.id}/snoop'
        if snoop_id:
            endpoint += f'/{snoop_id}'
            
        params = {
            'app': app_name,
            'spy': spy,
            'whisper': whisper
        }
        if app_args:
            params['appArgs'] = app_args
            
        data = await self.transport.request('POST', endpoint, params=params)
        return Channel(self.transport, data)

    async def redirect(self, endpoint):
        """
        Mengalihkan (Redirect/Transfer) saluran ke endpoint baru.
        Berguna untuk Call Forwarding atau Blind Transfer.
        
        Args:
            endpoint (str): Endpoint tujuan (misal: 'PJSIP/1001' atau lokasi dialplan).
        """
        params = {'endpoint': endpoint}
        return await self.transport.request('POST', f'/channels/{self.id}/redirect', params=params)


class ChannelRepository:
    def __init__(self, transport):
        self.transport = transport

    async def create(self, endpoint, app, app_args=None, caller_id=None, variables=None):
        """
        Memulai panggilan keluar (Originate).
        Ini adalah metode krusial untuk aplikasi auto-dialer.
        
        Args:
            endpoint (str): Tujuan panggilan (misal: 'PJSIP/1001').
            app (str): Nama aplikasi Stasis yang akan mengontrol saluran ini.
            app_args (str): Argumen yang diteruskan ke Stasis.
            variables (dict): Variabel saluran untuk diset saat pembuatan.
        """
        params = {
            'endpoint': endpoint,
            'app': app,
        }
        if app_args:
            params['appArgs'] = app_args
        if caller_id:
            params['callerId'] = caller_id
        
        body = {}
        if variables:
            body['variables'] = variables

        data = await self.transport.request('POST', '/channels', params=params, data=body)
        return Channel(self.transport, data)
    
    async def get(self, channel_id):
        """Mengambil detail saluran berdasarkan ID."""
        data = await self.transport.request('GET', f'/channels/{channel_id}')
        return Channel(self.transport, data)
    
    async def list(self):
        """Mendaftar semua saluran aktif."""
        data = await self.transport.request('GET', '/channels')
        return [Channel(self.transport, d) for d in data]
