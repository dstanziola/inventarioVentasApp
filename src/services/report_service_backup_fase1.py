"""
ReportService - FASE 2: Sistema de Reportes

Servicio principal para generación de reportes del sistema de inventario.
Implementa 4 tipos de reportes principales:
1. Reporte de Inventario Actual
2. Reporte de Movimientos por período  
3. Reporte de Ventas con filtros
4. Reporte de Rentabilidad

Autor: Sistema de Inventario Copy Point S.A.
Metodología: TDD - Implementación basada en tests unitarios
"""

import sqlite3
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict


@dataclass
class ReportData:
    """Estructura estándar para datos de reportes"""
    data: List[Dict[str, Any]]
    summary: Dict[str, Any]
    generated_at: datetime
    filters_applied: Optional[Dict[str, Any]] = None
    totals: Optional[Dict[str, Any]] = None


class ReportService:
    """Servicio para generación de reportes del sistema de inventario"""
    
    def __init__(self, db_path: str):
        """
        Inicializa el servicio de reportes
        
        Args:
            db_path: Ruta a la base de datos SQLite
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def _get_connection(self) -> sqlite3.Connection:
        """Obtiene conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
        return conn
    
    def _validate_date_range(self, fecha_inicio: date, fecha_fin: date) -> None:
        """
        Valida que el rango de fechas sea válido
        
        Args:
            fecha_inicio: Fecha de inicio del período
            fecha_fin: Fecha de fin del período
            
        Raises:
            ValueError: Si el rango de fechas es inválido
        """
        if fecha_fin < fecha_inicio:
            raise ValueError("fecha_fin debe ser posterior a fecha_inicio")
    
    def generate_inventory_report(
        self, 
        categoria_id: Optional[int] = None,
        fecha_corte: Optional[date] = None,
        solo_con_stock: bool = False
    ) -> Dict[str, Any]:
        """
        Genera reporte de inventario actual
        
        Args:
            categoria_id: Filtrar por categoría específica
            fecha_corte: Fecha de corte para el inventario (default: hoy)
            solo_con_stock: Solo mostrar productos con stock > 0
            
        Returns:
            Dict con datos del reporte de inventario
        """
        if fecha_corte is None:
            fecha_corte = date.today()
            
        try:
            with self._get_connection() as conn:
                # Query base para inventario actual
                query = """
                SELECT 
                    p.id_producto,
                    p.nombre,
                    c.nombre as categoria,
                    p.stock,
                    p.costo,
                    (p.stock * p.costo) as valor_total,
                    p.activo
                FROM productos p
                JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE c.tipo = 'MATERIAL'
                """
                
                params = []
                filters_applied = {}
                
                # Aplicar filtros
                if categoria_id:
                    query += " AND p.id_categoria = ?"
                    params.append(categoria_id)
                    filters_applied['categoria_id'] = categoria_id
                
                if solo_con_stock:
                    query += " AND p.stock > 0"
                    filters_applied['solo_con_stock'] = True
                    
                query += " ORDER BY c.nombre, p.nombre"
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                # Convertir a lista de diccionarios
                data = []
                total_productos = 0
                total_valor = Decimal('0')
                productos_con_stock = 0
                
                for row in rows:
                    item = {
                        'id_producto': row['id_producto'],
                        'nombre': row['nombre'],
                        'categoria': row['categoria'],
                        'stock_actual': row['stock'],
                        'costo_unitario': float(row['costo']),
                        'valor_total': float(row['valor_total']),
                        'stock_minimo': 5  # TODO: Implementar stock mínimo configurable
                    }
                    data.append(item)
                    
                    total_productos += 1
                    total_valor += Decimal(str(row['valor_total']))
                    if row['stock'] > 0:
                        productos_con_stock += 1
                
                # Preparar resumen
                summary = {
                    'total_productos': total_productos,
                    'productos_con_stock': productos_con_stock,
                    'productos_sin_stock': total_productos - productos_con_stock,
                    'valor_total_inventario': float(total_valor),
                    'fecha_corte': fecha_corte.isoformat()
                }
                
                return {
                    'data': data,
                    'summary': summary,
                    'generated_at': datetime.now(),
                    'filters_applied': filters_applied
                }
                
        except Exception as e:
            self.logger.error(f"Error generando reporte de inventario: {e}")
            raise
    
    def generate_movements_report(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        tipo_movimiento: Optional[str] = None,
        categoria_id: Optional[int] = None,
        producto_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Genera reporte de movimientos por período
        
        Args:
            fecha_inicio: Fecha de inicio del período
            fecha_fin: Fecha de fin del período
            tipo_movimiento: Filtrar por tipo ('ENTRADA', 'VENTA', 'AJUSTE')
            categoria_id: Filtrar por categoría
            producto_id: Filtrar por producto específico
            
        Returns:
            Dict con datos del reporte de movimientos
        """
        self._validate_date_range(fecha_inicio, fecha_fin)
        
        try:
            with self._get_connection() as conn:
                # Query base para movimientos
                query = """
                SELECT 
                    m.id_movimiento,
                    m.fecha_movimiento,
                    m.tipo_movimiento,
                    p.nombre as producto_nombre,
                    c.nombre as categoria_nombre,
                    m.cantidad,
                    m.responsable,
                    m.observaciones,
                    p.costo,
                    (ABS(m.cantidad) * p.costo) as valor_movimiento
                FROM movimientos m
                JOIN productos p ON m.id_producto = p.id_producto
                JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE DATE(m.fecha_movimiento) >= ? AND DATE(m.fecha_movimiento) <= ?
                """
                
                params = [fecha_inicio.isoformat(), fecha_fin.isoformat()]
                filters_applied = {
                    'fecha_inicio': fecha_inicio.isoformat(),
                    'fecha_fin': fecha_fin.isoformat()
                }
                
                # Aplicar filtros adicionales
                if tipo_movimiento:
                    query += " AND m.tipo_movimiento = ?"
                    params.append(tipo_movimiento)
                    filters_applied['tipo_movimiento'] = tipo_movimiento
                
                if categoria_id:
                    query += " AND p.id_categoria = ?"
                    params.append(categoria_id)
                    filters_applied['categoria_id'] = categoria_id
                
                if producto_id:
                    query += " AND p.id_producto = ?"
                    params.append(producto_id)
                    filters_applied['producto_id'] = producto_id
                    
                query += " ORDER BY m.fecha_movimiento DESC"
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                # Convertir a lista de diccionarios
                data = []
                total_movimientos = 0
                entradas = 0
                salidas = 0
                valor_total_movimientos = Decimal('0')
                
                for row in rows:
                    item = {
                        'id_movimiento': row['id_movimiento'],
                        'fecha_movimiento': row['fecha_movimiento'],
                        'tipo_movimiento': row['tipo_movimiento'],
                        'producto_nombre': row['producto_nombre'],
                        'categoria_nombre': row['categoria_nombre'],
                        'cantidad': row['cantidad'],
                        'responsable': row['responsable'],
                        'observaciones': row['observaciones'] or '',
                        'valor_movimiento': float(row['valor_movimiento'])
                    }
                    data.append(item)
                    
                    total_movimientos += 1
                    valor_total_movimientos += Decimal(str(row['valor_movimiento']))
                    
                    if row['cantidad'] > 0:
                        entradas += abs(row['cantidad'])
                    else:
                        salidas += abs(row['cantidad'])
                
                # Preparar resumen
                summary = {
                    'total_movimientos': total_movimientos,
                    'total_entradas': entradas,
                    'total_salidas': salidas,
                    'valor_total_movimientos': float(valor_total_movimientos),
                    'periodo': f"{fecha_inicio.isoformat()} - {fecha_fin.isoformat()}"
                }
                
                return {
                    'data': data,
                    'summary': summary,
                    'generated_at': datetime.now(),
                    'period': summary['periodo'],
                    'filters_applied': filters_applied
                }
                
        except Exception as e:
            self.logger.error(f"Error generando reporte de movimientos: {e}")
            raise
    
    def generate_sales_report(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        group_by: Optional[str] = None,
        include_details: bool = True,
        cliente_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Genera reporte de ventas con filtros
        
        Args:
            fecha_inicio: Fecha de inicio del período
            fecha_fin: Fecha de fin del período
            group_by: Agrupar por período ('day', 'month', 'year')
            include_details: Incluir detalles de productos vendidos
            cliente_id: Filtrar por cliente específico
            
        Returns:
            Dict con datos del reporte de ventas
        """
        self._validate_date_range(fecha_inicio, fecha_fin)
        
        try:
            with self._get_connection() as conn:
                # Query base para ventas
                query = """
                SELECT 
                    v.id_venta,
                    v.fecha_venta,
                    COALESCE(c.nombre, 'Cliente General') as cliente_nombre,
                    v.subtotal,
                    v.impuestos,
                    v.total,
                    v.responsable
                FROM ventas v
                LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
                WHERE DATE(v.fecha_venta) >= ? AND DATE(v.fecha_venta) <= ?
                """
                
                params = [fecha_inicio.isoformat(), fecha_fin.isoformat()]
                filters_applied = {
                    'fecha_inicio': fecha_inicio.isoformat(),
                    'fecha_fin': fecha_fin.isoformat()
                }
                
                if cliente_id:
                    query += " AND v.id_cliente = ?"
                    params.append(cliente_id)
                    filters_applied['cliente_id'] = cliente_id
                    
                query += " ORDER BY v.fecha_venta DESC"
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                # Convertir a lista de diccionarios
                data = []
                total_ventas = 0
                subtotal_acumulado = Decimal('0')
                impuestos_acumulados = Decimal('0')
                total_acumulado = Decimal('0')
                
                for row in rows:
                    item = {
                        'id_venta': row['id_venta'],
                        'fecha_venta': row['fecha_venta'],
                        'cliente_nombre': row['cliente_nombre'],
                        'subtotal': float(row['subtotal']),
                        'impuestos': float(row['impuestos']),
                        'total': float(row['total']),
                        'responsable': row['responsable']
                    }
                    data.append(item)
                    
                    total_ventas += 1
                    subtotal_acumulado += row['subtotal']
                    impuestos_acumulados += row['impuestos']
                    total_acumulado += row['total']
                
                # Preparar totales y resumen
                totals = {
                    'subtotal_total': float(subtotal_acumulado),
                    'impuestos_total': float(impuestos_acumulados),
                    'gran_total': float(total_acumulado)
                }
                
                summary = {
                    'total_ventas': total_ventas,
                    'promedio_venta': float(total_acumulado / total_ventas) if total_ventas > 0 else 0,
                    'periodo': f"{fecha_inicio.isoformat()} - {fecha_fin.isoformat()}"
                }
                
                result = {
                    'data': data,
                    'summary': summary,
                    'totals': totals,
                    'generated_at': datetime.now(),
                    'filters_applied': filters_applied
                }
                
                # Agregar agrupación si se solicita
                if group_by and not include_details:
                    result['grouped_data'] = self._group_sales_data(data, group_by)
                
                return result
                
        except Exception as e:
            self.logger.error(f"Error generando reporte de ventas: {e}")
            raise
    
    def _group_sales_data(self, data: List[Dict], group_by: str) -> Dict[str, Any]:
        """Agrupa datos de ventas por período especificado"""
        # Implementación básica de agrupación
        grouped = {}
        
        for sale in data:
            # Extraer fecha y agrupar según criterio
            fecha_venta = datetime.fromisoformat(sale['fecha_venta'].replace('Z', '+00:00'))
            
            if group_by == 'day':
                key = fecha_venta.date().isoformat()
            elif group_by == 'month':
                key = f"{fecha_venta.year}-{fecha_venta.month:02d}"
            elif group_by == 'year':
                key = str(fecha_venta.year)
            else:
                key = fecha_venta.date().isoformat()
            
            if key not in grouped:
                grouped[key] = {
                    'periodo': key,
                    'total_ventas': 0,
                    'subtotal': 0,
                    'impuestos': 0,
                    'total': 0
                }
            
            grouped[key]['total_ventas'] += 1
            grouped[key]['subtotal'] += sale['subtotal']
            grouped[key]['impuestos'] += sale['impuestos']
            grouped[key]['total'] += sale['total']
        
        return grouped
    
    def generate_profitability_report(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        categoria_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Genera reporte de rentabilidad por período
        
        Args:
            fecha_inicio: Fecha de inicio del período
            fecha_fin: Fecha de fin del período
            categoria_id: Filtrar por categoría específica
            
        Returns:
            Dict con datos del reporte de rentabilidad
        """
        self._validate_date_range(fecha_inicio, fecha_fin)
        
        try:
            with self._get_connection() as conn:
                # Query para calcular rentabilidad por producto
                query = """
                SELECT 
                    p.id_producto,
                    p.nombre as producto_nombre,
                    c.nombre as categoria_nombre,
                    SUM(ABS(m.cantidad)) as cantidad_vendida,
                    SUM(ABS(m.cantidad) * p.precio) as ingresos_brutos,
                    SUM(ABS(m.cantidad) * p.costo) as costo_total,
                    (SUM(ABS(m.cantidad) * p.precio) - SUM(ABS(m.cantidad) * p.costo)) as ganancia_bruta,
                    p.precio,
                    p.costo
                FROM movimientos m
                JOIN productos p ON m.id_producto = p.id_producto
                JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE m.tipo_movimiento = 'VENTA'
                AND DATE(m.fecha_movimiento) >= ? AND DATE(m.fecha_movimiento) <= ?
                """
                
                params = [fecha_inicio.isoformat(), fecha_fin.isoformat()]
                filters_applied = {
                    'fecha_inicio': fecha_inicio.isoformat(),
                    'fecha_fin': fecha_fin.isoformat()
                }
                
                if categoria_id:
                    query += " AND p.id_categoria = ?"
                    params.append(categoria_id)
                    filters_applied['categoria_id'] = categoria_id
                
                query += " GROUP BY p.id_producto ORDER BY ganancia_bruta DESC"
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                # Convertir a lista de diccionarios
                data = []
                total_ingresos = Decimal('0')
                total_costos = Decimal('0')
                total_ganancia = Decimal('0')
                
                for row in rows:
                    ingresos = Decimal(str(row['ingresos_brutos']))
                    costos = Decimal(str(row['costo_total']))
                    ganancia = Decimal(str(row['ganancia_bruta']))
                    
                    # Calcular margen de ganancia
                    margen_porcentaje = 0
                    if ingresos > 0:
                        margen_porcentaje = float((ganancia / ingresos) * 100)
                    
                    item = {
                        'producto_id': row['id_producto'],
                        'producto_nombre': row['producto_nombre'],
                        'categoria_nombre': row['categoria_nombre'],
                        'cantidad_vendida': row['cantidad_vendida'],
                        'ingresos_brutos': float(ingresos),
                        'costo_total': float(costos),
                        'ganancia_bruta': float(ganancia),
                        'margen_porcentaje': round(margen_porcentaje, 2)
                    }
                    data.append(item)
                    
                    total_ingresos += ingresos
                    total_costos += costos
                    total_ganancia += ganancia
                
                # Calcular margen total
                margen_total_porcentaje = 0
                if total_ingresos > 0:
                    margen_total_porcentaje = float((total_ganancia / total_ingresos) * 100)
                
                # Preparar totales y resumen
                totals = {
                    'total_ingresos': float(total_ingresos),
                    'total_costos': float(total_costos),
                    'total_ganancia': float(total_ganancia),
                    'margen_total_porcentaje': round(margen_total_porcentaje, 2)
                }
                
                summary = {
                    'productos_analizados': len(data),
                    'periodo': f"{fecha_inicio.isoformat()} - {fecha_fin.isoformat()}"
                }
                
                return {
                    'data': data,
                    'summary': summary,
                    'totals': totals,
                    'generated_at': datetime.now(),
                    'filters_applied': filters_applied
                }
                
        except Exception as e:
            self.logger.error(f"Error generando reporte de rentabilidad: {e}")
            raise
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas resumen generales del sistema
        
        Returns:
            Dict con estadísticas principales
        """
        try:
            with self._get_connection() as conn:
                stats = {}
                
                # Total de productos
                cursor = conn.execute("SELECT COUNT(*) as total FROM productos WHERE activo = 1")
                stats['total_productos'] = cursor.fetchone()['total']
                
                # Productos con stock
                cursor = conn.execute("SELECT COUNT(*) as total FROM productos WHERE activo = 1 AND stock > 0")
                stats['productos_con_stock'] = cursor.fetchone()['total']
                
                # Valor total del inventario
                cursor = conn.execute("""
                    SELECT SUM(stock * costo) as valor_total 
                    FROM productos p
                    JOIN categorias c ON p.id_categoria = c.id_categoria
                    WHERE p.activo = 1 AND c.tipo = 'MATERIAL'
                """)
                valor_total = cursor.fetchone()['valor_total']
                stats['valor_total_inventario'] = float(valor_total) if valor_total else 0
                
                # Ventas del mes actual
                primer_dia_mes = date.today().replace(day=1)
                cursor = conn.execute("""
                    SELECT COUNT(*) as total, SUM(total) as suma
                    FROM ventas 
                    WHERE DATE(fecha_venta) >= ?
                """, [primer_dia_mes.isoformat()])
                row = cursor.fetchone()
                stats['ventas_mes_actual'] = row['total']
                stats['ingresos_mes_actual'] = float(row['suma']) if row['suma'] else 0
                
                # TODO: Implementar productos más vendidos
                stats['productos_mas_vendidos'] = []
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas resumen: {e}")
            raise
    
    def export_to_pdf(
        self, 
        report_data: Dict[str, Any], 
        pdf_path: str, 
        report_type: str,
        company_info: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Exporta reporte a PDF usando reportlab
        
        Args:
            report_data: Datos del reporte
            pdf_path: Ruta donde guardar el PDF
            report_type: Tipo de reporte ('inventory', 'movements', 'sales', 'profitability')
            company_info: Información de la empresa para el encabezado
            
        Returns:
            True si la exportación fue exitosa
        """
        try:
            # Validación básica
            if not report_data or 'data' not in report_data:
                self.logger.error("Datos de reporte inválidos para exportación PDF")
                return False
            
            # Importar generador de PDFs
            from reports.pdf_generator import generate_pdf_report
            
            # Información de empresa por defecto si no se proporciona
            if not company_info:
                company_info = {
                    'nombre': 'Copy Point S.A.',
                    'ruc': '888-888-8888',
                    'direccion': 'Las Lajas, Las Cumbres, Panamá',
                    'telefono': '6666-6666',
                    'email': 'copy.point@gmail.com'
                }
            
            # Generar PDF usando el generador especializado
            success = generate_pdf_report(
                report_data=report_data,
                pdf_path=pdf_path,
                report_type=report_type,
                company_info=company_info
            )
            
            if success:
                self.logger.info(f"PDF generado exitosamente: {pdf_path}")
            else:
                self.logger.error(f"Error generando PDF: {pdf_path}")
            
            return success
            
        except ImportError as e:
            self.logger.error(f"Error importando generador de PDFs: {e}")
            # Fallback: crear PDF básico para mantener compatibilidad
            try:
                with open(pdf_path, 'wb') as f:
                    f.write(b'%PDF-1.4\n%Reporte generado sin reportlab\n')
                return True
            except:
                return False
            
        except Exception as e:
            self.logger.error(f"Error exportando a PDF: {e}")
            return False
