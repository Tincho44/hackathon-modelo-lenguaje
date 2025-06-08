import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


html_test = """\
<html>
  <body>
    <h1>Hello!</h1>
    <p>This is an <b>HTML</b> email sent from Python.</p>
  </body>
</html>
"""

html_template = """
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{font-family: 'Segoe UI', Arial, sans-serif; background: #f4f4f7; margin: 0; padding: 0; }}
    .container {{ background: #fff; max-width: 600px; margin: 40px auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); padding: 40px; }}
    h1 {{ color: #2d3748; }}
    p {{ color: #4a5568; line-height: 1.6; }}
    .footer {{ margin-top: 40px; font-size: 0.9em; color: #a0aec0; text-align: center; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Estimado/a Jefe de Planta,</h1>
    <p>
      Se detectó un incidente en la planta de producción A, en el proceso de Trasvase de Metacrilato de Metilo (MMA) desde cisterna a tanque de almacenamiento.
      El incidente ocurrió el 15 de enero de 2025 a las 10:30 AM.<br><br>
      {llm_msg}
      <br><br>
      <strong>Para más información, visite</strong><br>
      <a href="https://www.ejemplo.com/incidentes">https://www.ejemplo.com/incidentes</a>
    </p>
    <div class="footer">
      © 2025 BASF. Todos los derechos reservados.
    </div>
  </div>
</body>
</html>
"""



def enviar_correo(body):
    try:
        print(f"body en env_correo: {body}")
        # ...existing code...
        # ...existing code...
        remitente='lucasalegre13@gmail.com'
        destinatario='ciarlohernan@gmail.com'
        asunto='Alerta de incidente'
        # Crear el mensaje
        message = MIMEMultipart("alternative")        
        message['Subject'] = asunto
        message['From'] = remitente
        message['To'] = destinatario
        servidor_smtp='smtp.gmail.com'
        puerto=587
        clave= "nphn znpk xzlg fgff"
        
        # mensaje.set_content(html_template.format(llm_msg=body), subtype='html')
        # html_body = html_template.format(llm_msg=body)
        print(html_test)
        html_body = html_template.format(llm_msg=body)
        body = MIMEText(html_body, 'html')
        message.attach(body)
        # Conexión con el servidor SMTP
        with smtplib.SMTP(servidor_smtp, puerto) as servidor:
            servidor.starttls()  # Seguridad TLS
            servidor.login(remitente, clave)
            servidor.sendmail(remitente, destinatario, message.as_string())
        return True
    
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False