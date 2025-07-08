#!/usr/bin/env python3
"""
Validación Final de Refactorización Service Container
====================================================

Script para validar que la refactorización del Service Container 
ha sido completada exitosamente en todos los formularios.

Validaciones:
1. Sintaxis correcta en todos los archivos refactorizados
2. Imports correctos (eliminación de dependencias directas)
3. Propiedades lazy implementadas correctamente
4. Patrón arquitectónico consistente
5. Tests TDD disponibles

Autor: Sistema de Inventario - Validación Final
Fecha: Julio 2025
Versión: 1.0 - Refactorización Completa
"""

import ast
import os
import re
from pathlib import Path


class ServiceContainerValidation:
    """Validador de refactorización Service Container."""
    
    def __init__(self):
        self.base_path = Path('D:/inventario_app2')
        self.forms_path = self.base_path / 'src' / 'ui' / 'forms'
        self.tests_path = self.base_path / 'tests'
        
        # Formularios refactorizados
        self.refactored_forms = [
            'category_form.py',
            'client_form.py', 
            'sales_form.py',
            'movement_form.py'
        ]
        
        # Tests TDD creados
        self.tdd_tests = [
            'test_category_form_container.py',
            'test_client_form_container.py',
            'test_sales_form_container.py', 
            'test_movement_form_container.py'
        ]
        
        self.validation_results = {}
    
    def validate_syntax(self):
        """Validar sintaxis de archivos refactorizados."""
        print("=== Validación de Sintaxis ===")
        syntax_results = {}
        
        for form_file in self.refactored_forms:
            file_path = self.forms_path / form_file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                ast.parse(content)
                syntax_results[form_file] = {"status": "✅ VÁLIDO", "error": None}
                print(f"✅ {form_file}: Sintaxis válida")
                
            except SyntaxError as e:
                syntax_results[form_file] = {
                    "status": "❌ ERROR", 
                    "error": f"Línea {e.lineno}: {e.msg}"
                }
                print(f"❌ {form_file}: Error de sintaxis en línea {e.lineno}: {e.msg}")
            except Exception as e:
                syntax_results[form_file] = {"status": "❌ ERROR", "error": str(e)}
                print(f"❌ {form_file}: Error: {e}")
        
        self.validation_results['syntax'] = syntax_results
        return syntax_results
    
    def validate_imports(self):
        """Validar imports correctos en formularios refactorizados."""
        print("\n=== Validación de Imports ===")
        imports_results = {}
        
        for form_file in self.refactored_forms:
            file_path = self.forms_path / form_file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar imports requeridos
                has_service_container = 'from services.service_container import get_container' in content
                
                # Verificar imports deprecated eliminados
                deprecated_imports = [
                    'from db.database import get_database_connection',
                    'from services.category_service import CategoryService',
                    'from services.client_service import ClientService',
                    'from services.product_service import ProductService',
                    'from services.sales_service import SalesService',
                    'from services.movement_service import MovementService',
                    'from services.barcode_service import BarcodeService',
                    'from services.ticket_service import TicketService'
                ]
                
                has_deprecated = any(dep_import in content for dep_import in deprecated_imports)
                
                if has_service_container and not has_deprecated:
                    imports_results[form_file] = "✅ CORRECTO"
                    print(f"✅ {form_file}: Imports refactorizados correctamente")
                elif has_service_container and has_deprecated:
                    imports_results[form_file] = "⚠️ PARCIAL"
                    print(f"⚠️ {form_file}: Tiene Service Container pero mantiene imports deprecated")
                else:
                    imports_results[form_file] = "❌ INCORRECTO"
                    print(f"❌ {form_file}: Imports incorrectos")
                    
            except Exception as e:
                imports_results[form_file] = f"❌ ERROR: {e}"
                print(f"❌ {form_file}: Error leyendo archivo: {e}")
        
        self.validation_results['imports'] = imports_results
        return imports_results
    
    def validate_lazy_properties(self):
        """Validar implementación de propiedades lazy."""
        print("\n=== Validación de Propiedades Lazy ===")
        lazy_results = {}
        
        # Patrones esperados por formulario
        expected_patterns = {
            'category_form.py': ['@property', 'def category_service'],
            'client_form.py': ['@property', 'def client_service'],
            'sales_form.py': ['@property', 'def product_service', 'def client_service', 'def sales_service', 'def barcode_service'],
            'movement_form.py': ['@property', 'def movement_service', 'def product_service', 'def barcode_service', 'def ticket_service']
        }
        
        for form_file in self.refactored_forms:
            file_path = self.forms_path / form_file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                patterns = expected_patterns.get(form_file, [])
                found_patterns = []
                
                for pattern in patterns:
                    if pattern in content:
                        found_patterns.append(pattern)
                
                if len(found_patterns) >= len([p for p in patterns if 'def ' in p]) + 1:  # +1 for @property
                    lazy_results[form_file] = "✅ IMPLEMENTADO"
                    print(f"✅ {form_file}: Propiedades lazy implementadas correctamente")
                else:
                    lazy_results[form_file] = f"❌ FALTANTE: {set(patterns) - set(found_patterns)}"
                    print(f"❌ {form_file}: Propiedades lazy incompletas")
                    
            except Exception as e:
                lazy_results[form_file] = f"❌ ERROR: {e}"
                print(f"❌ {form_file}: Error validando propiedades: {e}")
        
        self.validation_results['lazy_properties'] = lazy_results
        return lazy_results
    
    def validate_constructor_changes(self):
        """Validar cambios en constructores."""
        print("\n=== Validación de Constructores ===")
        constructor_results = {}
        
        for form_file in self.refactored_forms:
            file_path = self.forms_path / form_file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar constructor
                constructor_match = re.search(r'def __init__\(self[^)]*\):', content)
                
                if constructor_match:
                    constructor_line = constructor_match.group(0)
                    
                    # Verificar que no requiera db_connection (excepto movement_form por compatibilidad)
                    if form_file == 'movement_form.py':
                        # MovementForm mantiene db_connection para compatibilidad
                        if 'db_connection' in constructor_line:
                            constructor_results[form_file] = "✅ CORRECTO (compatibilidad mantenida)"
                            print(f"✅ {form_file}: Constructor con compatibilidad mantenida")
                        else:
                            constructor_results[form_file] = "⚠️ MODIFICADO"
                            print(f"⚠️ {form_file}: Constructor modificado inesperadamente")
                    else:
                        # Otros formularios no deben requerir db_connection
                        if 'db_connection' not in constructor_line:
                            constructor_results[form_file] = "✅ REFACTORIZADO"
                            print(f"✅ {form_file}: Constructor refactorizado correctamente")
                        else:
                            constructor_results[form_file] = "❌ NO REFACTORIZADO"
                            print(f"❌ {form_file}: Constructor aún requiere db_connection")
                else:
                    constructor_results[form_file] = "❌ NO ENCONTRADO"
                    print(f"❌ {form_file}: Constructor no encontrado")
                    
            except Exception as e:
                constructor_results[form_file] = f"❌ ERROR: {e}"
                print(f"❌ {form_file}: Error validando constructor: {e}")
        
        self.validation_results['constructors'] = constructor_results
        return constructor_results
    
    def validate_tests_tdd(self):
        """Validar existencia de tests TDD."""
        print("\n=== Validación de Tests TDD ===")
        tests_results = {}
        
        for test_file in self.tdd_tests:
            file_path = self.tests_path / test_file
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificar contenido básico de tests
                    has_unittest = 'import unittest' in content
                    has_test_class = 'class Test' in content
                    has_test_methods = 'def test_' in content
                    has_service_container = 'ServiceContainer' in content
                    
                    if all([has_unittest, has_test_class, has_test_methods, has_service_container]):
                        tests_results[test_file] = "✅ COMPLETO"
                        print(f"✅ {test_file}: Test TDD completo")
                    else:
                        tests_results[test_file] = "⚠️ INCOMPLETO"
                        print(f"⚠️ {test_file}: Test TDD incompleto")
                        
                except Exception as e:
                    tests_results[test_file] = f"❌ ERROR: {e}"
                    print(f"❌ {test_file}: Error leyendo test: {e}")
            else:
                tests_results[test_file] = "❌ NO EXISTE"
                print(f"❌ {test_file}: Archivo no existe")
        
        self.validation_results['tests'] = tests_results
        return tests_results
    
    def generate_final_report(self):
        """Generar reporte final de validación."""
        print("\n" + "="*60)
        print("REPORTE FINAL DE VALIDACIÓN")
        print("="*60)
        
        total_forms = len(self.refactored_forms)
        total_tests = len(self.tdd_tests)
        
        # Contar éxitos por categoría
        syntax_success = sum(1 for r in self.validation_results.get('syntax', {}).values() 
                           if r.get('status') == '✅ VÁLIDO')
        
        imports_success = sum(1 for r in self.validation_results.get('imports', {}).values() 
                            if r == '✅ CORRECTO')
        
        lazy_success = sum(1 for r in self.validation_results.get('lazy_properties', {}).values() 
                         if r == '✅ IMPLEMENTADO')
        
        constructor_success = sum(1 for r in self.validation_results.get('constructors', {}).values() 
                                if '✅' in r)
        
        tests_success = sum(1 for r in self.validation_results.get('tests', {}).values() 
                          if r == '✅ COMPLETO')
        
        print(f"\n📊 ESTADÍSTICAS DE VALIDACIÓN:")
        print(f"Sintaxis válida: {syntax_success}/{total_forms} ({syntax_success/total_forms*100:.0f}%)")
        print(f"Imports correctos: {imports_success}/{total_forms} ({imports_success/total_forms*100:.0f}%)")
        print(f"Propiedades lazy: {lazy_success}/{total_forms} ({lazy_success/total_forms*100:.0f}%)")
        print(f"Constructores refactorizados: {constructor_success}/{total_forms} ({constructor_success/total_forms*100:.0f}%)")
        print(f"Tests TDD completos: {tests_success}/{total_tests} ({tests_success/total_tests*100:.0f}%)")
        
        # Calcular éxito total
        total_checks = syntax_success + imports_success + lazy_success + constructor_success + tests_success
        max_checks = total_forms * 4 + total_tests  # 4 validaciones por formulario + tests
        success_percentage = (total_checks / max_checks) * 100
        
        print(f"\n🎯 ÉXITO TOTAL DE REFACTORIZACIÓN: {success_percentage:.1f}%")
        
        if success_percentage >= 90:
            print("🎉 ¡REFACTORIZACIÓN EXITOSA!")
            status = "✅ COMPLETADA"
        elif success_percentage >= 75:
            print("⚠️ Refactorización mayormente exitosa con problemas menores")
            status = "⚠️ MAYORMENTE COMPLETADA"
        else:
            print("❌ Refactorización requiere correcciones")
            status = "❌ REQUIERE CORRECCIONES"
        
        print(f"\n🚀 ESTADO FINAL: {status}")
        
        return {
            'success_percentage': success_percentage,
            'status': status,
            'details': self.validation_results
        }
    
    def run_full_validation(self):
        """Ejecutar validación completa."""
        print("INICIANDO VALIDACIÓN COMPLETA DE REFACTORIZACIÓN SERVICE CONTAINER")
        print("="*70)
        
        self.validate_syntax()
        self.validate_imports() 
        self.validate_lazy_properties()
        self.validate_constructor_changes()
        self.validate_tests_tdd()
        
        return self.generate_final_report()


if __name__ == "__main__":
    validator = ServiceContainerValidation()
    result = validator.run_full_validation()
    
    print(f"\n💾 Resultados guardados en validation_results")
    print(f"Estado final: {result['status']}")
    print(f"Porcentaje de éxito: {result['success_percentage']:.1f}%")
