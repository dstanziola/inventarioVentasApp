#!/usr/bin/env python3
"""
Cargador de Contexto - Sistema Inventario v3.0
Lee y muestra archivos críticos para establecer contexto de desarrollo

Autor: Claude Opus 4
Fecha: 2025-07-22
Versión: 1.0
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime


class ContextLoader:
    """Clase para cargar contexto del sistema de inventario."""
    
    def __init__(self, base_path: str = "D:\\inventario_app2"):
        self.base_path = Path(base_path)
        self.context = {}
        
    def load_file_content(self, filename: str):
        """Carga el contenido de un archivo específico."""
        file_path = self.base_path / filename
        
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"✅ Cargado: {filename} ({len(content)} caracteres)")
                return content
            else:
                print(f"❌ No encontrado: {filename}")
                return None
                
        except Exception as e:
            print(f"❌ Error leyendo {filename}: {e}")
            return None
    
    def load_critical_files(self):
        """Carga archivos críticos del sistema."""
        critical_files = [
            "features_backlog.md",
            "inventory_system_directory.md", 
            "change_log.md",
            "claude_instructions_v3.md",
            "architecture.md",
            "app_test_plan.md",
            "config_reference.md"
        ]
        
        print("="*60)
        print("CARGANDO CONTEXTO CRÍTICO DEL SISTEMA")
        print("="*60)
        
        for filename in critical_files:
            content = self.load_file_content(filename)
            if content:
                self.context[filename] = {
                    "content": content,
                    "size": len(content),
                    "timestamp": datetime.now().isoformat()
                }
        
        print(f"\nArchivos cargados exitosamente: {len(self.context)}")
        return self.context
    
    def display_file_summary(self, filename: str, max_lines: int = 20):
        """Muestra resumen de un archivo específico."""
        if filename in self.context:
            content = self.context[filename]["content"]
            lines = content.split('\n')
            
            print(f"\n{'='*60}")
            print(f"ARCHIVO: {filename}")
            print(f"{'='*60}")
            print(f"Tamaño: {len(content)} caracteres")
            print(f"Líneas: {len(lines)}")
            print(f"Primeras {min(max_lines, len(lines))} líneas:")
            print("-" * 40)
            
            for i, line in enumerate(lines[:max_lines], 1):
                print(f"{i:3d}: {line}")
            
            if len(lines) > max_lines:
                print(f"... y {len(lines) - max_lines} líneas más")
        else:
            print(f"❌ Archivo {filename} no está cargado en el contexto")
    
    def display_all_summaries(self):
        """Muestra resumen de todos los archivos cargados."""
        for filename in self.context.keys():
            self.display_file_summary(filename, max_lines=15)
    
    def save_context_report(self):
        """Guarda reporte del contexto cargado."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(self.context),
            "files": {}
        }
        
        for filename, data in self.context.items():
            report["files"][filename] = {
                "size": data["size"],
                "timestamp": data["timestamp"],
                "lines": len(data["content"].split('\n'))
            }
        
        try:
            report_file = self.base_path / "context_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Reporte de contexto guardado en: {report_file}")
        except Exception as e:
            print(f"❌ Error guardando reporte: {e}")
        
        return report
    
    def get_project_status(self):
        """Analiza el estado actual del proyecto."""
        status = {
            "architecture_available": "architecture.md" in self.context,
            "backlog_available": "features_backlog.md" in self.context,
            "changelog_available": "change_log.md" in self.context,
            "directory_available": "inventory_system_directory.md" in self.context,
            "instructions_available": "claude_instructions_v3.md" in self.context
        }
        
        # Analizar backlog si está disponible
        if status["backlog_available"]:
            backlog_content = self.context["features_backlog.md"]["content"]
            status["in_progress_tasks"] = backlog_content.count("in_progress")
            status["completed_tasks"] = backlog_content.count("completed") 
            status["pending_tasks"] = backlog_content.count("pending")
        
        # Analizar changelog si está disponible
        if status["changelog_available"]:
            changelog_content = self.context["change_log.md"]["content"]
            status["recent_changes"] = len([line for line in changelog_content.split('\n') 
                                          if line.startswith('## [2025')])
        
        return status
    
    def run_full_context_load(self):
        """Ejecuta carga completa de contexto."""
        # Cargar archivos críticos
        self.load_critical_files()
        
        # Mostrar resúmenes
        self.display_all_summaries()
        
        # Analizar estado del proyecto
        print(f"\n{'='*60}")
        print("ANÁLISIS DEL ESTADO DEL PROYECTO")
        print(f"{'='*60}")
        
        status = self.get_project_status()
        for key, value in status.items():
            print(f"{key}: {value}")
        
        # Guardar reporte
        self.save_context_report()
        
        return self.context


def main():
    """Función principal del script."""
    try:
        loader = ContextLoader()
        context = loader.run_full_context_load()
        
        print(f"\n{'='*60}")
        print("CONTEXTO CARGADO EXITOSAMENTE")
        print(f"{'='*60}")
        print(f"Total de archivos en contexto: {len(context)}")
        print("Listo para operaciones de desarrollo.")
        
    except Exception as e:
        print(f"❌ ERROR en carga de contexto: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()