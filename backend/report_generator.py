from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib import colors
from datetime import datetime
import io
import json
import locale

# Set locale to Spanish for date formatting
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES')
    except locale.Error:
        # Fallback to default if Spanish locale not available
        pass

# Colores corporativos BASF
BASF_RED = HexColor('#C50022')
BASF_DARK_BLUE = HexColor('#004A96')
BASF_LIGHT_BLUE = HexColor('#21A0D2')
BASF_GRAY = HexColor('#666666')

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom styles for BASF branding"""
        # Main title style
        self.styles.add(ParagraphStyle(
            name='BASFTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=BASF_DARK_BLUE,
            fontName='Helvetica-Bold',
            spaceBefore=20,
            spaceAfter=30,
            alignment=1  # Center
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='BASFSubtitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=BASF_RED,
            fontName='Helvetica-Bold',
            spaceBefore=20,
            spaceAfter=12
        ))
        
        # Alert style
        self.styles.add(ParagraphStyle(
            name='BASFAlert',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=BASF_RED,
            fontName='Helvetica-Bold',
            leftIndent=20,
            spaceBefore=10,
            spaceAfter=10,
            borderColor=BASF_RED,
            borderWidth=2,
            borderPadding=10
        ))
        
        # Normal content style
        self.styles.add(ParagraphStyle(
            name='BASFContent',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            fontName='Helvetica',
            spaceBefore=6,
            spaceAfter=6,
            leftIndent=10
        ))

    def generate_conversation_report(self, conversation_data, output_path=None):
        """Generate a PDF report from conversation data"""
        # Create a BytesIO buffer if no output path provided
        if output_path is None:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                  rightMargin=72, leftMargin=72, 
                                  topMargin=72, bottomMargin=18)
        else:
            doc = SimpleDocTemplate(output_path, pagesize=A4,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
        
        # Build the story (content)
        story = []
        
        # Header
        story.append(Paragraph("BASF - Reporte de Incidente de Seguridad", self.styles['BASFTitle']))
        story.append(Spacer(1, 12))
        
        # Metadata table
        metadata = [
            ['Fecha del Reporte:', datetime.now().strftime("%d/%m/%Y %H:%M")],
            ['Sistema:', 'BASF Assistant - Gestión de Seguridad'],
            ['Tipo:', 'Análisis de Incidente Químico']
        ]
        
        metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#F5F5F5')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(metadata_table)
        story.append(Spacer(1, 20))
        
        # Extract and process conversation
        if 'messages' in conversation_data:
            messages = conversation_data['messages']
            
            # Find user query and assistant response
            user_query = None
            assistant_response = None
            
            for msg in messages:
                if msg.get('role') == 'user' and len(msg.get('content', '')) > 20:
                    user_query = msg['content']
                elif msg.get('role') == 'assistant' and not msg.get('isTyping'):
                    assistant_response = msg['content']
            
            # Incident Description
            story.append(Paragraph("1. DESCRIPCIÓN DEL INCIDENTE", self.styles['BASFSubtitle']))
            
            if user_query:
                # Extract key information from the query
                incident_summary = self._extract_incident_summary(user_query)
                story.append(Paragraph(incident_summary, self.styles['BASFContent']))
            else:
                # Default incident description when no specific query detected
                current_datetime = self._format_datetime_spanish(datetime.now())
                default_incident = f"""
                • <b>Ubicación:</b> Planta de Producción A - Área de Operaciones<br/>
                • <b>Fecha y Hora:</b> {current_datetime}<br/>
                • <b>Incidente:</b> Empleado operario se retiró el casco de seguridad durante operaciones de trasvase<br/>
                • <b>Sustancia Involucrada:</b> Metacrilato de Metilo (MMA)<br/>
                • <b>Violación de Seguridad:</b> Incumplimiento del protocolo de EPP (Equipo de Protección Personal)<br/>
                • <b>Riesgo Detectado:</b> Exposición potencial a vapores químicos y riesgo de impacto en la cabeza
                """
                story.append(Paragraph(default_incident, self.styles['BASFContent']))
            
            story.append(Spacer(1, 15))
            
            # Response and Recommendations
            story.append(Paragraph("2. ANÁLISIS Y RECOMENDACIONES", self.styles['BASFSubtitle']))
            
            if assistant_response:
                # Clean and format the response
                formatted_response = self._format_response(assistant_response)
                story.append(Paragraph(formatted_response, self.styles['BASFContent']))
            else:
                # Default analysis and recommendations when no specific response detected
                default_analysis = """
                <b>ANÁLISIS DEL INCIDENTE:</b><br/>
                El retiro del casco de seguridad por parte del operario durante las operaciones de trasvase de MMA constituye una grave violación de los protocolos de seguridad establecidos. Esta acción expone al trabajador a riesgos significativos de inhalación de vapores químicos y posibles traumatismos craneoencefálicos.<br/><br/>
                
                <b>FACTORES DE RIESGO IDENTIFICADOS:</b><br/>
                • Exposición directa a vapores de Metacrilato de Metilo<br/>
                • Riesgo de impacto por caída de objetos o equipos<br/>
                • Incumplimiento de normativas de seguridad industrial<br/>
                • Posible falta de supervisión en el área de trabajo<br/><br/>
                
                <b>RECOMENDACIONES INMEDIATAS:</b><br/>
                • <b>Acción Correctiva:</b> Suspensión temporal del empleado para capacitación en seguridad<br/>
                • <b>Medidas Preventivas:</b> Reforzar la supervisión en área de trasvase<br/>
                • <b>Capacitación:</b> Sesión obligatoria sobre uso correcto de EPP<br/>
                • <b>Seguimiento:</b> Evaluación médica del empleado por posible exposición<br/>
                • <b>Protocolo:</b> Revisión de procedimientos de seguridad en operaciones con MMA
                """
                story.append(Paragraph(default_analysis, self.styles['BASFContent']))
            
            story.append(Spacer(1, 15))
            
            # Summary Table
            story.append(Paragraph("3. RESUMEN EJECUTIVO", self.styles['BASFSubtitle']))
            
            summary_data = self._create_summary_table(user_query, assistant_response)
            summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), BASF_LIGHT_BLUE),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
        
        # Footer
        story.append(Spacer(1, 30))
        footer_text = f"Generado automáticamente por BASF Assistant • {datetime.now().strftime('%d/%m/%Y %H:%M')} • Confidencial"
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        if output_path is None:
            pdf_data = buffer.getvalue()
            buffer.close()
            return pdf_data
        
        return output_path

    def _extract_incident_summary(self, query):
        """Extract key incident information from the user query"""
        # Extract key details using simple text processing
        lines = []
        
        if "planta" in query.lower():
            lines.append("• Ubicación: Detectado en instalaciones de planta de producción")
        
        if "metacrilato" in query.lower() or "MMA" in query:
            lines.append("• Sustancia Involucrada: Metacrilato de Metilo (MMA)")
        
        if "casco" in query.lower():
            lines.append("• Violación de Seguridad: Trabajador sin equipo de protección personal (casco)")
        
        if "trasvase" in query.lower():
            lines.append("• Actividad: Operaciones de trasvase de material químico")
        
        if not lines:
            # Default incident when no specific details are detected
            lines = [
                "• <b>Ubicación:</b> Planta de Producción A - Área de Operaciones",
                "• <b>Incidente:</b> Empleado operario se retiró el casco de seguridad durante operaciones",
                "• <b>Violación de Seguridad:</b> Incumplimiento del protocolo de EPP",
                "• <b>Sustancia Involucrada:</b> Metacrilato de Metilo (MMA)",
                "• <b>Riesgo:</b> Exposición a vapores químicos y riesgo de traumatismo"
            ]
        
        return "<br/>".join(lines)

    def _format_response(self, response):
        """Format the assistant response for PDF"""
        # Clean up the response and handle ** formatting correctly
        import re
        
        # Replace ** with proper bold tags
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)
        
        # Handle numbered lists
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('*'):
                line = "• " + line[1:].strip()
            elif line and not line.startswith('•'):
                # Add spacing for paragraphs
                if formatted_lines and formatted_lines[-1]:
                    formatted_lines.append("")
            
            if line:
                formatted_lines.append(line)
        
        return "<br/>".join(formatted_lines)

    def _create_summary_table(self, query, response):
        """Create summary table data"""
        summary = [
            ['Nivel de Riesgo:', 'ALTO - Requiere acción inmediata'],
            ['Estado:', 'Protocolo de emergencia activado'],
            ['Sustancia:', 'Metacrilato de Metilo (MMA)'],
            ['Acción Requerida:', 'Confinamiento, evacuación y uso de EPP']
        ]
        
        # Analyze response for specific risks
        if response and "alerta" in response.lower():
            summary[0] = ['Nivel de Riesgo:', 'CRÍTICO - Alerta activada']
        
        return summary
    
    def _format_datetime_spanish(self, dt):
        """Format datetime to Spanish format"""
        months_spanish = {
            1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
            5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
            9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
        }
        
        day = dt.day
        month = months_spanish[dt.month]
        year = dt.year
        time = dt.strftime("%H:%M")
        
        return f"{day} de {month} de {year}, {time}"