# Windows NT Driver Development – Gyakorlati Ismertetők
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: TUDNIVALÓ

## 1. Miért fontos a Driver Development?
A Windows NT Driver Development a Windows kernelbe tartozó eszközmeghajtók fejlesztése. A driver-ek közvetlenül a kernelben futnak, és kezelik a hardvereszközöket.

## 2. Driver fejlesztési környezet

### 2.1 Windows Driver Kit (WDK)
- Visual Studio integráció
- Driver fejlesztői eszközök
- Tesztelési eszközök

### 2.2 Driver típusok
```c
// Function Driver
NTSTATUS DriverEntry(PDRIVER_OBJECT DriverObject, PUNICODE_STRING RegistryPath) {
    DriverObject->DriverUnload = DriverUnload;
    DriverObject->MajorFunction[IRP_MJ_CREATE] = DispatchCreate;
    DriverObject->MajorFunction[IRP_MJ_CLOSE] = DispatchClose;
    return STATUS_SUCCESS;
}

// Filter Driver
NTSTATUS FilterDriverEntry(PDRIVER_OBJECT DriverObject, PUNICODE_STRING RegistryPath) {
    IoAttachDeviceToDeviceStack(&FilterDeviceObject, TargetDeviceObject);
    return STATUS_SUCCESS;
}
```

## 3. Eszközmeghajtók létrehozása

### 3.1 Eszköz létrehozása
```c
NTSTATUS CreateDevice(PDRIVER_OBJECT DriverObject) {
    UNICODE_STRING DeviceName = RTL_CONSTANT_STRING(L"\\Device\\MyDevice");
    PDEVICE_OBJECT DeviceObject;
    
    NTSTATUS status = IoCreateDevice(
        DriverObject,
        0,
        &DeviceName,
        FILE_DEVICE_UNKNOWN,
        0,
        FALSE,
        &DeviceObject
    );
    
    return status;
}
```

### 3.2 Szimbólumikus link
```c
NTSTATUS CreateSymbolicLink() {
    UNICODE_STRING DeviceName = RTL_CONSTANT_STRING(L"\\Device\\MyDevice");
    UNICODE_STRING SymLinkName = RTL_CONSTANT_STRING(L"\\DosDevices\\MyDevice");
    
    return IoCreateSymbolicLink(&SymLinkName, &DeviceName);
}
```

## 4. I/O kezelés

### 4.1 IRP kezelés
```c
NTSTATUS DispatchIrp(PDEVICE_OBJECT DeviceObject, PIRP Irp) {
    PIO_STACK_LOCATION irpSp = IoGetCurrentIrpStackLocation(Irp);
    
    switch (irpSp->MajorFunction) {
        case IRP_MJ_CREATE:
            // Eszköz megnyitása
            break;
        case IRP_MJ_CLOSE:
            // Eszköz bezárása
            break;
        case IRP_MJ_READ:
            // Olvasás
            break;
        case IRP_MJ_WRITE:
            // Írás
            break;
    }
    
    IoCompleteRequest(Irp, IO_NO_INCREMENT);
    return STATUS_SUCCESS;
}
```

### 4.2 Buffer kezelés
```c
PVOID GetBuffer(PIRP Irp) {
    if (Irp->MdlAddress) {
        return MmGetSystemAddressForMdlSafe(Irp->MdlAddress, NormalPagePriority);
    }
    return Irp->AssociatedIrp.SystemBuffer;
}
```

## 5. Driver telepítés

### 5.1 INF fájl
```inf
[Version]
Signature="$WINDOWS NT$"
Class=Sample
ClassGuid={4D36E97D-E325-11CE-BFC1-08002BE10318}

[Manufacturer]
%MfgName%=DeviceList

[DeviceList]
%DeviceDesc%=DeviceInstall, USB\VID_1234&PID_5678

[DeviceInstall]
CopyFiles=DriverCopyFiles

[DriverCopyFiles]
sample.sys

[DestinationDirs]
DriverCopyFiles=12

[SourceDisksNames]
1 = %DiskName%,,,""

[SourceDisksFiles]
sample.sys=1
```

### 5.2 Driver telepítése
```bash
# Driver telepítése
sc create sample binPath= "C:\Windows\System32\drivers\sample.sys" type= kernel
sc start sample

# Driver leállítása
sc stop sample

# Driver törlése
sc delete sample
```

## 6. Driver hibakeresés

### 6.1 WinDbg használata
```bash
# Kernel dump elemzés
windbg -z C:\Windows\MEMORY.DMP

# Live kernel debugging
windbg -k net:port=50000,key=1.2.3.4
```

### 6.2 Hibakeresési technikák
```c
// Debug üzenet
KdPrint(("Debug üzenet\n"));

// Assert
ASSERT(condition);

// Breakpoint
DbgBreakPoint();
```

## 7. Driver biztonság

### 7.1 Driver aláírás
```bash
# Driver aláírás ellenőrzése
sigcheck -a sample.sys

# Test signing mód
bcdedit /set testsigning on
```

### 7.2 Driver ellenőrzés
```c
// Driver ellenőrzés
if (!MmIsDriverVerifying(DriverObject)) {
    // Driver nincs ellenőrizve
}
```

## 8. Driver optimalizálás

### 8.1 I/O optimalizálás
```c
// I/O optimalizálás
IoCreateDevice(
    DriverObject,
    0,
    &DeviceName,
    FILE_DEVICE_UNKNOWN,
    0,
    FALSE,
    &DeviceObject
);
```

### 8.2 Memória optimalizálás
```c
// Memória optimalizálás
PVOID pMem = ExAllocatePoolWithTag(NonPagedPool, size, 'tag');
```

## 9. Driver monitorozás

### 9.1 Driver naplózás
```c
// Driver naplózás
KdPrint(("Driver esemény: %d\n", event));
```

### 9.2 Driver teljesítmény
```c
// Driver teljesítmény
PERFORMANCE_INFORMATION pi;
GetPerformanceInfo(&pi, sizeof(pi));
```

## 10. Összefoglalás
A Windows NT Driver Development összetett, de jól strukturált rendszer. A KMDF és UMDF keretrendszerek egyszerűbbé teszik a driver fejlesztést. A driver biztonság és aláírás kötelező a modern Windows rendszereken.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
