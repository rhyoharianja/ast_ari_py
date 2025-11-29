class AsteriskRepository:
    def __init__(self, transport):
        self.transport = transport

    async def get_info(self, only=None):
        """
        Gets Asterisk system information.
        only: Filter information returned (build, system, config, status).
        """
        params = {}
        if only:
            params['only'] = only
        return await self.transport.request('GET', '/asterisk/info', params=params)

    async def get_global_variable(self, variable):
        """Get the value of a global variable."""
        params = {'variable': variable}
        data = await self.transport.request('GET', '/asterisk/variable', params=params)
        return data.get('value')

    async def set_global_variable(self, variable, value):
        """Set the value of a global variable."""
        params = {'variable': variable, 'value': value}
        await self.transport.request('POST', '/asterisk/variable', params=params)

    async def list_modules(self):
        """List Asterisk modules."""
        return await self.transport.request('GET', '/asterisk/modules')

    async def get_module(self, module_name):
        """Get Asterisk module information."""
        return await self.transport.request('GET', f'/asterisk/modules/{module_name}')

    async def load_module(self, module_name):
        """Load an Asterisk module."""
        return await self.transport.request('POST', f'/asterisk/modules/{module_name}')

    async def unload_module(self, module_name):
        """Unload an Asterisk module."""
        return await self.transport.request('DELETE', f'/asterisk/modules/{module_name}')

    async def reload_module(self, module_name):
        """Reload an Asterisk module."""
        return await self.transport.request('PUT', f'/asterisk/modules/{module_name}')

    async def list_log_channels(self):
        """Gets Asterisk log channels."""
        return await self.transport.request('GET', '/asterisk/logging')

    async def add_log_channel(self, log_channel_name, configuration):
        """Adds a log channel."""
        params = {'configuration': configuration}
        await self.transport.request('POST', f'/asterisk/logging/{log_channel_name}', params=params)

    async def delete_log_channel(self, log_channel_name):
        """Deletes a log channel."""
        await self.transport.request('DELETE', f'/asterisk/logging/{log_channel_name}')

    async def rotate_log(self, log_channel_name):
        """Rotates a log channel."""
        await self.transport.request('PUT', f'/asterisk/logging/{log_channel_name}/rotate')
