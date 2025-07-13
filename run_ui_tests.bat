@echo off
setlocal EnableDelayedExpansion

:: Ruta base de pruebas UI
set TEST_DIR=tests\integration\ui\forms
set REPORT_DIR=tests\reports

echo -------------------------------------------------
echo Ejecutando pruebas UI y generando reportes...
echo -------------------------------------------------

:: Lista de archivos de prueba UI a ejecutar
set TEST_FILES=^
 test_main_window_ui_integration.py^
 test_product_form_ui_complete.py^
 test_sales_form_ui_complete.py^
 test_category_form_ui_complete.py^
 test_client_form_ui_complete.py^
 test_movement_form_ui_complete.py^
 test_reports_form_ui_complete.py^
 test_ticket_forms_ui_complete.py^
 test_user_interaction_flows.py^
 test_ui_comprehensive_suite.py

:: Crear carpeta de reportes si no existe
if not exist %REPORT_DIR% (
    mkdir %REPORT_DIR%
)

:: Ejecutar cada prueba individualmente
for %%F in (%TEST_FILES%) do (
    echo Ejecutando %%F...
    pytest %TEST_DIR%\%%F > %REPORT_DIR%\%%~nF.txt
    echo Resultado guardado en %REPORT_DIR%\%%~nF.txt
    echo -------------------------------------------------
)

echo Pruebas finalizadas.
echo Los resultados individuales se encuentran en: %REPORT_DIR%
pause
