"""
PDFExporter - Exportador especializado para formato PDF.

Este módulo maneja la creación de archivos PDF con formato profesional,
incluyendo plantillas corporativas, diseño ejecutivo y presentación optimizada.

FUNCIONALIDADES:
- Creación de documentos PDF con diseño profesional
- Aplicación de plantillas corporativas con logo
- Formateo automático de tablas y datos
- Generación de gráficos y estadísticas
- Reportes ejecutivos con resúmenes

DEPENDENCIAS:
- reportlab: Librería principal para generación PDF
- PIL/Pillow: Procesamiento de imágenes (opcional)

ARQUITECTURA:
- Infrastructure Layer: Implementación concreta de exportación
- Template Method: Proceso estándar de creación PDF
- Builder Pattern: Construcción progresiva de documento

SPRINT 2: Implementación TDD con tests previos
Autor: Sistema de Inventario Copy Point S.A.
Versión: 1.0.0 - Sprint 2
Fecha: 2025-07-12
"""

import os
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, List, Optional, Union, Tuple

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import Color, black, white, blue, green, grey
    from reportlab.lib.units import inch, cm, mm
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.platypus import PageBreak, Image, KeepTogether
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.lib.validators import Auto
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Configurar logging
logger = logging.getLogger(__name__)


class PDFExporter:
    """
    Exportador especializado para archivos PDF con formato profesional.
    
    RESPONSABILIDADES:
    - Crear documentos PDF con diseño corporativo
    - Aplicar plantillas y estilos profesionales
    - Formatear tablas y datos para presentación óptima
    - Generar gráficos y visualizaciones
    - Crear reportes ejecutivos con resúmenes estadísticos
    
    PATRONES:
    - Template Method: Proceso estándar de creación PDF
    - Builder Pattern: Construcción progresiva de documento
    - Strategy Pattern: Diferentes layouts según tipo de reporte
    """
    
    def __init__(self):
        """
        Inicializar exportador PDF con configuración corporativa.
        
        Raises:
            ImportError: Si reportlab no está disponible
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab es requerido para PDFExporter. "
                "Instalar con: pip install reportlab>=3.6.0"
            )
        
        # Colores corporativos
        self.colors = {
            'primary': Color(0.12, 0.31, 0.47),      # #1F4E79 - Azul corporativo
            'secondary': Color(0.44, 0.68, 0.28),    # #70AD47 - Verde corporativo
            'accent': Color(0.77, 0.35, 0.07),       # #C55A11 - Naranja corporativo
            'light_gray': Color(0.95, 0.95, 0.95),   # #F2F2F2 - Gris claro
            'dark_gray': Color(0.35, 0.35, 0.35),    # #595959 - Gris oscuro
            'black': black,
            'white': white
        }
        
        # Información corporativa
        self.company_info = {
            'nombre': 'Copy Point S.A.',
            'ruc': '888-888-8888',
            'direccion': 'Las Lajas, Las Cumbres, Panamá',
            'telefono': '6666-6666',
            'email': 'copy.point@gmail.com',
            'web': 'www.copypoint.com.pa'
        }
        
        # Configuración de página
        self.page_config = {
            'pagesize': A4,
            'topMargin': 2*cm,
            'bottomMargin': 2*cm,
            'leftMargin': 2*cm,
            'rightMargin': 2*cm
        }
        
        # Estilos de texto
        self._setup_text_styles()
        
        logger.info("PDFExporter inicializado con configuración corporativa")
    
    def _setup_text_styles(self):
        """Configurar estilos de texto corporativos."""
        self.styles = getSampleStyleSheet()
        
        # Estilo para título principal
        self.styles.add(ParagraphStyle(
            name='CorporateTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CorporateSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            alignment=TA_LEFT,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para texto normal corporativo
        self.styles.add(ParagraphStyle(
            name='CorporateNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT,
            fontName='Helvetica'
        ))
        
        # Estilo para texto centrado
        self.styles.add(ParagraphStyle(
            name='CorporateCenter',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Estilo para información de empresa
        self.styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=self.colors['dark_gray'],
            fontName='Helvetica'
        ))
    
    def create_movements_pdf(self, template_data: Dict[str, Any], file_path: str) -> None:
        """
        Crear documento PDF para movimientos de inventario.
        
        Args:
            template_data: Datos formateados con plantilla aplicada
            file_path: Ruta donde guardar el archivo PDF
        
        Raises:
            ValueError: Si los datos no tienen formato correcto
            IOError: Si no se puede escribir el archivo
            Exception: Para otros errores de creación
        """
        try:
            # Validar datos de entrada
            self._validate_pdf_data(template_data)
            
            # Crear documento PDF
            doc = SimpleDocTemplate(
                file_path,
                pagesize=self.page_config['pagesize'],
                topMargin=self.page_config['topMargin'],
                bottomMargin=self.page_config['bottomMargin'],
                leftMargin=self.page_config['leftMargin'],
                rightMargin=self.page_config['rightMargin']
            )
            
            # Construir contenido del documento
            story = []
            
            # Header corporativo
            self._add_corporate_header(story, template_data)
            
            # Resumen ejecutivo
            if template_data.get('summary'):
                self._add_executive_summary(story, template_data['summary'])
            
            # Tabla de datos
            if template_data.get('data'):
                self._add_data_table(story, template_data['data'])
            else:
                self._add_empty_data_message(story)
            
            # Footer con información adicional
            self._add_document_footer(story, template_data)
            
            # Generar PDF
            doc.build(story, onFirstPage=self._create_page_header, 
                     onLaterPages=self._create_page_header)
            
            logger.info(f"PDF creado exitosamente: {file_path}")
            
        except ValueError as e:
            logger.error(f"Datos inválidos para PDF: {e}")
            raise
        except IOError as e:
            logger.error(f"Error escribiendo archivo PDF: {e}")
            raise IOError(f"No se pudo guardar archivo PDF: {e}")
        except Exception as e:
            logger.error(f"Error inesperado creando PDF: {e}")
            raise Exception(f"Error creando PDF: {e}")
    
    def _validate_pdf_data(self, template_data: Dict[str, Any]) -> None:
        """
        Validar que los datos tienen la estructura correcta para PDF.
        
        Args:
            template_data: Datos a validar
        
        Raises:
            ValueError: Si la estructura no es válida
        """
        if not isinstance(template_data, dict):
            raise ValueError("template_data debe ser un diccionario")
        
        required_keys = ['title', 'filters']
        for key in required_keys:
            if key not in template_data:
                raise ValueError(f"Clave requerida '{key}' faltante en template_data")
        
        # Validar datos si existen
        if 'data' in template_data and template_data['data']:
            if not isinstance(template_data['data'], list):
                raise ValueError("template_data['data'] debe ser una lista")
        
        logger.debug(f"Datos PDF validados: {template_data.get('title', 'Sin título')}")
    
    def _add_corporate_header(self, story: List, template_data: Dict[str, Any]) -> None:
        """
        Agregar header corporativo al documento.
        
        Args:
            story: Lista de elementos del documento
            template_data: Datos del reporte
        """
        # Nombre de la empresa
        company_name = Paragraph(
            f"<b>{self.company_info['nombre']}</b>",
            self.styles['CorporateTitle']
        )
        story.append(company_name)
        
        # Información corporativa
        company_details = Paragraph(
            f"RUC: {self.company_info['ruc']} | "
            f"Tel: {self.company_info['telefono']} | "
            f"Email: {self.company_info['email']}",
            self.styles['CompanyInfo']
        )
        story.append(company_details)
        story.append(Spacer(1, 0.3*inch))
        
        # Título del reporte
        report_title = Paragraph(
            f"<b>{template_data.get('title', 'Reporte de Inventario')}</b>",
            self.styles['CorporateSubtitle']
        )
        story.append(report_title)
        
        # Información de filtros
        filters_info = self._format_filters_for_pdf(template_data.get('filters', {}))
        if filters_info:
            filters_para = Paragraph(
                f"<b>Filtros aplicados:</b> {filters_info}",
                self.styles['CorporateNormal']
            )
            story.append(filters_para)
        
        # Fecha de generación
        generation_date = Paragraph(
            f"<b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            self.styles['CorporateNormal']
        )
        story.append(generation_date)
        story.append(Spacer(1, 0.2*inch))
    
    def _add_executive_summary(self, story: List, summary: Dict[str, Any]) -> None:
        """
        Agregar resumen ejecutivo al documento.
        
        Args:
            story: Lista de elementos del documento
            summary: Datos de resumen
        """
        # Título de resumen
        summary_title = Paragraph(
            "<b>RESUMEN EJECUTIVO</b>",
            self.styles['CorporateSubtitle']
        )
        story.append(summary_title)
        
        # Crear tabla de resumen
        summary_data = [
            ['Métrica', 'Valor'],
            ['Total de Movimientos', str(summary.get('total_movimientos', 0))],
            ['Total Entradas', str(summary.get('total_entradas', 0))],
            ['Total Ajustes', str(summary.get('total_ajustes', 0))],
            ['Valor Total', summary.get('valor_total', 'B/. 0.00')]
        ]
        
        # Agregar información adicional si está disponible
        if 'total_productos' in summary:
            summary_data.append(['Productos Afectados', str(summary['total_productos'])])
        
        if 'periodo_generacion' in summary:
            summary_data.append(['Período', summary['periodo_generacion']])
        
        # Crear tabla con estilo
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.colors['white'], self.colors['light_gray']]),
            
            # Borders
            ('GRID', (0, 0), (-1, -1), 1, self.colors['dark_gray']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
    
    def _add_data_table(self, story: List, data: List[Dict[str, Any]]) -> None:
        """
        Agregar tabla principal de datos al documento.
        
        Args:
            story: Lista de elementos del documento
            data: Lista de registros de datos
        """
        if not data:
            return
        
        # Título de la tabla
        table_title = Paragraph(
            "<b>DETALLE DE MOVIMIENTOS</b>",
            self.styles['CorporateSubtitle']
        )
        story.append(table_title)
        
        # Preparar datos para la tabla
        # Headers
        headers = list(data[0].keys())
        table_data = [headers]
        
        # Datos
        for record in data:
            row = []
            for header in headers:
                value = record.get(header, '')
                # Truncar valores muy largos para PDF
                if isinstance(value, str) and len(value) > 30:
                    value = value[:27] + "..."
                row.append(str(value))
            table_data.append(row)
        
        # Calcular anchos de columna dinámicamente
        page_width = self.page_config['pagesize'][0] - (self.page_config['leftMargin'] + self.page_config['rightMargin'])
        col_count = len(headers)
        col_width = page_width / col_count
        col_widths = [col_width] * col_count
        
        # Crear tabla
        data_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Aplicar estilo a la tabla
        data_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.colors['white'], self.colors['light_gray']]),
            
            # Borders
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['dark_gray']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Ajustar alineación para columnas numéricas
            ('ALIGN', (4, 1), (4, -1), 'RIGHT'),  # Cantidad
            ('ALIGN', (5, 1), (5, -1), 'RIGHT'),  # Stock Anterior
            ('ALIGN', (6, 1), (6, -1), 'RIGHT'),  # Stock Nuevo
        ]))
        
        # Envolver tabla para mantener unida si es posible
        story.append(KeepTogether(data_table))
        story.append(Spacer(1, 0.2*inch))
    
    def _add_empty_data_message(self, story: List) -> None:
        """
        Agregar mensaje cuando no hay datos para mostrar.
        
        Args:
            story: Lista de elementos del documento
        """
        empty_message = Paragraph(
            "<i>No hay datos para mostrar con los filtros aplicados.</i>",
            self.styles['CorporateCenter']
        )
        story.append(empty_message)
        story.append(Spacer(1, 0.3*inch))
    
    def _add_document_footer(self, story: List, template_data: Dict[str, Any]) -> None:
        """
        Agregar footer con información adicional.
        
        Args:
            story: Lista de elementos del documento
            template_data: Datos del template
        """
        story.append(PageBreak())
        
        # Información técnica
        footer_info = [
            f"Reporte generado por Sistema de Inventario {self.company_info['nombre']}",
            f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "Este documento es generado automáticamente por el sistema."
        ]
        
        for info in footer_info:
            footer_para = Paragraph(info, self.styles['CompanyInfo'])
            story.append(footer_para)
    
    def _create_page_header(self, canvas, doc) -> None:
        """
        Crear header de página (aparece en cada página).
        
        Args:
            canvas: Canvas de ReportLab
            doc: Documento
        """
        canvas.saveState()
        
        # Línea superior decorativa
        canvas.setStrokeColor(self.colors['primary'])
        canvas.setLineWidth(2)
        canvas.line(doc.leftMargin, doc.height + doc.topMargin - 10,
                   doc.width + doc.leftMargin, doc.height + doc.topMargin - 10)
        
        # Número de página en footer
        page_num = canvas.getPageNumber()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(self.colors['dark_gray'])
        canvas.drawRightString(
            doc.width + doc.leftMargin,
            doc.bottomMargin - 20,
            f"Página {page_num}"
        )
        
        # Información de empresa en footer
        canvas.drawString(
            doc.leftMargin,
            doc.bottomMargin - 20,
            f"{self.company_info['nombre']} - {self.company_info['telefono']}"
        )
        
        canvas.restoreState()
    
    def _format_filters_for_pdf(self, filters: Dict[str, Any]) -> str:
        """
        Formatear información de filtros para PDF.
        
        Args:
            filters: Diccionario de filtros aplicados
        
        Returns:
            str: Texto formateado de filtros
        """
        if not filters:
            return "Ninguno"
        
        filter_parts = []
        
        for key, value in filters.items():
            if key in ['fecha_inicio', 'fecha_fin', 'mensaje']:
                continue  # Manejado por separado
            
            if value and str(value).upper() not in ['TODOS', 'ALL', 'NINGUNO']:
                formatted_key = key.replace('_', ' ').title()
                filter_parts.append(f"{formatted_key}: {value}")
        
        # Agregar mensaje si existe
        if 'mensaje' in filters:
            filter_parts.append(filters['mensaje'])
        
        # Agregar rango de fechas si existe
        if 'fecha_inicio' in filters and 'fecha_fin' in filters:
            inicio = filters['fecha_inicio']
            fin = filters['fecha_fin']
            if inicio and fin:
                filter_parts.append(f"Período: {inicio} - {fin}")
        
        return "; ".join(filter_parts) if filter_parts else "Ninguno"
    
    def create_chart_pdf(self, chart_data: Dict[str, Any], file_path: str) -> None:
        """
        Crear PDF con gráficos especializados.
        
        Args:
            chart_data: Datos para generar gráficos
            file_path: Ruta del archivo PDF
        """
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            
            # Header
            title = Paragraph("Análisis Gráfico de Inventario", self.styles['CorporateTitle'])
            story.append(title)
            story.append(Spacer(1, 0.5*inch))
            
            # Crear gráfico de torta si hay datos categóricos
            if 'categories' in chart_data:
                pie_chart = self._create_pie_chart(chart_data['categories'])
                story.append(pie_chart)
            
            # Crear gráfico de barras si hay datos temporales
            if 'timeline' in chart_data:
                bar_chart = self._create_bar_chart(chart_data['timeline'])
                story.append(bar_chart)
            
            doc.build(story)
            logger.info(f"PDF con gráficos creado: {file_path}")
            
        except Exception as e:
            logger.error(f"Error creando PDF con gráficos: {e}")
            raise
    
    def _create_pie_chart(self, data: Dict[str, int]) -> Drawing:
        """
        Crear gráfico de torta para distribución categórica.
        
        Args:
            data: Datos categóricos {categoría: valor}
        
        Returns:
            Drawing: Gráfico de torta
        """
        drawing = Drawing(400, 200)
        
        pie = Pie()
        pie.x = 50
        pie.y = 50
        pie.width = 100
        pie.height = 100
        
        # Datos para el gráfico
        pie.data = list(data.values())
        pie.labels = list(data.keys())
        
        # Colores corporativos
        pie.slices.strokeColor = self.colors['white']
        pie.slices.strokeWidth = 1
        
        drawing.add(pie)
        return drawing
    
    def _create_bar_chart(self, data: Dict[str, int]) -> Drawing:
        """
        Crear gráfico de barras para datos temporales.
        
        Args:
            data: Datos temporales {período: valor}
        
        Returns:
            Drawing: Gráfico de barras
        """
        drawing = Drawing(400, 200)
        
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.width = 300
        chart.height = 125
        
        # Datos para el gráfico
        chart.data = [list(data.values())]
        chart.categoryAxis.categoryNames = list(data.keys())
        
        # Estilo corporativo
        chart.bars[0].fillColor = self.colors['secondary']
        
        drawing.add(chart)
        return drawing
    
    def get_supported_formats(self) -> List[str]:
        """
        Obtener lista de formatos soportados por este exportador.
        
        Returns:
            List[str]: Formatos soportados
        """
        return ['.pdf']
    
    def validate_file_path(self, file_path: str) -> bool:
        """
        Validar que la ruta de archivo es válida para PDF.
        
        Args:
            file_path: Ruta del archivo
        
        Returns:
            bool: True si es válida
        """
        if not file_path:
            return False
        
        # Verificar extensión
        valid_extensions = self.get_supported_formats()
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in valid_extensions:
            return False
        
        # Verificar que el directorio padre existe o se puede crear
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError:
                return False
        
        return True
    
    def create_entry_ticket_pdf(self, template_data: Dict[str, Any], file_path: str) -> None:
        """
        Crear documento PDF para ticket de entrada de inventario.
        
        Args:
            template_data: Datos formateados del ticket
                - title: Título del ticket
                - ticket_info: Información básica del ticket
                - productos: Lista de productos
                - resumen: Resumen del ticket
                - empresa: Información corporativa
            file_path: Ruta donde guardar el archivo PDF
        
        Raises:
            ValueError: Si los datos no tienen formato correcto
            IOError: Si no se puede escribir el archivo
            Exception: Para otros errores de creación
        """
        try:
            # Validar datos específicos para ticket
            self._validate_ticket_pdf_data(template_data)
            
            # Crear documento PDF con tamaño de página más compacto para tickets
            doc = SimpleDocTemplate(
                file_path,
                pagesize=self.page_config['pagesize'],
                topMargin=1.5*cm,
                bottomMargin=1.5*cm,
                leftMargin=1.5*cm,
                rightMargin=1.5*cm
            )
            
            # Construir contenido del ticket
            story = []
            
            # Header del ticket
            self._add_ticket_header(story, template_data)
            
            # Información del ticket
            self._add_ticket_info(story, template_data.get('ticket_info', {}))
            
            # Tabla de productos
            if template_data.get('productos'):
                self._add_ticket_products_table(story, template_data['productos'])
            
            # Resumen del ticket
            if template_data.get('resumen'):
                self._add_ticket_summary(story, template_data['resumen'])
            
            # Footer del ticket
            self._add_ticket_footer(story, template_data)
            
            # Generar PDF
            doc.build(story, onFirstPage=self._create_ticket_page_header, 
                     onLaterPages=self._create_ticket_page_header)
            
            logger.info(f"Ticket PDF creado exitosamente: {file_path}")
            
        except ValueError as e:
            logger.error(f"Datos inválidos para ticket PDF: {e}")
            raise
        except IOError as e:
            logger.error(f"Error escribiendo ticket PDF: {e}")
            raise IOError(f"No se pudo guardar ticket PDF: {e}")
        except Exception as e:
            logger.error(f"Error inesperado creando ticket PDF: {e}")
            raise Exception(f"Error creando ticket PDF: {e}")
    
    def _validate_ticket_pdf_data(self, template_data: Dict[str, Any]) -> None:
        """
        Validar que los datos del ticket tienen la estructura correcta para PDF.
        
        Args:
            template_data: Datos a validar
        
        Raises:
            ValueError: Si la estructura no es válida
        """
        if not isinstance(template_data, dict):
            raise ValueError("template_data debe ser un diccionario")
        
        required_keys = ['title', 'ticket_info']
        for key in required_keys:
            if key not in template_data:
                raise ValueError(f"Clave requerida '{key}' faltante en template_data")
        
        # Validar información del ticket
        ticket_info = template_data.get('ticket_info', {})
        if not ticket_info.get('numero'):
            raise ValueError("Número de ticket es requerido")
        
        logger.debug(f"Datos de ticket PDF validados: {ticket_info.get('numero', 'Sin número')}")
    
    def _add_ticket_header(self, story: List, template_data: Dict[str, Any]) -> None:
        """
        Agregar header del ticket al documento.
        
        Args:
            story: Lista de elementos del documento
            template_data: Datos del ticket
        """
        # Información de la empresa
        empresa = template_data.get('empresa', self.company_info)
        
        # Nombre de la empresa
        company_name = Paragraph(
            f"<b>{empresa.get('nombre', 'Copy Point S.A.')}</b>",
            self.styles['CorporateTitle']
        )
        story.append(company_name)
        
        # Dirección y contacto
        company_details = Paragraph(
            f"{empresa.get('direccion', 'Las Lajas, Las Cumbres, Panamá')}<br/>"
            f"Tel: {empresa.get('telefono', '6342-9218')} | Email: {empresa.get('email', 'tus_amigos@copypoint.online')}",
            self.styles['CompanyInfo']
        )
        story.append(company_details)
        story.append(Spacer(1, 0.3*inch))
        
        # Título del ticket
        ticket_title = Paragraph(
            f"<b>{template_data.get('title', 'Ticket de Entrada')}</b>",
            self.styles['CorporateSubtitle']
        )
        story.append(ticket_title)
        story.append(Spacer(1, 0.2*inch))
    
    def _add_ticket_info(self, story: List, ticket_info: Dict[str, Any]) -> None:
        """
        Agregar información básica del ticket.
        
        Args:
            story: Lista de elementos del documento
            ticket_info: Información del ticket
        """
        # Crear tabla con información del ticket
        info_data = [
            ['Número de Ticket:', str(ticket_info.get('numero', 'N/A'))],
            ['Tipo:', str(ticket_info.get('tipo', 'ENTRADA'))],
            ['Fecha y Hora:', str(ticket_info.get('fecha', 'No especificada'))],
            ['Responsable:', str(ticket_info.get('responsable', 'No especificado'))]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [self.colors['white'], self.colors['light_gray']]),
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['dark_gray']),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.2*inch))
    
    def _add_ticket_products_table(self, story: List, productos: List[Dict[str, Any]]) -> None:
        """
        Agregar tabla de productos al ticket.
        
        Args:
            story: Lista de elementos del documento
            productos: Lista de productos
        """
        # Título de productos
        products_title = Paragraph(
            "<b>PRODUCTOS</b>",
            self.styles['CorporateSubtitle']
        )
        story.append(products_title)
        
        # Preparar datos para la tabla
        headers = ['Código', 'Nombre del Producto', 'Cantidad', 'Observaciones']
        table_data = [headers]
        
        for producto in productos:
            row = [
                str(producto.get('codigo', 'N/A')),
                str(producto.get('nombre', 'Producto sin nombre')),
                str(producto.get('cantidad', 0)),
                str(producto.get('observaciones', ''))[:30] + ('...' if len(str(producto.get('observaciones', ''))) > 30 else '')
            ]
            table_data.append(row)
        
        # Crear tabla
        products_table = Table(table_data, colWidths=[1*inch, 2.5*inch, 0.8*inch, 1.7*inch])
        
        # Aplicar estilo
        products_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Código
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Nombre
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Cantidad
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),    # Observaciones
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.colors['white'], self.colors['light_gray']]),
            
            # Borders
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['dark_gray']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(products_table)
        story.append(Spacer(1, 0.2*inch))
    
    def _add_ticket_summary(self, story: List, resumen: Dict[str, Any]) -> None:
        """
        Agregar resumen del ticket.
        
        Args:
            story: Lista de elementos del documento
            resumen: Datos de resumen
        """
        # Título de resumen
        summary_title = Paragraph(
            "<b>RESUMEN</b>",
            self.styles['CorporateSubtitle']
        )
        story.append(summary_title)
        
        # Datos del resumen
        summary_data = [
            ['Total de Productos:', str(resumen.get('total_productos', 0))],
            ['Cantidad Total:', str(resumen.get('total_cantidad', 0))]
        ]
        
        # Agregar observaciones si existen
        if resumen.get('observaciones_generales'):
            summary_data.append(['Observaciones:', str(resumen['observaciones_generales'])])
        
        summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), self.colors['light_gray']),
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['dark_gray']),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
    
    def _add_ticket_footer(self, story: List, template_data: Dict[str, Any]) -> None:
        """
        Agregar footer del ticket.
        
        Args:
            story: Lista de elementos del documento
            template_data: Datos del template
        """
        # Línea de separación
        story.append(Spacer(1, 0.2*inch))
        
        # Nota del sistema
        footer_note = Paragraph(
            "<i>Este ticket fue generado automáticamente por el Sistema de Gestión de Inventario.</i>",
            self.styles['CompanyInfo']
        )
        story.append(footer_note)
        
        # Fecha de generación
        generation_info = Paragraph(
            f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}",
            self.styles['CompanyInfo']
        )
        story.append(generation_info)
    
    def _create_ticket_page_header(self, canvas, doc) -> None:
        """
        Crear header de página para tickets (más simple que reportes).
        
        Args:
            canvas: Canvas de ReportLab
            doc: Documento
        """
        canvas.saveState()
        
        # Línea superior más fina para tickets
        canvas.setStrokeColor(self.colors['secondary'])
        canvas.setLineWidth(1)
        canvas.line(doc.leftMargin, doc.height + doc.topMargin - 10,
                   doc.width + doc.leftMargin, doc.height + doc.topMargin - 10)
        
        # Número de página en footer (más discreto para tickets)
        page_num = canvas.getPageNumber()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(self.colors['dark_gray'])
        canvas.drawRightString(
            doc.width + doc.leftMargin,
            doc.bottomMargin - 15,
            f"Página {page_num}"
        )
        
        canvas.restoreState()

    def get_page_size_options(self) -> Dict[str, Tuple[float, float]]:
        """
        Obtener opciones de tamaño de página disponibles.
        
        Returns:
            Dict[str, Tuple[float, float]]: Opciones de tamaño
        """
        return {
            'A4': A4,
            'Letter': letter
        }
    
    def set_page_size(self, size_name: str) -> None:
        """
        Establecer tamaño de página.
        
        Args:
            size_name: Nombre del tamaño ('A4' o 'Letter')
        
        Raises:
            ValueError: Si el tamaño no es soportado
        """
        sizes = self.get_page_size_options()
        if size_name not in sizes:
            raise ValueError(f"Tamaño '{size_name}' no soportado. Opciones: {list(sizes.keys())}")
        
        self.page_config['pagesize'] = sizes[size_name]
        logger.debug(f"Tamaño de página cambiado a: {size_name}")
