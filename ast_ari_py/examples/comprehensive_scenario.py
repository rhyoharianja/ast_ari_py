import asyncio
import logging
from ast_ari_py import ARIClient

# Konfigurasi Log
logging.basicConfig(level=logging.INFO)

# Konfigurasi ARI
ARI_URL = "http://localhost:8088/ari"
ARI_USER = "asterisk"
ARI_PASS = "asterisk"
APP_NAME = "demo-app"

async def setup_resources(client):
    """
    1. Contoh Penggunaan: Membuat Agent, Group, Supervisor, Trunk
    """
    print("\n--- 1. SETUP RESOURCES ---")
    
    # Mendaftarkan Agent
    agent1 = client.users.add_user("101", "Agent Smith", "1001", "PJSIP", "1001", role="agent")
    agent2 = client.users.add_user("102", "Agent Doe", "1002", "PJSIP", "1002", role="agent")
    print(f"Registered Agents: {agent1.name}, {agent2.name}")

    # Mendaftarkan Supervisor
    supervisor = client.users.add_user("900", "Supervisor Boss", "9000", "PJSIP", "9000", role="supervisor")
    print(f"Registered Supervisor: {supervisor.name}")

    # Membuat Call Group (Sales)
    sales_group = client.call_groups.create_group("sales")
    sales_group.add_member(agent1)
    sales_group.add_member(agent2)
    print(f"Created Group 'sales' with members: {[u.name for u in sales_group.users]}")

    # Mendaftarkan Trunk
    trunk = client.trunks.add_trunk("sip_provider", "PJSIP", "my_provider", max_channels=10)
    print(f"Registered Trunk: {trunk.name}")

async def handle_inbound_call(channel, client):
    """
    3. Contoh: Ringing Inbound dan Mengangkat Inbound Call
    """
    print(f"\n--- INBOUND CALL: {channel.id} ---")
    
    # Ringing
    print(">> Ringing channel...")
    await channel.ring()
    await asyncio.sleep(2) # Simulasi dering 2 detik
    
    # Answering
    print(">> Answering call...")
    await channel.answer()
    await channel.stop_ring()
    
    # Play welcome message
    await channel.play("sound:hello-world")
    await asyncio.sleep(1)

    """
    4. Contoh: Redirect Call atau Call Forwarding ke Agent Lain
    """
    print("\n--- 4. REDIRECT / FORWARDING ---")
    target_extension = "1001"
    print(f">> Redirecting caller to extension {target_extension}...")
    
    # Metode 1: Native Redirect (Blind Transfer)
    # Ini akan memindahkan channel keluar dari Stasis ke endpoint tujuan
    try:
        await channel.redirect(f"PJSIP/{target_extension}")
        print(">> Redirect command sent.")
    except Exception as e:
        print(f"Redirect failed: {e}")

async def make_outbound_call(client):
    """
    2. Contoh: Melakukan Outbound Call via Trunk
    """
    print("\n--- 2. OUTBOUND CALL EXAMPLE ---")
    try:
        # Panggil nomor luar via trunk 'sip_provider'
        dest = "08123456789"
        print(f">> Dialing {dest} via trunk...")
        
        # Ini akan membuat channel baru dan memasukkannya ke aplikasi Stasis kita
        channel = await client.trunks.dial_out(
            trunk_name="sip_provider", 
            destination_number=dest, 
            app=APP_NAME
        )
        print(f">> Outbound call initiated. Channel ID: {channel.id}")
        return channel
    except Exception as e:
        print(f">> Outbound call failed: {e}")

async def event_handler(event, client):
    if event['type'] == 'StasisStart':
        channel_id = event['channel']['id']
        args = event.get('args', [])
        
        channel = await client.channels.get(channel_id)
        
        print(f"StasisStart: Channel {channel_id} entered app.")
        
        # Logika sederhana untuk membedakan inbound vs outbound yang kita buat sendiri
        # Biasanya outbound call yang kita originate akan kita beri argumen atau variabel khusus.
        # Di sini kita anggap jika tidak ada args, itu inbound call dari luar.
        if not args:
            await handle_inbound_call(channel, client)
        else:
            print(">> Outbound channel ready.")

    elif event['type'] == 'StasisEnd':
        print(f"StasisEnd: Channel {event['channel']['id']} left app.")

async def main():
    client = ARIClient(ARI_URL, ARI_USER, ARI_PASS)
    
    try:
        await client.connect()
        print("Connected to ARI.")
        
        # 1. Setup Resources
        await setup_resources(client)
        
        # Jalankan aplikasi listener
        # Catatan: Untuk demo outbound call, Anda bisa uncomment baris di bawah ini,
        # tapi pastikan Asterisk running dan trunk valid.
        # asyncio.create_task(make_outbound_call(client))
        
        print(f"\nWaiting for incoming calls in application '{APP_NAME}'...")
        await client.run_app(APP_NAME, lambda e: event_handler(e, client))
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nStopping...")
