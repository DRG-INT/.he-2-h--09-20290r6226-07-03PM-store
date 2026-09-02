# Windows NT Driver Development
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Windows NT Driver Development?
A Windows NT Driver Development a Windows kernelbe tartozó eszközmeghajtók fejlesztése. A driver-ek közvetlenül a kernelben futnak, és kezelik a hardvereszközöket.

## 2. Driver típusok

### 2.1 Kernel-Mode Driver
- Kernel szintű futtatás
- Teljes hozzáférés a kernelhez
- Hibás driver kernel összeomláshoz vezet

### 2.2 User-Mode Driver
- Felhasználói szintű futtatás
- Korlátozott hozzáférés
- Kernel összeomlás nélkül

### 2.3 WDM (Windows Driver Model)
- Windows 2000, XP, Vista, 7
- Kompatibilitási réteg

### 2.4 KMDF (Kernel-Mode Driver Framework)
- Windows XP és újabb
- Ajánlott driver keretrendszer
- Egyszerűbb fejlesztés

### 2.5 UMDF (User-Mode Driver Framework)
- Windows Vista és újabb
- Felhasználói szintű driver-ek
- Kernel biztonság

## 3. Driver fejlesztési környezet

### 3.1 Windows Driver Kit (WDK)
- Visual Studio integráció
- Driver fejlesztői eszközök
- Tesztelési eszközök

### 3.2 Driver típusok
- **Function Driver:** Eszköz funkcióját kezeli
- **Filter Driver:** I/O kérések módosítása
- **Miniport Driver:** Hardver specifikus

## 4. Driver struktúra

### 4.1 DriverEntry
```c
NTSTATUS DriverEntry(
    PDRIVER_OBJECT DriverObject,
    PUNICODE_STRING RegistryPath
) {
    // Driver inicializálása
    DriverObject->DriverUnload = DriverUnload;
    return STATUS_SUCCESS;
}
```

### 4.2 Dispatch rutinok
```c
NTSTATUS DriverDispatch(
    PDEVICE_OBJECT DeviceObject,
    PIRP Irp
) {
    // I/O kérés kezelése
    switch (MajorFunction) {
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

## 5. Eszközmeghajtók létrehozása

### 5.1 Eszköz létrehozása
```c
NTSTATUS CreateDevice(
    PDRIVER_OBJECT DriverObject,
    PUNICODE_STRING DeviceName,
    PDEVICE_OBJECT *DeviceObject
) {
    return IoCreateDevice(
        DriverObject,
        0,
        DeviceName,
        FILE_DEVICE_UNKNOWN,
        0,
        FALSE,
        DeviceObject
    );
}
```

### 5.2 Szimbólumikus link létrehozása
```c
NTSTATUS CreateSymbolicLink(
    PUNICODE_STRING SymbolicLinkName,
    PUNICODE_STRING DeviceName
) {
    return IoCreateSymbolicLink(SymbolicLinkName, DeviceName);
}
```

## 6. I/O kezelés

### 6.1 IRP kezelés
```c
NTSTATUS HandleIrp(
    PDEVICE_OBJECT DeviceObject,
    PIRP Irp
) {
    PIO_STACK_LOCATION irpSp = IoGetCurrentIrpStackLocation(Irp);
    switch (irpSp->MajorFunction) {
        case IRP_MJ_READ:
            // Olvasás kezelése
            break;
        case IRP_MJ_WRITE:
            // Írás kezelése
            break;
    }
    IoCompleteRequest(Irp, IO_NO_INCREMENT);
    return STATUS_SUCCESS;
}
```

### 6.2 Buffer kezelés
```c
// Buffer lekérdezése
PVOID buffer = MmGetSystemAddressForMdlSafe(Irp->MdlAddress, NormalPagePriority);

// Buffer másolása
RtlCopyMemory(buffer, userBuffer, length);
```

## 7. Driver biztonság

### 7.1 Driver aláírás
- Windows 10 1607 óta kötelező
- WHQL (Windows Hardware Quality Labs)
- Test signing mód

### 7.2 Driver ellenőrzés
```c
// Driver ellenőrzés
if (!MmIsDriverVerifying(DriverObject)) {
    // Driver nincs ellenőrizve
}
```

## 8. Driver hibakeresés

### 8.1 WinDbg
- Kernel debugger
- Driver betöltés hibakeresés
- I/O hibakeresés

### 8.2 Hibakeresési technikák
```c
// Debug üzenet
KdPrint(("Debug üzenet\n"));

// Assert
ASSERT(condition);

// Breakpoint
DbgBreakPoint();
```

## 9. Driver telepítés

### 9.1 INF fájl
```inf
[Version]
Signature="$WINDOWS NT$"
Class=Sample
ClassGuid={...}

[Manufacturer]
%MfgName%=DeviceList

[DeviceList]
%DeviceDesc%=DeviceInstall, USB\VID_1234&PID_5678

[DeviceInstall]
CopyFiles=DriverCopyFiles

[DriverCopyFiles]
sample.sys
```

### 9.2 Driver telepítése
```bash
# Driver telepítése
sc create sample binPath= "C:\Windows\System32\drivers\sample.sys" type= kernel
sc start sample
```

## 10. Összefoglalás
A Windows NT Driver Development összetett, de jól strukturált rendszer. A KMDF és UMDF keretrendszerek egyszerűbbé teszik a driver fejlesztést. A driver biztonság és aláírás kötelező a modern Windows rendszereken.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
