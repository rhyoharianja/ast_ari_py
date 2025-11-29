from .base import BaseResource

class Mailbox(BaseResource):
    def __init__(self, transport, data):
        super().__init__(transport, data)

    async def update(self, old_messages, new_messages):
        """Change the state of a mailbox."""
        params = {'oldMessages': old_messages, 'newMessages': new_messages}
        await self.transport.request('PUT', f'/mailboxes/{self.name}', params=params)

    async def delete(self):
        """Destroy a mailbox."""
        await self.transport.request('DELETE', f'/mailboxes/{self.name}')

class MailboxRepository:
    def __init__(self, transport):
        self.transport = transport

    async def list(self):
        """List all mailboxes."""
        data = await self.transport.request('GET', '/mailboxes')
        return [Mailbox(self.transport, mb) for mb in data]

    async def get(self, mailbox_name):
        """Retrieve the current state of a mailbox."""
        data = await self.transport.request('GET', f'/mailboxes/{mailbox_name}')
        return Mailbox(self.transport, data)

    async def update(self, mailbox_name, old_messages, new_messages):
        """Change the state of a mailbox."""
        params = {'oldMessages': old_messages, 'newMessages': new_messages}
        await self.transport.request('PUT', f'/mailboxes/{mailbox_name}', params=params)

    async def delete(self, mailbox_name):
        """Destroy a mailbox."""
        await self.transport.request('DELETE', f'/mailboxes/{mailbox_name}')
