#!/usr/bin/env python3
"""
Ejecutor de análisis de cobertura - FASE 5A
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

def main():
    # Cambiar al directorio del proyecto
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("=== ANÁLISIS DE COBERTURA DE TESTS - FASE 5A ===")
    print(f"Directorio: {project_dir}")
    print("=" * 60)
    
    # Ejecutar pytest con análisis de cobertura
    print("\n1. Ejecutando pytest con análisis de cobertura...")
    
    cmd = [
        sys.executable, "-m", "pytest", 
        "test_fase5a_adaptado.py",
        "-v",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        print("RESULTADO:")
        print(result.stdout)
        
        if result.stderr:
            print("\nERRORES/WARNINGS:")
            print(result.stderr)
            
        print(f"\nCódigo de salida: {result.returncode}")
        
        # Determinar estado
        if result.returncode == 0:
            print("✅ TESTS EXITOSOS")
        else:
            print("❌ TESTS FALLIDOS")
            
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT: Tests tardaron demasiado")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Análisis manual de archivos
    print("\n2. Análisis manual de estructura...")
    
    # Servicios implementados
    services_dir = project_dir / "src" / "services"
    if services_dir.exists():
        services = [f for f in services_dir.iterdir() if f.is_file() and f.suffix == '.py' and f.name != '__init__.py']
        print(f"   Servicios encontrados: {len(services)}")
        for service in services:
            print(f"   - {service.name}")
    
    # Tests implementados
    tests_dir = project_dir / "tests"
    if tests_dir.exists():
        test_files = list(tests_dir.glob("**/*.py"))
        test_files = [f for f in test_files if f.name.startswith('test_')]
        print(f"   Tests encontrados: {len(test_files)}")
        for test_file in test_files[:10]:  # Primeros 10
            print(f"   - {test_file.name}")
        if len(test_files) > 10:
            print(f"   ... y {len(test_files) - 10} más")
    
    # Análisis de modelos
    models_dir = project_dir / "src" / "models"
    if models_dir.exists():
        models = [f for f in models_dir.iterdir() if f.is_file() and f.suffix == '.py' and f.name != '__init__.py']
        print(f"   Modelos encontrados: {len(models)}")
        for model in models:
            print(f"   - {model.name}")
    
    # Formularios UI
    forms_dir = project_dir / "src" / "ui" / "forms"
    if forms_dir.exists():
        forms = [f for f in forms_dir.iterdir() if f.is_file() and f.suffix == '.py' and f.name != '__init__.py']
        print(f"   Formularios UI encontrados: {len(forms)}")
        for form in forms:
            print(f"   - {form.name}")
    
    print("\n3. Análisis de componentes faltantes...")
    
    # Verificar archivos críticos
    critical_files = [
        "src/db/database.py",
        "src/services/product_service.py",
        "src/services/category_service.py",
        "src/services/sales_service.py",
        "src/services/user_service.py",
        "src/ui/main/main_window.py",
        "src/ui/auth/login_window.py",
        "main.py"
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not (project_dir / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("   ❌ Archivos críticos faltantes:")
        for file in missing_files:
            print(f"      - {file}")
    else:
        print("   ✅ Todos los archivos críticos presentes")
    
    # Análisis de tests específicos por servicio
    print("\n4. Análisis de cobertura por servicio...")
    
    service_tests = {
        "ProductService": ["test_product_service", "test_product_form"],
        "CategoryService": ["test_category", "test_category_form"],
        "SalesService": ["test_sales", "test_sales_form"],
        "UserService": ["test_user", "test_authentication"],
        "ReportService": ["test_report", "test_reports"],
        "BarcodeService": ["test_barcode"]
    }
    
    for service, expected_tests in service_tests.items():
        found_tests = []
        for test_file in test_files:
            for expected in expected_tests:
                if expected in test_file.name.lower():
                    found_tests.append(test_file.name)
        
        if found_tests:
            print(f"   ✅ {service}: {len(found_tests)} tests encontrados")
        else:
            print(f"   ⚠️ {service}: Sin tests específicos encontrados")
    
    print("\n" + "=" * 60)
    print("ANÁLISIS COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    main()
