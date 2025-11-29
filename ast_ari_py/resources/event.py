class EventRepository:
    def __init__(self, transport):
        self.transport = transport

    async def generate_user_event(self, event_name, application, source=None, variables=None):
        """
        Generate a user event.
        
        Args:
            event_name (str): Event name.
            application (str): The name of the application that will receive this event.
            source (list/str): URI(s) for event source (channel:{channelId}, bridge:{bridgeId}, etc).
            variables (dict): The "variables" key in the body object holds custom key/value pairs.
        """
        params = {'application': application}
        if source:
            # source can be a list or single string
            if isinstance(source, list):
                params['source'] = ",".join(source)
            else:
                params['source'] = source
                
        data = {}
        if variables:
            data['variables'] = variables
            
        await self.transport.request('POST', f'/events/user/{event_name}', params=params, data=data)
