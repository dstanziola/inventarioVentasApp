#!/usr/bin/env python3
"""
Script para ejecutar análisis de cobertura de tests - FASE 5A
Proyecto: Sistema de Inventario Copy Point
"""

import subprocess
import sys
import os
from pathlib import Path

def run_coverage_analysis():
    """Ejecuta el análisis de cobertura de tests"""
    
    # Cambiar al directorio del proyecto
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("=== ANÁLISIS DE COBERTURA DE TESTS - FASE 5A ===\n")
    print(f"Directorio de trabajo: {project_dir}")
    
    # Comando para ejecutar pytest con coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html:coverage_report",
        "--cov-fail-under=0",
        "-v",
        "--tb=short"
    ]
    
    print(f"Ejecutando: {' '.join(cmd)}\n")
    
    try:
        # Ejecutar el comando
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print("=== SALIDA DEL ANÁLISIS ===")
        print(result.stdout)
        
        if result.stderr:
            print("\n=== ERRORES/ADVERTENCIAS ===")
            print(result.stderr)
        
        print(f"\n=== CÓDIGO DE SALIDA: {result.returncode} ===")
        
        # Verificar si se generó el reporte HTML
        html_report = project_dir / "coverage_report" / "index.html"
        if html_report.exists():
            print(f"\nReporte HTML generado en: {html_report}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("ERROR: El análisis de cobertura tomó demasiado tiempo (>5 minutos)")
        return False
    except Exception as e:
        print(f"ERROR: No se pudo ejecutar el análisis: {e}")
        return False

if __name__ == "__main__":
    success = run_coverage_analysis()
    sys.exit(0 if success else 1)
