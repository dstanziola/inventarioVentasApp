"""
Servicio para generación de etiquetas y códigos de barras - FASE 3 Optimizado.

Este módulo proporciona funcionalidades completas para:
- Generación de imágenes de códigos de barras
- Creación de etiquetas de productos
- Generación de PDFs con múltiples etiquetas
- Gestión de templates de etiquetas
- Funcionalidades de impresión

PATRÓN FASE 3:
- DatabaseHelper: Operaciones BD optimizadas
- ValidationHelper: Validaciones robustas
- LoggingHelper: Auditoría estructurada

Autor: Sistema de Inventario Copy Point S.A.
Fecha: Junio 2025
"""

import os
import tempfile
import time
from decimal import Decimal
from io import BytesIO
from typing import List, Dict, Optional, Union, Tuple
import json
import threading
from pathlib import Path

# Importaciones de librerías externas
try:
    import barcode
    from barcode.writer import ImageWriter
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm, inch
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.graphics.barcode import code128
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    print(f"Error importando dependencias: {e}")
    raise

# Importaciones del sistema - FASE 3 Pattern
from models.producto import Producto
from models.categoria import Categoria
from helpers.database_helper import DatabaseHelper
from helpers.validation_helper import ValidationHelper
from helpers.logging_helper import LoggingHelper


class LabelService:
    """
    Servicio para generación de etiquetas y códigos de barras - FASE 3 Optimizado.
    
    PATRÓN FASE 3:
    - DatabaseHelper para operaciones BD optimizadas
    - ValidationHelper para validaciones robustas
    - LoggingHelper para logging estructurado y auditoría
    """
    
    # Templates predefinidos
    DEFAULT_TEMPLATES = {
        'avery_5160': {
            'id': 'avery_5160',
            'name': 'Avery 5160',
            'description': '30 etiquetas por página (2.625" x 1")',
            'labels_per_page': 30,
            'label_width': 66.675,  # mm
            'label_height': 25.4,   # mm
            'page_width': 215.9,    # mm (carta)
            'page_height': 279.4,   # mm
            'top_margin': 12.7,
            'left_margin': 5.5,
            'columns': 3,
            'rows': 10,
            'h_spacing': 3.2,
            'v_spacing': 0
        },
        'avery_5163': {
            'id': 'avery_5163',
            'name': 'Avery 5163',
            'description': '10 etiquetas por página (2" x 4")',
            'labels_per_page': 10,
            'label_width': 101.6,   # mm
            'label_height': 50.8,   # mm
            'page_width': 215.9,    # mm
            'page_height': 279.4,   # mm
            'top_margin': 12.7,
            'left_margin': 5.5,
            'columns': 2,
            'rows': 5,
            'h_spacing': 3.2,
            'v_spacing': 0
        },
        'a4_standard': {
            'id': 'a4_standard',
            'name': 'A4 Standard',
            'description': '21 etiquetas por página (70mm x 40mm)',
            'labels_per_page': 21,
            'label_width': 70,      # mm
            'label_height': 40,     # mm
            'page_width': 210,      # mm (A4)
            'page_height': 297,     # mm
            'top_margin': 15,
            'left_margin': 5,
            'columns': 3,
            'rows': 7,
            'h_spacing': 0,
            'v_spacing': 2.5
        },
        'thermal_80mm': {
            'id': 'thermal_80mm',
            'name': 'Térmica 80mm',
            'description': 'Rollo continuo para impresoras térmicas',
            'labels_per_page': 1,
            'label_width': 80,      # mm
            'label_height': 50,     # mm
            'page_width': 80,       # mm
            'page_height': 50,      # mm
            'top_margin': 2,
            'left_margin': 2,
            'columns': 1,
            'rows': 1,
            'h_spacing': 0,
            'v_spacing': 0
        }
    }
    
    # Formatos de códigos soportados
    SUPPORTED_FORMATS = [
        'Code128', 'Code39', 'EAN13', 'EAN8', 'UPC', 'UPCA'
    ]
    
    def __init__(self, db_connection, product_service=None):
        """
        Inicializar el servicio de etiquetas con patrón FASE 3.
        
        Args:
            db_connection: Conexión a base de datos
            product_service: Servicio de productos (opcional)
        """
        # FASE 3 Components
        self.db_connection = db_connection
        self.db_helper = DatabaseHelper(db_connection)
        self.validator = ValidationHelper()
        self.logger = LoggingHelper.get_service_logger('label_service')
        
        # Servicios relacionados
        self.product_service = product_service
        if not product_service:
            # Import dinámico para evitar circular import
            try:
                from services.product_service import ProductService
                self.product_service = ProductService(db_connection)
            except ImportError:
                self.logger.warning("ProductService no disponible para LabelService")
        
        # Configuración interna
        self.templates = self.DEFAULT_TEMPLATES.copy()
        self.custom_templates_file = 'config/custom_templates.json'
        self._lock = threading.Lock()
        self._product_cache = {}  # Cache para productos frecuentes
        self._cache_max_size = 100
        self._cache_expiry = 300  # 5 minutos
        
        # Cargar templates personalizados si existen
        self._load_custom_templates()
        
        self.logger.info("LabelService inicializado correctamente con patrón FASE 3")
    
    def validate_barcode(self, barcode: str) -> bool:
        """
        Validar formato de código de barras usando ValidationHelper.
        
        Args:
            barcode: Código de barras a validar
            
        Returns:
            bool: True si el código es válido
        """
        try:
            return self.validator.validate_barcode_format(barcode)
        except Exception as e:
            self.logger.error(f"Error validando código de barras: {e}")
            return False
    
    def format_barcode(self, barcode: str) -> str:
        """
        Formatear código de barras usando ValidationHelper.
        
        Args:
            barcode: Código de barras a formatear
            
        Returns:
            str: Código de barras formateado
        """
        try:
            return self.validator.sanitize_string(barcode).upper()
        except Exception as e:
            self.logger.error(f"Error formateando código de barras: {e}")
            return ""
    
    def search_product_by_code(self, code: str) -> Optional[Producto]:
        """
        Buscar producto por código con cache optimizado.
        
        Args:
            code: Código del producto a buscar
            
        Returns:
            Optional[Producto]: Producto encontrado o None
        """
        start_time = time.time()
        
        try:
            # Validar y formatear código
            if not self.validate_barcode(code):
                self.logger.warning(f"Código de barras inválido: {code}")
                return None
            
            formatted_code = self.format_barcode(code)
            
            # Verificar cache primero
            cached_product = self._get_from_cache(formatted_code)
            if cached_product:
                duration = time.time() - start_time
                self.logger.debug(f"Producto {formatted_code} encontrado en cache, búsqueda completada en {duration:.4f}s")
                return cached_product
            
            # Buscar en base de datos
            product = self.product_service.get_product_by_id(int(formatted_code))
            
            if product:
                # Agregar a cache
                self._add_to_cache(formatted_code, product)
                duration = time.time() - start_time
                self.logger.info(f"Producto {formatted_code} encontrado en BD, búsqueda completada en {duration:.4f}s")
                return product
            else:
                duration = time.time() - start_time
                self.logger.info(f"Producto {formatted_code} no encontrado, búsqueda completada en {duration:.4f}s")
                return None
                
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Error buscando producto por código {code}: {e}")
            return None
    
    def generate_barcode_image(self, 
                              code: str, 
                              format: str = 'Code128',
                              width: int = 150,
                              height: int = 50,
                              font_size: int = 10,
                              text_below: bool = True) -> bytes:
        """
        Generar imagen de código de barras con validación FASE 3.
        
        Args:
            code: Código a generar
            format: Formato del código (Code128, EAN13, etc.)
            width: Ancho en píxeles
            height: Alto en píxeles
            font_size: Tamaño de fuente para texto
            text_below: Si mostrar texto debajo del código
            
        Returns:
            bytes: Imagen del código en formato PNG
            
        Raises:
            ValueError: Si el código o formato son inválidos
        """
        start_time = time.time()
        
        try:
            # Validación usando ValidationHelper
            if not self.validator.validate_non_empty_string(code):
                raise ValueError("El código no puede estar vacío")
            
            if format not in self.SUPPORTED_FORMATS:
                raise ValueError(f"Formato {format} no soportado. Usar: {self.SUPPORTED_FORMATS}")
            
            # Convertir código a string y limpiar
            code_str = self.validator.sanitize_string(str(code))
            
            # Validar según el formato
            if format == 'EAN13' and len(code_str) != 13:
                raise ValueError("EAN13 requiere exactamente 13 dígitos")
            elif format == 'EAN8' and len(code_str) != 8:
                raise ValueError("EAN8 requiere exactamente 8 dígitos")
            
            # Generar código de barras
            barcode_class = getattr(barcode, format.lower())
            
            # Configurar writer con opciones
            writer = ImageWriter()
            writer.set_options({
                'module_width': 0.2,
                'module_height': height / 2.0,
                'font_size': font_size,
                'text_distance': 5,
                'quiet_zone': 6
            })
            
            # Generar código
            barcode_obj = barcode_class(code_str, writer=writer)
            
            # Crear imagen en memoria
            buffer = BytesIO()
            barcode_obj.write(buffer, {
                'format': 'PNG',
                'write_text': text_below
            })
            
            # Redimensionar si es necesario
            buffer.seek(0)
            image = Image.open(buffer)
            
            if image.size[0] != width or image.size[1] != height:
                image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Convertir a bytes
            output_buffer = BytesIO()
            image.save(output_buffer, format='PNG')
            
            duration = time.time() - start_time
            self.logger.debug(f"Código de barras generado: {format} - {code_str}, completado en {duration:.4f}s")
            return output_buffer.getvalue()
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Error generando código de barras: {e}")
            raise
    
    def create_product_label(self, 
                           product: Producto,
                           format: str = 'standard',
                           include_category: bool = False,
                           include_price: bool = True,
                           include_barcode: bool = True) -> bytes:
        """
        Crear etiqueta de producto con logging estructurado.
        
        Args:
            product: Producto para generar etiqueta
            format: Formato de etiqueta (standard, mini, detailed)
            include_category: Si incluir información de categoría
            include_price: Si incluir precio
            include_barcode: Si incluir código de barras
            
        Returns:
            bytes: Imagen de la etiqueta en formato PNG
            
        Raises:
            ValueError: Si el producto es inválido
        """
        start_time = time.time()
        
        try:
            # Validar producto usando ValidationHelper
            if not product or product is None:
                raise ValueError("El producto no puede ser None")
            
            if not self.validator.validate_positive_integer(product.id_producto):
                raise ValueError("El producto debe tener un ID válido")
            
            if not self.validator.validate_non_empty_string(product.nombre, 1):
                raise ValueError("El producto debe tener un nombre válido")
            
            self.logger.info(f"Iniciando creación de etiqueta para producto {product.id_producto}")
            
            # Obtener categoría si se solicita
            category = None
            if include_category and product.id_categoria:
                try:
                    # Usar DatabaseHelper para consulta optimizada
                    category_data = self.db_helper.safe_execute(
                        "SELECT * FROM categorias WHERE id_categoria = ?",
                        (product.id_categoria,)
                    )
                    if category_data:
                        from models.categoria import Categoria
                        category = Categoria(**category_data)
                except Exception as e:
                    self.logger.warning(f"No se pudo obtener categoría {product.id_categoria}: {e}")
            
            # Configurar dimensiones según formato
            if format == 'mini':
                width, height = 200, 120
                font_sizes = {'title': 12, 'detail': 8, 'price': 10}
            elif format == 'detailed':
                width, height = 400, 250
                font_sizes = {'title': 16, 'detail': 12, 'price': 14}
            else:  # standard
                width, height = 300, 180
                font_sizes = {'title': 14, 'detail': 10, 'price': 12}
            
            # Crear imagen
            image = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(image)
            
            # Intentar cargar fuentes
            try:
                font_title = ImageFont.truetype("arial.ttf", font_sizes['title'])
                font_detail = ImageFont.truetype("arial.ttf", font_sizes['detail'])
                font_price = ImageFont.truetype("arialbd.ttf", font_sizes['price'])
            except:
                # Usar fuente por defecto si no se encuentran las TTF
                font_title = ImageFont.load_default()
                font_detail = ImageFont.load_default()
                font_price = ImageFont.load_default()
            
            # Calcular posiciones
            y_pos = 10
            x_margin = 10
            
            # Título del producto
            product_name = product.nombre[:30] + "..." if len(product.nombre) > 30 else product.nombre
            draw.text((x_margin, y_pos), product_name, fill='black', font=font_title)
            y_pos += font_sizes['title'] + 5
            
            # Información de categoría
            if include_category and category:
                category_text = f"Categoría: {category.nombre}"
                draw.text((x_margin, y_pos), category_text, fill='gray', font=font_detail)
                y_pos += font_sizes['detail'] + 3
            
            # ID del producto
            id_text = f"ID: {product.id_producto}"
            draw.text((x_margin, y_pos), id_text, fill='gray', font=font_detail)
            y_pos += font_sizes['detail'] + 5
            
            # Precio
            if include_price and product.precio:
                price_text = f"Precio: B/. {product.precio:.2f}"
                draw.text((x_margin, y_pos), price_text, fill='darkgreen', font=font_price)
                y_pos += font_sizes['price'] + 8
            
            # Código de barras
            if include_barcode:
                try:
                    barcode_width = width - (x_margin * 2)
                    barcode_height = 40 if format != 'mini' else 25
                    
                    barcode_image_data = self.generate_barcode_image(
                        str(product.id_producto),
                        width=barcode_width,
                        height=barcode_height,
                        font_size=8 if format == 'mini' else 10
                    )
                    
                    # Pegar código de barras
                    barcode_buffer = BytesIO(barcode_image_data)
                    barcode_img = Image.open(barcode_buffer)
                    
                    # Calcular posición centrada
                    barcode_x = (width - barcode_img.width) // 2
                    barcode_y = height - barcode_img.height - 10
                    
                    image.paste(barcode_img, (barcode_x, barcode_y))
                    
                except Exception as e:
                    self.logger.warning(f"No se pudo generar código de barras para producto {product.id_producto}: {e}")
            
            # Convertir a bytes
            output_buffer = BytesIO()
            image.save(output_buffer, format='PNG')
            
            duration = time.time() - start_time
            self.logger.info(f"Etiqueta creada para producto {product.id_producto}, completada en {duration:.4f}s")
            return output_buffer.getvalue()
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Error creando etiqueta de producto: {e}")
            raise
    
    def generate_labels_pdf(self, 
                          products: Union[List[Producto], List[Dict]],
                          template: str = 'a4_standard',
                          use_quantities: bool = False,
                          label_format: str = 'standard') -> bytes:
        """
        Generar PDF con múltiples etiquetas.
        
        Args:
            products: Lista de productos o diccionarios con producto y cantidad
            template: Template a usar
            use_quantities: Si usar cantidades específicas
            label_format: Formato de etiquetas individuales
            
        Returns:
            bytes: PDF con las etiquetas
            
        Raises:
            ValueError: Si el template no existe o productos inválidos
        """
        start_time = time.time()
        
        try:
            # Validar template
            if template not in self.templates:
                raise ValueError(f"Template '{template}' no encontrado")
            
            template_data = self.templates[template]
            
            # Validar productos
            if not products:
                raise ValueError("La lista de productos no puede estar vacía")
            
            self.logger.info(f"Generando PDF con {len(products)} productos usando template {template}")
            
            # Preparar lista de etiquetas a generar
            labels_to_generate = []
            
            for item in products:
                if use_quantities and isinstance(item, dict):
                    product = item['product']
                    quantity = item.get('quantity', 1)
                else:
                    product = item
                    quantity = 1
                
                # Agregar etiquetas según cantidad
                for _ in range(quantity):
                    labels_to_generate.append(product)
            
            # Crear PDF
            pdf_buffer = BytesIO()
            
            # Configurar página
            page_width = template_data['page_width'] * mm
            page_height = template_data['page_height'] * mm
            
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=(page_width, page_height),
                topMargin=template_data['top_margin'] * mm,
                leftMargin=template_data['left_margin'] * mm,
                rightMargin=5 * mm,
                bottomMargin=5 * mm
            )
            
            # Calcular posiciones
            positions = self._calculate_label_positions(template_data)
            
            # Crear canvas para dibujo directo
            canvas_pdf = canvas.Canvas(pdf_buffer, pagesize=(page_width, page_height))
            
            labels_per_page = template_data['labels_per_page']
            current_page = 0
            
            for i, product in enumerate(labels_to_generate):
                position_index = i % labels_per_page
                
                # Nueva página si es necesario
                if position_index == 0 and i > 0:
                    canvas_pdf.showPage()
                    current_page += 1
                
                # Obtener posición
                pos = positions[position_index]
                
                # Generar etiqueta individual
                try:
                    label_image_data = self.create_product_label(
                        product, 
                        format=label_format
                    )
                    
                    # Crear archivo temporal para la imagen
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                        tmp_file.write(label_image_data)
                        tmp_path = tmp_file.name
                    
                    # Dibujar imagen en PDF
                    canvas_pdf.drawImage(
                        tmp_path,
                        pos['x'] * mm,
                        (template_data['page_height'] - pos['y'] - pos['height']) * mm,
                        width=pos['width'] * mm,
                        height=pos['height'] * mm,
                        preserveAspectRatio=True
                    )
                    
                    # Limpiar archivo temporal
                    os.unlink(tmp_path)
                    
                except Exception as e:
                    self.logger.warning(f"Error generando etiqueta para producto {product.id_producto}: {e}")
                    
                    # Dibujar marco de error
                    canvas_pdf.setStrokeColor(colors.red)
                    canvas_pdf.rect(
                        pos['x'] * mm,
                        (template_data['page_height'] - pos['y'] - pos['height']) * mm,
                        pos['width'] * mm,
                        pos['height'] * mm
                    )
                    
                    # Texto de error
                    canvas_pdf.setFillColor(colors.red)
                    canvas_pdf.drawString(
                        (pos['x'] + 5) * mm,
                        (template_data['page_height'] - pos['y'] - pos['height']/2) * mm,
                        "ERROR"
                    )
            
            # Finalizar PDF
            canvas_pdf.save()
            
            duration = time.time() - start_time
            self.logger.info(f"PDF generado con {len(labels_to_generate)} etiquetas, completado en {duration:.4f}s")
            return pdf_buffer.getvalue()
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Error generando PDF de etiquetas: {e}")
            raise
    
    def get_available_templates(self) -> List[Dict]:
        """
        Obtener lista de templates disponibles.
        
        Returns:
            List[Dict]: Lista de templates con su información
        """
        templates_list = []
        
        for template_id, template_data in self.templates.items():
            templates_list.append({
                'id': template_id,
                'name': template_data['name'],
                'description': template_data['description'],
                'labels_per_page': template_data['labels_per_page'],
                'page_size': f"{template_data['page_width']}x{template_data['page_height']}mm"
            })
        
        return templates_list
    
    def _cleanup_cache_if_needed(self):
        """Limpiar cache si es necesario."""
        if len(self._product_cache) > self._cache_max_size:
            # Remover entradas más antiguas
            current_time = time.time()
            items_to_remove = []
            
            for code, (product, timestamp) in self._product_cache.items():
                if current_time - timestamp > self._cache_expiry:
                    items_to_remove.append(code)
            
            for code in items_to_remove:
                del self._product_cache[code]
            
            self.logger.debug(f"Cache limpiado: {len(items_to_remove)} entradas removidas")
    
    def _get_from_cache(self, code: str) -> Optional[Producto]:
        """Obtener producto del cache."""
        if code in self._product_cache:
            product, timestamp = self._product_cache[code]
            if time.time() - timestamp < self._cache_expiry:
                return product
            else:
                del self._product_cache[code]
        return None
    
    def _add_to_cache(self, code: str, product: Producto):
        """Agregar producto al cache."""
        self._cleanup_cache_if_needed()
        self._product_cache[code] = (product, time.time())
    
    def _calculate_label_positions(self, template_data: Dict) -> List[Dict]:
        """
        Calcular posiciones de etiquetas en la página.
        
        Args:
            template_data: Datos del template
            
        Returns:
            List[Dict]: Lista de posiciones con x, y, width, height
        """
        positions = []
        
        cols = template_data['columns']
        rows = template_data['rows']
        
        label_width = template_data['label_width']
        label_height = template_data['label_height']
        
        top_margin = template_data['top_margin']
        left_margin = template_data['left_margin']
        
        h_spacing = template_data.get('h_spacing', 0)
        v_spacing = template_data.get('v_spacing', 0)
        
        for row in range(rows):
            for col in range(cols):
                x = left_margin + col * (label_width + h_spacing)
                y = top_margin + row * (label_height + v_spacing)
                
                positions.append({
                    'x': x,
                    'y': y,
                    'width': label_width,
                    'height': label_height
                })
        
        return positions
    
    def _load_custom_templates(self):
        """Cargar templates personalizados desde archivo."""
        try:
            if os.path.exists(self.custom_templates_file):
                with open(self.custom_templates_file, 'r', encoding='utf-8') as f:
                    custom_templates = json.load(f)
                    self.templates.update(custom_templates)
                    self.logger.info(f"Cargados {len(custom_templates)} templates personalizados")
        except Exception as e:
            self.logger.warning(f"No se pudieron cargar templates personalizados: {e}")


# Función de compatibilidad hacia atrás
def get_label_service() -> LabelService:
    """
    Obtener instancia del servicio de etiquetas (función de compatibilidad).
    
    Returns:
        LabelService: Nueva instancia del servicio
    """
    # Crear conexión mock para compatibilidad
    class MockDBConnection:
        def get_connection(self):
            return None
    
    return LabelService(MockDBConnection())
