from .base import Resource

class Trunk:
    def __init__(self, name, endpoint_tech, endpoint_resource, max_channels=None):
        self.name = name
        self.endpoint_tech = endpoint_tech
        self.endpoint_resource = endpoint_resource
        self.max_channels = max_channels
        # Dalam implementasi nyata, kita perlu melacak active_channels secara real-time
        # menggunakan event StasisStart/End yang difilter berdasarkan trunk ini.
        self.active_channels = 0 

    def get_endpoint_string(self):
        return f"{self.endpoint_tech}/{self.endpoint_resource}"

    def __repr__(self):
        return f"<Trunk {self.name} ({self.get_endpoint_string()})>"

class TrunkManager:
    def __init__(self, client):
        self.client = client
        self._trunks = {}

    def add_trunk(self, name, endpoint_tech, endpoint_resource, max_channels=None):
        """Mendaftarkan trunk baru."""
        trunk = Trunk(name, endpoint_tech, endpoint_resource, max_channels)
        self._trunks[name] = trunk
        return trunk

    def get_trunk(self, name):
        return self._trunks.get(name)

    async def dial_out(self, trunk_name, destination_number, app, app_args=None, caller_id=None, timeout=30):
        """
        Melakukan panggilan keluar melalui trunk.
        
        Args:
            trunk_name (str): Nama trunk yang terdaftar.
            destination_number (str): Nomor tujuan (misal: '08123456789').
            app (str): Aplikasi Stasis.
        """
        trunk = self.get_trunk(trunk_name)
        if not trunk:
            raise ValueError(f"Trunk {trunk_name} not found")

        # Cek kapasitas (logic sederhana, perlu sinkronisasi event untuk akurasi)
        if trunk.max_channels and trunk.active_channels >= trunk.max_channels:
            raise RuntimeError(f"Trunk {trunk_name} is at full capacity")

        # Konstruksi endpoint string.
        # Format PJSIP biasanya: PJSIP/nomor@endpoint_trunk
        # Atau jika endpoint adalah trunk itu sendiri: PJSIP/endpoint_trunk/sip:nomor@provider
        # Asumsi sederhana: PJSIP/endpoint_trunk/sip:destination_number
        # ATAU jika menggunakan dialplan context: Local/destination_number@trunk_context
        
        # Pendekatan paling umum dengan ARI murni ke Endpoint PJSIP:
        # PJSIP/destination_number@endpoint_resource
        endpoint = f"{trunk.endpoint_tech}/{destination_number}@{trunk.endpoint_resource}"
        
        return await self.client.channels.create(
            endpoint=endpoint,
            app=app,
            app_args=app_args,
            caller_id=caller_id,
            variables={"TIMEOUT(absolute)": str(timeout)}
        )
