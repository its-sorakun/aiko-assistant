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
    // to prevent DLL hell, both platform.dll and device.dll can be found in cpu_monitor/cpu_monitor/x64/Debug folder
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

    std::cout << "successfully hooked and initialized the AMD Ring-0 driver" << std::endl;

    // get device manager from AMD Platform
    IDeviceManager& rDeviceManager = rPlatform.GetIDeviceManager();

    // ask the device manager for the CPU object (device Type: dtCPU, Index: 0)

    ICPUEx* pCpu = (ICPUEx*)rDeviceManager.GetDevice(dtCPU, 0);

    if(pCpu == NULL){
        std::cout << "Failed to find the CPU device" << std::endl;
        return 1;
    }

    // allocate a blank block of memory on the stack
    CPUParameters stData;

    // pass that memory block to the driver to be filled
    int iRet = pCpu->GetCPUParameters(stData);

    //  Check if it succeeded (0 usually means success in low-level C APIs)
    if (iRet == 0) { 
        std::cout << "Current CPU Temperature: " << stData.dTemperature << " Celsius" << std::endl;
    } else {
        std::cout << "Failed to read CPU parameters! Error Code: " << iRet << std::endl;
    }


    return 0;


}