@echo off
echo ===============================================
echo GUARDANDO CAMBIOS DE REFACTORIZACION MODO TECLADO
echo Sistema de Inventario Copy Point S.A.
echo ===============================================

cd /d "D:\inventario_app2"

echo.
echo Estado actual de Git:
git status

echo.
echo Agregando archivos modificados...
git add src/ui/forms/movement_form.py
git add src/ui/forms/sales_form.py
git add tests/ui/forms/test_movement_form_barcode_integration.py
git add tests/ui/forms/test_sales_form_barcode_integration.py
git add tests/ui/widgets/test_barcode_entry.py
git add tests/test_barcode_service_keyboard_mode.py
git add CHANGELOG.md

echo.
echo Creando commit...
git commit -m "refactor: Complete refactoring to keyboard mode for barcode scanning

- REFACTORED: movement_form.py v2.0 - keyboard mode implementation
- REFACTORED: sales_form.py v2.0 - keyboard mode implementation  
- REMOVED: Hardware dependencies (hidapi, threads, device management)
- ADDED: Direct BarcodeEntry widget integration
- ADDED: Comprehensive test suite for keyboard mode
- IMPROVED: Code maintainability and universal HID compatibility
- TESTED: TDD protocol applied with full test coverage

BREAKING CHANGE: Removed hardware scanner methods
- toggle_scanner, _start_scanner_check, _scanner_check_loop removed
- Now requires HID keyboard mode configuration on scanners
- Universal compatibility with any HID keyboard-mode scanner"

echo.
echo Estado final:
git status

echo.
echo Commit completado - Refactorizacion Modo Teclado
echo ===============================================
pause
