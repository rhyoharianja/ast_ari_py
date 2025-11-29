from .base import Resource

class UserRole:
    AGENT = 'agent'
    SUPERVISOR = 'supervisor'
    ADMIN = 'admin'

class User:
    def __init__(self, id, name, extension, endpoint_tech, endpoint_resource, role=UserRole.AGENT):
        self.id = id
        self.name = name
        self.extension = extension
        self.endpoint_tech = endpoint_tech
        self.endpoint_resource = endpoint_resource
        self.role = role
        self.current_channel = None # Track active channel ID

    def can_snoop(self):
        return self.role in [UserRole.SUPERVISOR, UserRole.ADMIN]

    def __repr__(self):
        return f"<User {self.name} ({self.role}) Ext:{self.extension}>"

class UserManager:
    def __init__(self, client):
        self.client = client
        self._users = {} # In-memory storage. In prod, use DB.
        self._extension_map = {}

    def add_user(self, id, name, extension, endpoint_tech, endpoint_resource, role=UserRole.AGENT):
        """Mendaftarkan user baru ke sistem logika aplikasi."""
        user = User(id, name, extension, endpoint_tech, endpoint_resource, role)
        self._users[id] = user
        self._extension_map[extension] = user
        return user

    def get_user_by_extension(self, extension):
        return self._extension_map.get(extension)

    def get_user_by_id(self, id):
        return self._users.get(id)

    async def snoop_user(self, supervisor_id, target_extension, spy='both', whisper='none'):
        """
        Helper untuk supervisor melakukan snoop ke user lain.
        """
        supervisor = self.get_user_by_id(supervisor_id)
        target = self.get_user_by_extension(target_extension)

        if not supervisor:
            raise ValueError("Supervisor not found")
        if not target:
            raise ValueError("Target user not found")

        if not supervisor.can_snoop():
            raise PermissionError(f"User {supervisor.name} does not have supervisor privileges.")

        if not target.current_channel:
            raise ValueError(f"Target {target.name} is not currently in a call.")

        # Dapatkan objek channel target
        target_channel = await self.client.channels.get(target.current_channel)
        
        # Lakukan snoop
        # Kita buat channel snoop yang terhubung ke aplikasi supervisor?
        # Atau sekadar snoop biasa.
        # Biasanya snoop akan membuat channel baru. Kita perlu menghubungkan channel baru ini ke supervisor.
        # Namun, ARI snoop() membuat channel yang 'attached' ke target.
        # Kita perlu mem-bridge channel snoop ini ke supervisor, atau mengarahkannya ke endpoint supervisor.
        
        # Cara 1: Originate ke supervisor, lalu bridge dengan snoop channel?
        # Cara 2: Snoop dengan app, lalu di StasisStart snoop channel, kita bridge ke supervisor.
        
        # Mari gunakan pendekatan sederhana: Return snoop channel object, biarkan app logic menangani bridging.
        return await target_channel.snoop(app_name='snoop_app', spy=spy, whisper=whisper)

    async def whisper_user(self, supervisor_id, target_extension):
        """
        Supervisor membisiki user (Whisper).
        Hanya supervisor yang didengar oleh target, target tidak didengar supervisor (kecuali spy='both').
        """
        # whisper='out' berarti menyuntikkan audio ke arah keluar target (ke telinga target).
        # spy='none' berarti supervisor tidak mendengar audio target.
        # Biasanya supervisor ingin mendengar juga (coaching), jadi spy='both', whisper='out'.
        return await self.snoop_user(supervisor_id, target_extension, spy='both', whisper='out')
