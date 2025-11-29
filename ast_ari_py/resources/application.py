from .base import BaseResource

class Application(BaseResource):
    def __init__(self, transport, data):
        super().__init__(transport, data)

    async def subscribe(self, event_source):
        """
        Subscribe an application to a event source.
        event_source: URI for event source (channel:{channelId}, bridge:{bridgeId}, endpoint:{tech}/{resource}, deviceState:{deviceName})
        """
        endpoint = f'/applications/{self.name}/subscription'
        params = {'eventSource': event_source}
        return await self.transport.request('POST', endpoint, params=params)

    async def unsubscribe(self, event_source):
        """
        Unsubscribe an application from an event source.
        """
        endpoint = f'/applications/{self.name}/subscription'
        params = {'eventSource': event_source}
        return await self.transport.request('DELETE', endpoint, params=params)

class ApplicationRepository:
    def __init__(self, transport):
        self.transport = transport

    async def list(self):
        """List all applications."""
        data = await self.transport.request('GET', '/applications')
        return [Application(self.transport, app) for app in data]

    async def get(self, application_name):
        """Get details of an application."""
        data = await self.transport.request('GET', f'/applications/{application_name}')
        return Application(self.transport, data)
