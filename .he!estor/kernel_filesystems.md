# Kernel Fájlrendszerek és Fájlrendszer Kiválasztás
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Fájlrendszer a Kernelben?

A fájlrendszer az a kernel része, amely kezeli az adatok tárolását a lemezen. A fájlrendszer meghatározza, hogyan tárolódnak a fájlok, hogyan érhetők el, és hogyan kezelődnek a jogosultságok.

## 2. Főbb Linux Fájlrendszerek

### 2.1 Ext4 (Extended Filesystem 4)
- **Előnyök:** Stabil, gyors, jól tesztelt, alapértelmezett
- **Hátrányok:** Korlátok nagy fájlrendszerekben, journalling overhead
- **Használat:** Általános célú, desktop, szerver

### 2.2 XFS
- **Előnyök:** Nagyon nagy fájlrendszerek, jól skálázódik, nagy fájlok kezelése
- **Hátrányok:** Nem támogatja a small file-eket jól, journalling
- **Használat:** Nagy teljesítményű szerverek, adatbázisok

### 2.3 Btrfs (B-Tree Filesystem)
- **Előnyök:** CoW (Copy-on-Write), pillanatképek, RAID támogatás, összetett fájlrendszer
- **Hátrányok:** még nem teljesen stabil, nagyobb overhead
- **Használat:** Desktop, tesztelés, adatvédelmi igényű rendszerek

### 2.4 ZFS
- **Előnyök:** Data integrity, RAID-Z, telítettség ellenállás, pillanatképek
- **Hátrányok:** Nagy memóriahasználat, nem GPL (licenc probléma)
- **Használat:** Tároló szerverek, backup rendszerek

### 2.5 FAT32 / exFAT
- **Előnyök:** Egyszerű, cross-platform, nagy kompatibilitás
- **Hátrányok:** Nincs jogosultságkezelés, nincs journalling, fájlnév korlátok
- **Használat:** USB meghajtók, külső eszközök

### 2.6 NTFS
- **Előnyök:** Windows kompatibilitás, nagy fájlok, journaling
- **Hátrányok:** Lassabb Linux alatt, jogosultságok kezelése problémás
- **Használat:** Dual-boot rendszerek, Windows kompatibilitás

## 3. Fájlrendszer Kiválasztási Kritériumok

### 3.1 Teljesítmény
- **Small files:** Ext4, XFS
- **Large files:** XFS, Btrfs
- **Random access:** XFS, Ext4
- **Sequential access:** XFS, ZFS

### 3.2 Megbízhatóság
- **Data integrity:** ZFS, Btrfs (checksums)
- **Journaling:** Ext4, XFS, NTFS
- **Recovery:** Ext4, XFS

### 3.3 Kompatibilitás
- **Linux only:** Ext4, XFS, Btrfs
- **Cross-platform:** FAT32, exFAT, NTFS
- **Network:** NFS, CIFS/SMB

### 3.4 Funkciók
- **Snapshots:** Btrfs, ZFS
- **Compression:** Btrfs, ZFS
- **Encryption:** Ext4 (ecryptfs), Btrfs (native)
- **RAID:** Btrfs (built-in), ZFS (RAID-Z), MDADM (software)

## 4. Fájlrendszer Működése a Kernelben

### 4.1 VFS (Virtual Filesystem Switch)
- A kernel absztrakció réteg a fájlrendszerek között
- Minden fájlrendszer ugyanazzal a felülettel rendelkezik
- Alkalmazások nem tudják, melyik fájlrendszer van háttérben

### 4.2 Block Layer
- A lemez I/O kezelése
- I/O ütemező (deadline, cfq, noop, bfq)
- Request queue kezelés

### 4.3 Page Cache
- A kernel memóriában tárolja a fájlok gyakran használt részeit
- Gyorsabb elérés, kevesebb lemez I/O

### 4.4 Journaling
- A fájlrendszer módosítások naplózása
- Összeomlás utáni helyreállítás
- Ext3/4, XFS, Btrfs, NTFS támogatja

## 5. Fájlrendszer Karbantartás

### 5.1 Ellenőrzés
```bash
# Ext4 ellenőrzése
fsck.ext4 /dev/sda1

# XFS ellenőrzése
xfs_repair /dev/sda1

# Btrfs ellenőrzése
btrfs check /dev/sda1
```

### 5.2 Defragmentálás
```bash
# Ext4 defragmentálás
e4defrag /dev/sda1

# XFS defragmentálás (nem szükséges, online)
xfs_fsr /dev/sda1

# Btrfs defragmentálás
btrfs filesystem defragment /mnt
```

### 5.3 Méret növelése
```bash
# Ext4 méret növelése
resize2fs /dev/sda1

# XFS méret növelése
xfs_growfs /mnt
```

## 6. Fájlrendszer Teljesítmény Optimalizálás

### 6.1 Mount Opciók
```bash
# Ext4 optimalizálás
mount -o noatime,nodiratime /dev/sda1 /mnt

# XFS optimalizálás
mount -o noatime,nodiratime,logbufs=8 /dev/sda1 /mnt

# Btrfs optimalizálás
mount -o noatime,compress=zstd /dev/sda1 /mnt
```

### 6.2 I/O Ütemező
```bash
# SSD-hez
echo noop > /sys/block/sda/queue/scheduler

# HDD-hez
echo deadline > /sys/block/sda/queue/scheduler
```

## 7. Fájlrendszer Biztonság

### 7.1 Jogosultságok
- **Owner/Group:** Fájlok tulajdonosa és csoportja
- **Permissions:** Olvasás (r), írás (w), végrehajtás (x)
- **ACLs:** Bővített jogosultságok
- **SELinux/AppArmor:** Mandatory Access Control

### 7.2 Titkosítás
- **eCryptfs:** Fájl szintű titkosítás
- **LUKS:** Lemez szintű titkosítás
- **Btrfs native encryption:** Beépített titkosítás

## 8. Összefoglalás

A fájlrendszer kiválasztása:
- **Használati cél** alapján történik
- **Teljesítmény**, **megbízhatóság**, **kompatibilitás** egyensúlyát kell megtartani
- **Ext4** a legstabilabb általános célú választás
- **XFS** nagy teljesítményű szerverekhez
- **Btrfs** modernebb funkciókhoz, de kevésbé stabil
- **ZFS** a legjobb adatintegritáshoz, de nagy memóriahasználat

A fájlrendszer működésének megértése:
- **Kernel VFS** absztrakció megértése
- **Block layer** és **page cache** ismerete
- **Journaling** és **CoW** elméleti ismerete

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
