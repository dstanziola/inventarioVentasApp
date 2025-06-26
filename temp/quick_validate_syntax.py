#!/usr/bin/env python3
"""
Script simple para verificar sintaxis de modelos
"""

# Test básico de importación de modelos
try:
    import ast
    
    # Validar Ticket
    with open("D:\\inventario_app2\\models\\ticket.py", "r", encoding="utf-8") as f:
        ticket_content = f.read()
    ast.parse(ticket_content)
    print("✅ Ticket - Sintaxis válida")
    
    # Validar CompanyConfig  
    with open("D:\\inventario_app2\\models\\company_config.py", "r", encoding="utf-8") as f:
        config_content = f.read()
    ast.parse(config_content)
    print("✅ CompanyConfig - Sintaxis válida")
    
    # Validar Database
    with open("D:\\inventario_app2\\db\\database.py", "r", encoding="utf-8") as f:
        db_content = f.read()
    ast.parse(db_content)
    print("✅ Database - Sintaxis válida")
    
    print("\n🎯 TODOS LOS MODELOS VALIDADOS EXITOSAMENTE")
    print("Proceeding to next step: Creating unit tests...")
    
except Exception as e:
    print(f"❌ Error: {e}")
