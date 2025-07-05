@echo off
echo ============================================
echo VALIDACION DE REFACTORIZACION MODO TECLADO
echo Sistema de Inventario Copy Point S.A.
echo ============================================

cd /d "D:\inventario_app2"

echo.
echo Ejecutando tests de validacion...
echo.

echo --- Test 1: BarcodeEntry Widget ---
python -m pytest tests/ui/widgets/test_barcode_entry.py -v --tb=short
echo Return code: %ERRORLEVEL%

echo.
echo --- Test 2: MovementForm Integration ---
python -m pytest tests/ui/forms/test_movement_form_barcode_integration.py -v --tb=short
echo Return code: %ERRORLEVEL%

echo.
echo --- Test 3: SalesForm Integration ---
python -m pytest tests/ui/forms/test_sales_form_barcode_integration.py -v --tb=short
echo Return code: %ERRORLEVEL%

echo.
echo --- Test 4: BarcodeService Keyboard Mode ---
python -m pytest tests/test_barcode_service_keyboard_mode.py -v --tb=short
echo Return code: %ERRORLEVEL%

echo.
echo ============================================
echo VALIDACION COMPLETADA
echo ============================================
pause
