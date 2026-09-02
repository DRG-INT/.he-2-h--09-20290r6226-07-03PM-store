# Windows NT Security – Gyakorlati Ismertetők
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: TUDNIVALÓ

## 1. Miért fontos a Windows NT Security?
A Windows NT Security rendszer kezeli a hozzáférést, a jogosultságokat, az auditálást és a titkosítást. Célja, hogy csak jogosult felhasználók és programok érhessenek el erőforrásokat.

## 2. Security gyakorlati használata

### 2.1 Access Token kezelése
```c
HANDLE hToken;
OpenProcessToken(GetCurrentProcess(), TOKEN_ALL_ACCESS, &hToken);
```

### 2.2 Jogosultságok kezelése
```c
LUID luid;
LookupPrivilegeValue(NULL, SE_SECURITY_NAME, &luid);

TOKEN_PRIVILEGES tp = { 0 };
tp.PrivilegeCount = 1;
tp.Privileges[0].Luid = luid;
tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;

AdjustTokenPrivileges(hToken, FALSE, &tp, 0, NULL, NULL);
```

### 2.3 Security Descriptor kezelése
```c
PSECURITY_DESCRIPTOR pSD;
InitializeSecurityDescriptor(&pSD, SECURITY_DESCRIPTOR_REVISION);

// Owner beállítása
SetSecurityDescriptorOwner(&pSD, pOwnerSid, FALSE);

// DACL beállítása
SetSecurityDescriptorDacl(&pSD, TRUE, pDacl, FALSE);
```

## 3. Hozzáférési szabályok

### 3.1 Fájl hozzáférés
```c
HANDLE hFile = CreateFile(
    "C:\\file.txt",
    GENERIC_READ,
    0,
    NULL,
    OPEN_EXISTING,
    FILE_ATTRIBUTE_NORMAL,
    NULL
);
```

### 3.2 Eszköz hozzáférés
```c
HANDLE hDevice = CreateFile(
    "\\\\.\\PhysicalDrive0",
    GENERIC_READ | GENERIC_WRITE,
    0,
    NULL,
    OPEN_EXISTING,
    FILE_ATTRIBUTE_NORMAL,
    NULL
);
```

### 3.3 Registry hozzáférés
```c
HKEY hKey;
RegOpenKeyEx(
    HKEY_LOCAL_MACHINE,
    "Software\\MyApp",
    0,
    KEY_READ,
    &hKey
);
```

## 4. UAC (User Account Control)

### 4.1 UAC szintek
- Standard user
- Administrator
- System

### 4.2 UAC virtualizáció
```c
// Virtualization bekapcsolása
WCHAR appName[MAX_PATH];
GetModuleFileName(NULL, appName, MAX_PATH);

// Regisztráció
HKEY hKey;
RegCreateKeyEx(
    HKEY_CURRENT_USER,
    "Software\\Classes\\VirtualStore",
    0,
    NULL,
    REG_OPTION_NON_VOLATILE,
    KEY_ALL_ACCESS,
    NULL,
    &hKey,
    NULL
);
```

## 5. Integrity Levels

### 5.1 Integrity Level beállítása
```c
// Integrity Level beállítása
DWORD dwIntegrityLevel = SECURITY_MANDATORY_LOW_RID;
PSID pIntegritySid = NULL;

ConvertStringSidToSid("S-1-16-4096", &pIntegritySid);

LABEL_SECURITY_INFORMATION lsi = { 0 };
lsi.Label = pIntegritySid;

SetSecurityInfo(
    hFile,
    SE_FILE_OBJECT,
    LABEL_SECURITY_INFORMATION,
    NULL,
    NULL,
    NULL,
    &lsi
);
```

## 6. AppContainer

### 6.1 AppContainer létrehozása
```c
// AppContainer létrehozása
PSID pAppContainerSid;
DeriveAppContainerSid(
    L"AppContainerName",
    &pAppContainerSid
);
```

### 6.2 AppContainer jogosultságok
```c
// AppContainer jogosultságok
CreateProcessAsUser(
    hUserToken,
    "C:\\Windows\\system32\\notepad.exe",
    NULL,
    NULL,
    NULL,
    FALSE,
    CREATE_APPCONTAINER,
    NULL,
    NULL,
    &si,
    &pi
);
```

## 7. Windows Defender

### 7.1 Windows Defender Antivirus
```c
// Windows Defender ellenőrzés
IWindowsDefender *pDefender;
CoCreateInstance(
    CLSID_WindowsDefender,
    NULL,
    CLSCTX_INPROC_SERVER,
    IID_IWindowsDefender,
    (void**)&pDefender
);
```

### 7.2 Windows Defender Firewall
```c
// Tűzfal szabályok
INetFwPolicy2 *pPolicy;
CoCreateInstance(
    __uuidof(NetFwPolicy2),
    NULL,
    CLSCTX_INPROC_SERVER,
    __uuidof(INetFwPolicy2),
    (void**)&pPolicy
);
```

## 8. Auditálás

### 8.1 Audit bejegyzések
```c
// Audit bejegyzések
HANDLE hEventLog = OpenEventLog(NULL, "Security");
ReadEventLog(hEventLog, EVENTLOG_FORWARDS_READ, 0, pBuffer, dwBufferSize, &dwRead, &dwNeeded);
```

### 8.2 Audit események
```c
// Audit események
HANDLE hToken;
GetTokenInformation(hToken, TokenAuditPolicy, pAuditPolicy, sizeof(AUDIT_POLICY), &dwReturned);
```

## 9. Titkosítás

### 9.1 DPAPI
```c
DATA_BLOB dataIn, dataOut;
CryptProtectData(&dataIn, L"Description", NULL, NULL, NULL, CRYPTPROTECT_UI_FORBIDDEN, &dataOut);
```

### 9.2 Crypt API
```c
HCRYPTPROV hCryptProv;
CryptAcquireContext(&hCryptProv, NULL, NULL, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT);
```

## 10. Összefoglalás
A Windows NT Security rendszer összetett, de jól strukturált. Kezeli a hozzáférést, a jogosultságokat, az auditálást és a titkosítást. A Security Reference Monitor biztosítja, hogy csak jogosult felhasználók és programok érhessenek el erőforrásokat.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
