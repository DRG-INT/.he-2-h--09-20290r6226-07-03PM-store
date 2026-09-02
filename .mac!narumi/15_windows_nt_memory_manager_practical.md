# Windows NT Memory Manager – Gyakorlati Ismertetők
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: TUDNIVALÓ

## 1. Miért fontos a Memory Manager?
A Windows NT Memory Manager kezeli a virtuális memóriát, a lapozást, a memóriakezelést és a memóriavédelem. Minden folyamatnak saját címtere van, és a Memory Manager gondoskodik a lapok betöltéséről és a védelemről.

## 2. Memory Manager gyakorlati használata

### 2.1 Memóriakezelés
```c
// Memóriafoglalás
PVOID pMem = VirtualAlloc(
    NULL,
    1024 * 1024,
    MEM_COMMIT | MEM_RESERVE,
    PAGE_READWRITE
);

// Memóriafelszabadítás
VirtualFree(pMem, 0, MEM_RELEASE);
```

### 2.2 Lapozás kezelése
```c
// Lap fájl létrehozása
HANDLE hPageFile = CreateFile(
    "C:\\pagefile.sys",
    GENERIC_READ | GENERIC_WRITE,
    0,
    NULL,
    CREATE_ALWAYS,
    FILE_ATTRIBUTE_NORMAL,
    NULL
);

// Lap fájl megnyitása
HANDLE hPageFile = CreateFile(
    "C:\\pagefile.sys",
    GENERIC_READ | GENERIC_WRITE,
    0,
    NULL,
    OPEN_EXISTING,
    FILE_ATTRIBUTE_NORMAL,
    NULL
);
```

### 2.3 Memóriavédelem
```c
// Memóriavédelem bekapcsolása
DWORD dwOldProtect;
VirtualProtect(
    pMem,
    1024 * 1024,
    PAGE_EXECUTE_READ,
    &dwOldProtect
);
```

## 3. Memory Manager és a hibakeresés

### 3.1 Memóriahibák
- Page Fault
- Access Violation
- Heap Corruption
- Stack Overflow

### 3.2 Hibakeresési eszközök
- **WinDbg:** Kernel memória elemzés
- **VMMap:** Memória címterek elemzése
- **Pool Monitor:** Pool használat

## 4. Memory Manager és a teljesítmény

### 4.1 Memóriateljesítmény
- Working Set
- Page Fault
- TLB miss

### 4.2 Memóriatröszt
```c
// Memóriatörés bekapcsolása
HeapSetInformation(
    GetProcessHeap(),
    HeapEnableTerminationOnCorruption,
    NULL,
    0
);
```

## 5. Memory Manager és a biztonság

### 5.1 Memóriavédelem
- DEP (Data Execution Prevention)
- ASLR (Address Space Layout Randomization)
- SMEP (Supervisor Mode Execution Prevention)
- SMAP (Supervisor Mode Access Prevention)

### 5.2 Memóriavédelem konfiguráció
```c
// DEP bekapcsolása
SetProcessDEPPolicy(PROCESS_DEP_ENABLE);

// ASLR bekapcsolása
IMAGE_DLLCHARACTERISTICS_HIGH_ENTROPY_VA
IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE
```

## 6. Memory Manager és a virtualizáció

### 6.1 Virtualizációs memória
- Hyper-V
- WSL2
- Docker

### 6.2 Memóriakezelés virtualizációban
- Balloon driver
- Memory overcommit
- KSM (Kernel Same-page Merging)

## 7. Memory Manager és a driver fejlesztés

### 7.1 Driver memóriakezelés
```c
// Kernel memóriafoglalás
PVOID pMem = ExAllocatePoolWithTag(
    NonPagedPool,
    1024,
    'tag'
);

// Kernel memóriafelszabadítás
ExFreePoolWithTag(pMem, 'tag');
```

### 7.2 DMA memóriakezelés
```c
// DMA adapter lekérdezése
IoGetDmaAdapter(
    PhysicalDeviceObject,
    &DeviceDescription,
    &NumberOfMapRegisters
);
```

## 8. Memory Manager és a processzek

### 8.1 Processz memóriája
- Virtuális címterek
- Working Set
- Private Bytes

### 8.2 Processz memóriakezelés
```c
// Processz memóriainformációk
PROCESS_MEMORY_COUNTERS pmc;
GetProcessMemoryInfo(
    GetCurrentProcess(),
    &pmc,
    sizeof(pmc)
);
```

## 9. Memory Manager és a fájlok

### 9.1 Fájlba mapelés
```c
// Fájl megnyitása
HANDLE hFile = CreateFile(
    "C:\\file.txt",
    GENERIC_READ,
    0,
    NULL,
    OPEN_EXISTING,
    FILE_ATTRIBUTE_NORMAL,
    NULL
);

// Fájl mapelése
HANDLE hMap = CreateFileMapping(
    hFile,
    NULL,
    PAGE_READONLY,
    0,
    0,
    NULL
);

// Map view
PVOID pView = MapViewOfFile(
    hMap,
    FILE_MAP_READ,
    0,
    0,
    0
);
```

## 10. Összefoglalás
A Windows NT Memory Manager összetett, de jól strukturált rendszer. Kezeli a virtuális memóriát, a lapozást, a memóriakezelést és a memóriavédelem. A Memory Manager biztosítja, hogy minden folyamat saját, védett címteret kapjon.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
