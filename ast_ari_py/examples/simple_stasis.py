import asyncio
from ast_ari_py.core.client import ARIClient

# Konfigurasi
ARI_URL = "http://localhost:8088/ari"
ARI_USER = "asterisk"
ARI_PASS = "asterisk"
APP_NAME = "hello-world"

client = None

async def on_stasis_start(event, client):
    channel_id = event['channel']['id']
    print(f"Saluran {channel_id} memasuki Stasis.")
    
    # 1. Dapatkan objek saluran
    channel = await client.channels.get(channel_id)
    
    # 2. Jawab panggilan
    await channel.answer()
    print("Panggilan dijawab.")
    
    # 3. Mainkan file suara (pastikan file 'demo-congrats' ada di Asterisk)
    await channel.play("sound:demo-congrats")
    
    # 4. Rekam pesan selama maksimal 10 detik
    print("Mulai merekam...")
    recording = await channel.record(name=f"rec_{channel_id}", max_duration=10, if_exists='overwrite')
    
    # Kita tidak perlu menunggu rekaman selesai di sini dengan sleep,
    # karena kita akan menangkap event RecordingFinished nanti.

async def event_handler(event):
    # Dispatcher sederhana berdasarkan tipe event
    event_type = event.get('type')
    
    if event_type == 'StasisStart':
        await on_stasis_start(event, client)
        
    elif event_type == 'RecordingFinished':
        rec_name = event['recording']['name']
        print(f"Rekaman selesai: {rec_name}. Durasi: {event['recording']['duration']} detik.")
        # Di sini kita bisa memanggil fungsi pengirim email
        
    elif event_type == 'StasisEnd':
        print(f"Saluran {event['channel']['id']} meninggalkan aplikasi.")

async def main():
    global client
    client = ARIClient(ARI_URL, ARI_USER, ARI_PASS)
    await client.connect()
    
    try:
        print(f"Menghubungkan ke aplikasi '{APP_NAME}'...")
        await client.run_app(APP_NAME, event_handler)
    except asyncio.CancelledError:
        await client.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Aplikasi dihentikan.")
