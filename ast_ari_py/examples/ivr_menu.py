import asyncio
from ast_ari_py import ARIClient

# Konfigurasi
ARI_URL = "http://localhost:8088/ari"
ARI_USER = "asterisk"
ARI_PASS = "asterisk"
APP_NAME = "ivr-demo"

async def on_dtmf(event, channel, client):
    """Menangani input tombol (DTMF) dari pengguna."""
    digit = event['digit']
    print(f"Channel {channel.id} pressed: {digit}")

    if digit == '1':
        await channel.play("sound:sales-queue")
        # Logika transfer ke antrian sales
        # await client.call_groups.dial_group("sales", ...)
    elif digit == '2':
        await channel.play("sound:support-queue")
        # Logika transfer ke support
    elif digit == '*':
        await channel.play("sound:main-menu")
    else:
        await channel.play("sound:invalid-option")

async def run_ivr(channel, client):
    print(f"Starting IVR for {channel.id}")
    
    await channel.answer()
    await channel.play("sound:welcome-to-service")
    await asyncio.sleep(1)
    await channel.play("sound:press-1-for-sales")
    await channel.play("sound:press-2-for-support")

    # Di ARI, kita tidak 'menunggu' input dengan blocking function.
    # Kita mendengarkan event ChannelDtmfReceived.
    # Logic ada di event_handler.

async def event_handler(event, client):
    event_type = event.get('type')
    
    if event_type == 'StasisStart':
        channel_id = event['channel']['id']
        channel = await client.channels.get(channel_id)
        await run_ivr(channel, client)

    elif event_type == 'ChannelDtmfReceived':
        channel_id = event['channel']['id']
        channel = await client.channels.get(channel_id)
        await on_dtmf(event, channel, client)

    elif event_type == 'StasisEnd':
        print(f"Channel {event['channel']['id']} left IVR.")

async def main():
    client = ARIClient(ARI_URL, ARI_USER, ARI_PASS)
    await client.connect()
    print(f"IVR App '{APP_NAME}' running...")
    await client.run_app(APP_NAME, lambda e: event_handler(e, client))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
