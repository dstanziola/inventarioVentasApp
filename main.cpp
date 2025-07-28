// main.cpp
#include <windows.h>
#include "resource.h"

int APIENTRY WinMain(HINSTANCE hInstance,
                     HINSTANCE hPrevInstance,
                     LPSTR     lpCmdLine,
                     int       nCmdShow)
{
    // Ruta relativa al .bat (o especifica ruta absoluta)
    ShellExecuteA(NULL, "open", "run.bat", NULL, NULL, SW_SHOWNORMAL);
    return 0;
}
