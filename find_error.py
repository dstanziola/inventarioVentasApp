#!/usr/bin/env python3
"""
Script de Localización de Errores - Sistema Inventario v3.0
Diagnóstico de problemas de acceso al sistema de archivos

Autor: Claude Opus 4
Fecha: 2025-07-22
Versión: 1.0
"""

import os
import sys
import traceback
from pathlib import Path
import json
from datetime import datetime


class ErrorDiagnostic:
    """Clase para diagnóstico de errores del sistema de archivos."""
    
    def __init__(self, base_path: str = "D:\\inventario_app2"):
        self.base_path = Path(base_path)
        self.errors = []
        self.warnings = []
        self.info = []
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "base_path": str(self.base_path),
            "python_version": sys.version,
            "platform": sys.platform
        }
    
    def log_error(self, message: str, exception: Exception = None):
        """Registra un error en el diagnóstico."""
        error_data = {
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        if exception:
            error_data["exception"] = str(exception)
            error_data["traceback"] = traceback.format_exc()
        
        self.errors.append(error_data)
        print(f"❌ ERROR: {message}")
        if exception:
            print(f"   Detalle: {exception}")
    
    def log_warning(self, message: str):
        """Registra una advertencia."""
        warning_data = {
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.warnings.append(warning_data)
        print(f"⚠️  WARNING: {message}")
    
    def log_info(self, message: str):
        """Registra información."""
        info_data = {
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.info.append(info_data)
        print(f"ℹ️  INFO: {message}")
    
    def check_path_existence(self):
        """Verifica la existencia del directorio base."""
        try:
            if self.base_path.exists():
                self.log_info(f"Directorio base existe: {self.base_path}")
                return True
            else:
                self.log_error(f"Directorio base NO existe: {self.base_path}")
                return False
        except Exception as e:
            self.log_error(f"Error verificando existencia de directorio", e)
            return False
    
    def check_permissions(self):
        """Verifica permisos de acceso."""
        try:
            if self.base_path.exists():
                # Verificar permisos de lectura
                if os.access(self.base_path, os.R_OK):
                    self.log_info("Permisos de lectura: OK")
                else:
                    self.log_error("Sin permisos de lectura")
                
                # Verificar permisos de escritura
                if os.access(self.base_path, os.W_OK):
                    self.log_info("Permisos de escritura: OK")
                else:
                    self.log_error("Sin permisos de escritura")
                
                # Verificar permisos de ejecución
                if os.access(self.base_path, os.X_OK):
                    self.log_info("Permisos de ejecución: OK")
                else:
                    self.log_error("Sin permisos de ejecución")
        except Exception as e:
            self.log_error("Error verificando permisos", e)
    
    def list_directory_contents(self):
        """Intenta listar contenidos del directorio."""
        try:
            if self.base_path.exists() and self.base_path.is_dir():
                contents = list(self.base_path.iterdir())
                self.log_info(f"Directorio contiene {len(contents)} elementos")
                
                for item in contents[:10]:  # Mostrar solo primeros 10
                    item_type = "DIR" if item.is_dir() else "FILE"
                    self.log_info(f"  [{item_type}] {item.name}")
                
                if len(contents) > 10:
                    self.log_info(f"  ... y {len(contents) - 10} elementos más")
                
                return contents
            else:
                self.log_error("El directorio no existe o no es un directorio")
                return []
        except Exception as e:
            self.log_error("Error listando contenidos del directorio", e)
            return []
    
    def check_critical_files(self):
        """Verifica la existencia de archivos críticos del sistema."""
        critical_files = [
            "claude_instructions_v3.md",
            "architecture.md",
            "features_backlog.md",
            "inventory_system_directory.md",
            "change_log.md",
            "app_test_plan.md",
            "config_reference.md"
        ]
        
        found_files = []
        missing_files = []
        
        for file_name in critical_files:
            file_path = self.base_path / file_name
            try:
                if file_path.exists():
                    found_files.append(file_name)
                    self.log_info(f"Archivo crítico encontrado: {file_name}")
                else:
                    missing_files.append(file_name)
                    self.log_warning(f"Archivo crítico faltante: {file_name}")
            except Exception as e:
                self.log_error(f"Error verificando archivo {file_name}", e)
                missing_files.append(file_name)
        
        self.report["critical_files"] = {
            "found": found_files,
            "missing": missing_files,
            "total_critical": len(critical_files)
        }
    
    def test_file_operations(self):
        """Prueba operaciones básicas de archivos."""
        test_file = self.base_path / "test_diagnostic.tmp"
        
        try:
            # Prueba de escritura
            with open(test_file, 'w') as f:
                f.write("Test diagnostic file\n")
            self.log_info("Prueba de escritura: OK")
            
            # Prueba de lectura
            with open(test_file, 'r') as f:
                content = f.read()
            if "Test diagnostic" in content:
                self.log_info("Prueba de lectura: OK")
            else:
                self.log_error("Prueba de lectura: FALLO - contenido incorrecto")
            
            # Limpieza
            test_file.unlink()
            self.log_info("Limpieza de archivo de prueba: OK")
            
        except Exception as e:
            self.log_error("Error en pruebas de operaciones de archivo", e)
            # Intentar limpiar en caso de error
            try:
                if test_file.exists():
                    test_file.unlink()
            except:
                pass
    
    def generate_report(self):
        """Genera reporte final de diagnóstico."""
        self.report.update({
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "summary": {
                "total_errors": len(self.errors),
                "total_warnings": len(self.warnings),
                "total_info": len(self.info),
                "status": "CRITICAL" if self.errors else "WARNING" if self.warnings else "OK"
            }
        })
        
        # Guardar reporte en archivo
        try:
            report_file = self.base_path / "diagnostic_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.report, f, indent=2, ensure_ascii=False)
            self.log_info(f"Reporte guardado en: {report_file}")
        except Exception as e:
            self.log_error("No se pudo guardar el reporte", e)
    
    def run_full_diagnostic(self):
        """Ejecuta diagnóstico completo."""
        print("="*60)
        print("DIAGNÓSTICO DEL SISTEMA DE INVENTARIO v3.0")
        print("="*60)
        print()
        
        print("1. Verificando existencia del directorio base...")
        path_exists = self.check_path_existence()
        print()
        
        if path_exists:
            print("2. Verificando permisos...")
            self.check_permissions()
            print()
            
            print("3. Listando contenidos del directorio...")
            self.list_directory_contents()
            print()
            
            print("4. Verificando archivos críticos...")
            self.check_critical_files()
            print()
            
            print("5. Probando operaciones de archivo...")
            self.test_file_operations()
            print()
        
        print("6. Generando reporte final...")
        self.generate_report()
        print()
        
        print("="*60)
        print("RESUMEN DEL DIAGNÓSTICO")
        print("="*60)
        print(f"Estado: {self.report['summary']['status']}")
        print(f"Errores: {self.report['summary']['total_errors']}")
        print(f"Advertencias: {self.report['summary']['total_warnings']}")
        print(f"Información: {self.report['summary']['total_info']}")
        print()
        
        if self.errors:
            print("ACCIONES RECOMENDADAS:")
            print("- Verificar que el directorio D:\\inventario_app2 existe")
            print("- Comprobar permisos de usuario en el directorio")
            print("- Verificar que no hay procesos bloqueando archivos")
            print("- Considerar ejecutar como administrador si es necesario")
        
        return self.report


def main():
    """Función principal del script."""
    try:
        diagnostic = ErrorDiagnostic()
        report = diagnostic.run_full_diagnostic()
        
        # Códigos de salida
        if report['summary']['status'] == 'CRITICAL':
            sys.exit(1)
        elif report['summary']['status'] == 'WARNING':
            sys.exit(2)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ ERROR CRÍTICO en el script de diagnóstico: {e}")
        traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()