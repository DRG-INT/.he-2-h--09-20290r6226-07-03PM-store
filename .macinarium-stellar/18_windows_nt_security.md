# Windows NT Security
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Windows NT Security?
A Windows NT Security rendszer kezeli a hozzáférést, a jogosultságokat, az auditálást és a titkosítást. Célja, hogy csak jogosult felhasználók és programok érhessenek el erőforrásokat.

## 2. Windows NT Security architektúra

### 2.1 Security Reference Monitor
- Hozzáférési szabályok ellenőrzése
- Jogosultságok kezelése
- Auditálás

### 2.2 Access Token
- Felhasználó azonosítója
- Csoport tagság
- Jogosultságok
- Integrity Level

### 2.3 Security Descriptor
- Owner
- Group
- DACL (Discretionary Access Control List)
- SACL (System Access Control List)

## 3. Hozzáférési szabályok

### 3.1 Hozzáférési jogok
- GENERIC_READ
- GENERIC_WRITE
- GENERIC_EXECUTE
- GENERIC_ALL

### 3.2 DACL
- ACE (Access Control Entry)
- Access Allowed
- Access Denied
- Audit

### 3.3 SACL
- Audit bejegyzések
- Success/Failure
- Audit célok

## 4. Jogosultságok

### 4.1 Jogosultság típusok
- SeChangeNotifyPrivilege
- SeSecurityPrivilege
- SeBackupPrivilege
- SeRestorePrivilege
- SeSystemtimePrivilege

### 4.2 Jogosultságok kezelése
```c
// Jogosultságok lekérdezése
LookupPrivilegeValue(NULL, SE_SECURITY_NAME, &luid);

// Jogosultságok beállítása
AdjustTokenPrivileges(hToken, FALSE, &tp, 0, NULL, NULL);
```

## 5. User Account Control (UAC)

### 5.1 Mi az a UAC?
- Felhasználói fiókok szintjei
- Standard user vs Administrator
- Virtualization (redirection)

### 5.2 UAC szintek
- Standard user
- Administrator
- System

## 6. Integrity Levels

### 6.1 Mi az a Integrity Level?
- Biztonsági szint
- Low, Medium, High, System

### 6.2 Integrity Levels használata
- Internet Explorer: Low
- alkalmazások: Medium
- Rendszerszolgáltatások: High
- Kernel: System

## 7. AppContainer

### 7.1 Mi az a AppContainer?
- Alkalmazások izolálása
- Korlátozott hozzáférés
- Windows Store alkalmazások

### 7.2 AppContainer jogosultságok
- Korlátozott fájlrendszer hozzáférés
- Korlátozott registry hozzáférés
- Korlátozott hálózati hozzáférés

## 8. Windows Hello és biometria

### 8.1 Windows Hello
- Arckép
- Ujjlenyomat
- PIN

### 8.2 Biometria
- Face recognition
- Fingerprint
- Iris

## 9. Windows Defender

### 9.1 Windows Defender Antivirus
- Víruskereső
- Valós idejű védelem
- Felhővédelem

### 9.2 Windows Defender Firewall
- Tűzfal
- Hálózati szűrés
- Szabályok

## 10. Összefoglalás
A Windows NT Security rendszer összetett, de jól strukturált. Kezeli a hozzáférést, a jogosultságokat, az auditálást és a titkosítást. A Security Reference Monitor biztosítja, hogy csak jogosult felhasználók és programok érhessenek el erőforrásokat.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
