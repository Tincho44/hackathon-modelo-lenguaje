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
    .chatbot-button {{ 
      display: inline-block; 
      background: linear-gradient(135deg, #004A96 0%, #21A0D2 100%); 
      color: white; 
      padding: 14px 28px; 
      text-decoration: none; 
      border-radius: 8px; 
      font-weight: bold; 
      font-size: 16px; 
      margin: 20px 0; 
      text-align: center; 
      box-shadow: 0 4px 12px rgba(0, 74, 150, 0.3); 
      transition: transform 0.2s ease; 
    }}
    .chatbot-button:hover {{ 
      transform: translateY(-2px); 
      box-shadow: 0 6px 16px rgba(0, 74, 150, 0.4); 
    }}
    .button-container {{ 
      text-align: center; 
      margin: 25px 0; 
    }}
    .footer {{ margin-top: 40px; font-size: 0.9em; color: #a0aec0; text-align: center; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Estimado/a Jefe de Planta,</h1>
    <p>
      Se detectó un incidente en la planta de producción A, en el proceso de Trasvase de Metacrilato de Metilo (MMA) desde cisterna a tanque de almacenamiento.
      El incidente ocurrió el 15 de enero de 2025 a las 10:30 AM.<br><br>
      <strong>Alerta registrada:</strong><br>
      <em>"{llm_msg}"</em>
    </p>
    
    <div class="button-container">
      <p><strong>Acceda al chatbot de BASF Assistant para ver la respuesta:</strong></p>
      <a href="{chatbot_url}" class="chatbot-button">Ver respuesta en BASF Assistant</a>
    </div>
    
    <div class="footer">
      © 2025 BASF. Todos los derechos reservados.
    </div>
  </div>
</body>
</html>
"""



def enviar_correo(query_text, chatbot_url):
    try:
        print(f"Enviando correo con consulta original: {query_text[:100]}...")
        print(f"URL del chatbot: {chatbot_url}")
        
        remitente='lucasalegre13@gmail.com'
        destinatario='poptnico75@gmail.com'
        asunto='Alerta de incidente - BASF Assistant'
        
        # Crear el mensaje
        message = MIMEMultipart("alternative")        
        message['Subject'] = asunto
        message['From'] = remitente
        message['To'] = destinatario
        servidor_smtp='smtp.gmail.com'
        puerto=587
        clave= "nphn znpk xzlg fgff"
        
        # Formatear el HTML con ambos parámetros
        html_body = html_template.format(llm_msg=query_text, chatbot_url=chatbot_url)
        body = MIMEText(html_body, 'html')
        message.attach(body)
        
        # Conexión con el servidor SMTP
        with smtplib.SMTP(servidor_smtp, puerto) as servidor:
            servidor.starttls()  # Seguridad TLS
            servidor.login(remitente, clave)
            servidor.sendmail(remitente, destinatario, message.as_string())
        print("✅ Correo enviado exitosamente con URL del chatbot")
        return True
    
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False