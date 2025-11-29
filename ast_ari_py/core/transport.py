import aiohttp
import asyncio
import logging
import ujson as json
from yarl import URL
from .exceptions import (
    ARIError, ResourceNotFound, InvalidState, ARIBadRequest, 
    ARIAuthError, ARIForbidden, ARIUnprocessableEntity, ARIServerError
)

class ARITransport:
    def __init__(self, base_url, username, password, loop=None):
        self._base_url = URL(base_url)
        self._auth = aiohttp.BasicAuth(username, password)
        self._loop = loop or asyncio.get_event_loop()
        self._session = None
        self._logger = logging.getLogger(__name__)
        self._closed = False

    async def connect(self):
        """Menginisialisasi sesi aiohttp."""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                auth=self._auth,
                json_serialize=json.dumps
            )
            self._logger.info(f"Sesi ARI terhubung ke {self._base_url}")

    async def close(self):
        """Menutup sesi dan membersihkan sumber daya."""
        if self._session:
            await self._session.close()
            self._closed = True
            self._logger.info("Sesi ARI ditutup.")

    async def request(self, method, endpoint, params=None, data=None):
        """
        Menjalankan permintaan REST ke Asterisk dengan penanganan kesalahan terpusat.
        
        Args:
            method (str): Metode HTTP (GET, POST, DELETE, dll).
            endpoint (str): Jalur API (misal: '/channels').
            params (dict): Parameter query string.
            data (dict): Payload JSON untuk body permintaan.
        """
        if self._closed or not self._session:
            raise ARIError("Transport belum terhubung atau sudah ditutup.")

        url = self._base_url.join(URL(endpoint))
        
        try:
            async with self._session.request(method, url, params=params, json=data) as response:
                # Logika penanganan respon berdasarkan kode status
                if response.status == 204:
                    return None  # Sukses tanpa konten (No Content)
                
                response_text = await response.text()
                
                if response.status >= 400:
                    self._logger.warning(
                        f"Permintaan ARI Gagal: {method} {url} -> {response.status}: {response_text}"
                    )
                    
                    # Pemetaan kesalahan spesifik ARI
                    if response.status == 400:
                        raise ARIBadRequest(f"Permintaan tidak valid (400): {response_text}")
                    elif response.status == 401:
                        raise ARIAuthError(f"Gagal otentikasi (401): {response_text}")
                    elif response.status == 403:
                        raise ARIForbidden(f"Akses ditolak (403): {response_text}")
                    elif response.status == 404:
                        raise ResourceNotFound(f"Sumber daya tidak ditemukan (404): {endpoint}")
                    elif response.status == 409:
                        raise InvalidState(f"Konflik keadaan sumber daya (409): {response_text}")
                    elif response.status == 422:
                        raise ARIUnprocessableEntity(f"Entitas tidak dapat diproses (422): {response_text}")
                    elif response.status >= 500:
                        raise ARIServerError(f"Kesalahan Server Asterisk ({response.status}): {response_text}")
                    else:
                        raise ARIError(f"Kesalahan ARI {response.status}: {response_text}")

                try:
                    return json.loads(response_text)
                except ValueError:
                    return response_text

        except aiohttp.ClientError as e:
            self._logger.error(f"Kesalahan koneksi jaringan: {e}")
            raise ARIError(f"Kegagalan transportasi jaringan: {str(e)}")

    async def connect_websocket(self, app_name, event_callback):
        """
        Membangun koneksi WebSocket persisten untuk menerima kejadian.
        
        Args:
            app_name (str): Nama aplikasi Stasis yang didaftarkan di extensions.conf.
            event_callback (coroutine): Fungsi asinkron untuk memproses setiap kejadian JSON.
        """
        # Konstruksi URL WebSocket
        ws_scheme = "wss" if self._base_url.scheme == "https" else "ws"
        # Perhatikan: ARI memerlukan api_key di parameter query untuk WebSocket jika tidak menggunakan header
        ws_url = self._base_url.with_scheme(ws_scheme).with_path(self._base_url.path + "/events")
        
        params = {
            'app': app_name,
            'api_key': f"{self._auth.login}:{self._auth.password}"
        }

        retry_count = 0
        max_retries = 5
        base_delay = 2

        while not self._closed:
            try:
                self._logger.info(f"Mencoba menghubungkan WebSocket ke {ws_url} untuk aplikasi '{app_name}'...")
                async with self._session.ws_connect(ws_url, params=params) as ws:
                    self._logger.info("WebSocket terhubung. Mulai mendengarkan kejadian.")
                    retry_count = 0  # Reset retry count setelah sukses
                    
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            try:
                                event_data = json.loads(msg.data)
                                # Dispatch kejadian secara asinkron tanpa memblokir pembacaan soket berikutnya
                                asyncio.create_task(event_callback(event_data))
                            except ValueError:
                                self._logger.error("Gagal mendecode JSON dari pesan WebSocket")
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            self._logger.error(f"Koneksi WebSocket terputus dengan error: {ws.exception()}")
                            break
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            self._logger.warning("WebSocket ditutup oleh server.")
                            break
                            
            except aiohttp.ClientConnectorError as e:
                self._logger.error(f"Gagal menghubungkan WebSocket: {e}")
            except Exception as e:
                self._logger.exception(f"Kesalahan tidak terduga di loop WebSocket: {e}")
            
            # Logika Eksponensial Backoff untuk Reconnection
            if not self._closed:
                retry_count += 1
                delay = min(base_delay * (2 ** (retry_count - 1)), 60) # Maksimal delay 60 detik
                self._logger.info(f"Menunggu {delay} detik sebelum mencoba menghubungkan ulang...")
                await asyncio.sleep(delay)
