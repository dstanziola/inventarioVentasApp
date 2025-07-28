// main.cpp
#include <windows.h>
#include <shellapi.h>
#include <string.h>

int WINAPI WinMain(HINSTANCE hInstance,
                   HINSTANCE hPrevInstance,
                   LPSTR    lpCmdLine,
                   int      nCmdShow)
{
    // 1) Obtiene la ruta completa de este ejecutable
    char exePath[MAX_PATH];
    GetModuleFileNameA(NULL, exePath, MAX_PATH);

    // 2) Quita el nombre del .exe (todo tras la última '\')
    char *p = strrchr(exePath, '\\');
    if (p) {
        *p = '\0';
    }

    // 3) Construye la ruta completa a run.bat en la misma carpeta
    strcat(exePath, "\\run.bat");

    // 4) Lanza el .bat
    ShellExecuteA(
        NULL,           // ventana padre (ninguna)
        "open",         // acción
        exePath,        // archivo a ejecutar
        NULL,           // parámetros
        NULL,           // directorio de trabajo (ya está en exePath)
        SW_SHOWNORMAL   // estilo de ventana
    );

    return 0;
}
