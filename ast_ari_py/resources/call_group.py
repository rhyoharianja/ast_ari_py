from .base import Resource

class CallGroup:
    def __init__(self, name, users=None):
        self.name = name
        self.users = users or []

    def add_member(self, user):
        """Menambahkan user ke grup."""
        if user not in self.users:
            self.users.append(user)

    def remove_member(self, user):
        """Menghapus user dari grup."""
        if user in self.users:
            self.users.remove(user)

    def get_dial_string(self):
        """
        Menghasilkan dial string untuk parallel dialing.
        Contoh: 'PJSIP/1001&PJSIP/1002'
        """
        endpoints = []
        for user in self.users:
            if user.endpoint_tech and user.endpoint_resource:
                endpoints.append(f"{user.endpoint_tech}/{user.endpoint_resource}")
        return "&".join(endpoints)

class CallGroupManager:
    def __init__(self, client):
        self.client = client
        self._groups = {}

    def create_group(self, name, users=None):
        group = CallGroup(name, users)
        self._groups[name] = group
        return group

    def get_group(self, name):
        return self._groups.get(name)

    async def dial_group(self, group_name, app, app_args=None, caller_id=None):
        """
        Melakukan panggilan ke seluruh anggota grup secara paralel.
        """
        group = self.get_group(group_name)
        if not group:
            raise ValueError(f"Group {group_name} not found")

        endpoint_string = group.get_dial_string()
        if not endpoint_string:
            raise ValueError("Group has no valid endpoints")

        # Menggunakan ChannelRepository untuk originate
        return await self.client.channels.create(
            endpoint=endpoint_string,
            app=app,
            app_args=app_args,
            caller_id=caller_id
        )
