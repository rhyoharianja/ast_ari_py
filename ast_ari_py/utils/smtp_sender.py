import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import os

def send_recording_email(smtp_conf, recipient, subject, body, file_path):
    """
    Mengirimkan file rekaman sebagai lampiran email.
    Fungsi ini harus dijalankan di thread terpisah atau executor agar tidak memblokir loop asyncio.
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = smtp_conf['user']
    msg['To'] = recipient
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Pastikan file ada
        if not os.path.exists(file_path):
            print(f"File rekaman tidak ditemukan: {file_path}")
            return

        with open(file_path, 'rb') as f:
            # Membaca file biner dan melampirkannya
            file_data = f.read()
            filename = os.path.basename(file_path)
            part = MIMEApplication(file_data, Name=filename)
        
        part['Content-Disposition'] = f'attachment; filename="{filename}"'
        msg.attach(part)

        # Koneksi SMTP (gunakan SMTP_SSL untuk port 465)
        with smtplib.SMTP_SSL(smtp_conf['host'], smtp_conf['port']) as server:
            server.login(smtp_conf['user'], smtp_conf['password'])
            server.sendmail(smtp_conf['user'], recipient, msg.as_string())
            
        print(f"Email terkirim sukses ke {recipient}")
    except Exception as e:
        print(f"Gagal mengirim email: {str(e)}")
