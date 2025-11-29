import asyncio
import logging
from ast_ari_py import ARIClient
from ast_ari_py.core.exceptions import (
    ARIBadRequest, ARIAuthError, ARIForbidden, 
    ResourceNotFound, ARIUnprocessableEntity, ARIServerError
)

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ARI_URL = "http://localhost:8088/ari"
ARI_USER = "asterisk"
ARI_PASS = "asterisk"

async def demonstrate_asterisk_info(client):
    print("\n--- 1. Asterisk System Info ---")
    try:
        info = await client.asterisk.get_info()
        print(f"System Info: {info}")
        
        modules = await client.asterisk.list_modules()
        print(f"Loaded Modules: {len(modules)} modules found.")
        
    except ARIForbidden as e:
        print(f"ERROR: Akses ditolak. Cek izin user di ari.conf. Detail: {e}")
    except Exception as e:
        print(f"ERROR: {e}")

async def demonstrate_sounds(client):
    print("\n--- 2. Sound Resources ---")
    try:
        sounds = await client.sounds.list(lang="en", format="wav")
        print(f"Found {len(sounds)} sounds (en/wav).")
        
        if sounds:
            first_sound = sounds[0]
            details = await client.sounds.get(first_sound.id)
            print(f"Details for '{first_sound.id}': {details.text}")
            
    except ResourceNotFound as e:
        print(f"ERROR: Sound tidak ditemukan. Detail: {e}")

async def demonstrate_mailbox_error_handling(client):
    print("\n--- 3. Mailbox & Error Handling ---")
    try:
        # Mencoba update mailbox yang mungkin tidak ada
        print("Updating mailbox 'non_existent_box'...")
        await client.mailboxes.update("non_existent_box", old_messages=0, new_messages=5)
        
    except ResourceNotFound:
        print("CAUGHT ERROR (404): Mailbox tidak ditemukan. Ini diharapkan.")
        
    except ARIBadRequest as e:
        print(f"CAUGHT ERROR (400): Parameter salah. Detail: {e}")

async def demonstrate_channel_errors(client):
    print("\n--- 4. Channel Error Handling ---")
    try:
        # Mencoba menutup channel yang tidak valid
        print("Hanging up invalid channel...")
        fake_channel = await client.channels.get("invalid-id")
        await fake_channel.hangup()
        
    except ResourceNotFound:
        print("CAUGHT ERROR (404): Channel tidak ditemukan.")
        
    except ARIUnprocessableEntity as e:
        print(f"CAUGHT ERROR (422): Request valid tapi state salah. Detail: {e}")

async def main():
    client = ARIClient(ARI_URL, ARI_USER, ARI_PASS)
    
    try:
        await client.connect()
        print("Connected to ARI.")
        
        await demonstrate_asterisk_info(client)
        await demonstrate_sounds(client)
        await demonstrate_mailbox_error_handling(client)
        await demonstrate_channel_errors(client)
        
    except ARIAuthError:
        print("CRITICAL: Gagal Login! Cek username/password.")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
