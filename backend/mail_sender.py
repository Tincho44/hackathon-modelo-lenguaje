import smtplib
from email.message import EmailMessage

def enviar_correo(destinatario, asunto, cuerpo):
    try:
        # Crear el mensaje
        mensaje = EmailMessage()
        mensaje['Subject'] = asunto
        mensaje['From'] = remitente
        mensaje['To'] = destinatario
        mensaje.set_content(cuerpo)
        servidor_smtp='smtp.gmail.com'
        puerto=587
        remitente='lucasalegre13@gmail.com',
        clave= "nphn znpk xzlg fgff"

        # Conexión con el servidor SMTP
        with smtplib.SMTP(servidor_smtp, puerto) as servidor:
            servidor.starttls()  # Seguridad TLS
            servidor.login(remitente, clave)
            servidor.send_message(mensaje)
        return True
    
    except Exception as e:
        print(f"Error al enviar el correo: {e}")