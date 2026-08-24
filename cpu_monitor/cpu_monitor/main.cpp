#include <iostream>
#include <windows.h>
#include "include/IPlatform.h"
#include "include/IDeviceManager.h"
#include "include/ICPUEx.h"
#include "include/IBIOSEx.h"
#include "include/IDevice.h"

// returns IPlatform object
typedef IPlatform& (__stdcall* GetPlatformFunc)();

int main(){
    std::cout << "Starting CPU Monitor" << std::endl;

    // load platform.dll into the memory
    HMODULE hPlatform = LoadLibrary(L"Platform.dll"); 
    
    // prevent segmentation fault
    if(hPlatform == NULL){
        std:: cout << "Failed to load Platform.dll, check if it exits in the correct path";
        return 1;
    }

    // hunt down the memory address of the GetPlatform function after loading it through Platform.dll
    GetPlatformFunc GetPlatform = (GetPlatformFunc)GetProcAddress(hPlatform, "GetPlatform");

    if (GetPlatform == NULL){
        std::cout << "failed to find the GetPlatform inside the dll" << std::endl;
        return 1;
    }

    // call the function GetPlatform() and retrieve the AMD Platform object
    IPlatform& rPlatform = GetPlatform();

    // tell the AMD driver to initialize it's connection to the kernel
    if(rPlatform.Init() == false){
        std::cout << "failed to initialize the AMD Platform" << std::endl;
        return 1;
    }

    std::cout << "successfully hooked and initiallized the AMD Ring-0 driver" << std::endl;


    return 0;


}