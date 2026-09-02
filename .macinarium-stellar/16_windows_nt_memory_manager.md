# Windows NT Memory Manager
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Windows NT Memory Manager?
A Windows NT Memory Manager kezeli a virtuális memóriát, a lapozást, a memóriakezelést és a memóriavédelem. Minden folyamatnak saját címtere van, és a Memory Manager gondoskodik a lapok betöltéséről és a védelemről.

## 2. Memóriakezelés architektúra

### 2.1 Virtuális memória
- 32 bites rendszer: 4GB címtér (2GB felhasználó, 2GB kernel)
- 64 bites rendszer: 128TB címtér
- Minden folyamat saját címtere

### 2.2 Lapozás
- 4KB lapok
- Lapozási táblák (PTE)
- TLB (Translation Lookaside Buffer)

### 2.3 Memóriakezelés
- Virtual Address Descriptor (VAD)
- Working Set
- Standby List
- Modified Page List
- Free Page List

## 3. Memory Manager működése

### 3.1 Címterek
- **User space:** 0x00000000 – 0x7FFFFFFF (32 bites)
- **Kernel space:** 0x80000000 – 0xFFFFFFFF (32 bites)
- **Kernel space:** 0xFFFF800000000000 – 0xFFFFFFFFFFFFFFFF (64 bites)

### 3.2 Lapozási táblák
- Page Directory (PD)
- Page Directory Pointer Table (PDPT)
- Page Map Level 4 (PML4) – 64 bites
- Page Table (PT)
- Page Table Entry (PTE)

### 3.3 TLB
- CPU gyorsítótár
- Címfordítás gyorsítása
- TLB miss esetén Memory Manager beavatkozik

## 4. Memóriakezelési funkciók

### 4.1 Allokáció
```c
PVOID VirtualAlloc(
    PVOID Address,
    SIZE_T Size,
    DWORD AllocationType,
    DWORD Protect
);
```

### 4.2 Felszabadítás
```c
BOOL VirtualFree(
    PVOID Address,
    SIZE_T Size,
    DWORD FreeType
);
```

### 4.3 Védelmi módok
- PAGE_NOACCESS
- PAGE_READONLY
- PAGE_READWRITE
- PAGE_EXECUTE
- PAGE_EXECUTE_READ
- PAGE_EXECUTE_READWRITE

## 5. Working Set

### 5.1 Mi az a Working Set?
- A folyamat által használt fizikai memória
- Dinamikusan változik
- Memory Manager kezeli

### 5.2 Working Set kezelés
- Working Set Expansion
- Working Set Trimming
- Page Fault

## 6. Lapozás (Paging)

### 6.1 Lap hívások
- Page Fault
- Page In
- Page Out
- Page Replacement

### 6.2 Lapozási fájl
- `pagefile.sys`
- Merevlemezre kiírt lapok
- Memória helyettesítés

## 7. Memóriavédelem

### 7.1 Memóriavédelmi mechanizmusok
- DEP (Data Execution Prevention)
- ASLR (Address Space Layout Randomization)
- SMEP (Supervisor Mode Execution Prevention)
- SMAP (Supervisor Mode Access Prevention)

### 7.2 Memóriavédelem konfiguráció
```c
// DEP bekapcsolása
SetProcessDEPPolicy(PROCESS_DEP_ENABLE);

// ASLR bekapcsolása
IMAGE_DLLCHARACTERISTICS_HIGH_ENTROPY_VA
IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE
```

## 8. Memóriakezelés hibakeresés

### 8.1 Memóriahibák
- Page Fault
- Access Violation
- Heap Corruption
- Stack Overflow

### 8.2 Hibakeresési eszközök
- **WinDbg:** Kernel memória elemzés
- **Performance Monitor:** Memória használat
- **Pool Monitor:** Pool használat
- **VMMap:** Memória címterek elemzése

## 9. Memóriakezelés optimalizálás

### 9.1 Memóriabeállítások
- Page file méret
- Working set méret
- Pool méret

### 9.2 Memóriatröszt
```c
// Memóriatörés
HeapSetInformation(
    GetProcessHeap(),
    HeapEnableTerminationOnCorruption,
    NULL,
    0
);
```

## 10. Összefoglalás
A Windows NT Memory Manager összetett, de jól strukturált rendszer. Kezeli a virtuális memóriát, a lapozást, a memóriakezelést és a memóriavédelem. A Memory Manager biztosítja, hogy minden folyamat saját, védett címteret kapjon.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
