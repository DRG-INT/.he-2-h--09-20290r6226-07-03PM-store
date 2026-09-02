# Inferno – Gyakorlati Tudás és Ismertetők
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: TUDNIVALÓ

## 1. Miért érdemes ma is az Inferno?
Az Inferno nem csak egy operációs rendszer, hanem egy disztribúlt rendszer elve. A Diszk virtuális gép, a Limbo nyelv, és a Styx protokoll ma is használatosak a disztribúlt rendszerekben.

## 2. Hogyan indulj bele?
- Töltsd le az Inferno ISO-t.
- Írd egy pendrive-ra.
- Bootolj belőle.
- A parancssor a `dis` shell, hasonlít a bashhez, de más.
- A Limbo nyelv a rendszer része.

## 3. Inferno és a modern rendszerek
### 3.1 Limbo nyelv
- A Limbo ma is használatos
- Moduláris, típusbiztos
- Diszk VM-en fut

### 3.2 Styx protokoll
- A Styx protokoll ma is használatos
- 9P protokoll leszármazottja
- Fájlok, eszközök, processzek elérése hálózaton keresztül

### 3.3 Nincs root
- Nincs sudo, nincs su
- Minden felhasználó ugyanazokkal a jogokkal rendelkezik

## 4. Inferno fejlesztés
### 4.1 Forráskód
- Az Inferno forráskódja elérhető a GPL licenc alatt
- Kis, olvasható kernel
- Diszk VM forráskódja elérhető

### 4.2 Limbo nyelv
- A Limbo fordító forráskódja elérhető
- Moduláris, típusbiztos
- Diszk VM-en fut

## 5. Inferno és a biztonság
### 5.1 Hozzáférési szabályok
- Fájljogosultságok
- Nincs root
- Nincs sudo

### 5.2 Veszélyeztetettség
- Kis felhasználói bázis
- Kevesebb támadási felület
- De kevésbé tesztelt

## 6. Inferno és a Plan 9
- Az Inferno a Plan 9 unokaöccse
- A Plan 9-ről örökölte a "minden eszköz fájlrendszer" elvet
- Új elemeket hozott: Diszk VM, Limbo nyelv, Styx protokoll

## 7. Inferno és a Go nyelv
- A Go nyelv (Rob Pike) tervezte a Plan 9-es és Inferno tapasztalatokkal
- A Go a Limbo nyelv öröke
- A Go a Diszk VM elveit követi

## 8. Inferno és a virtualizáció
### 8.1 QEMU
- Inferno futhat QEMU-ban
- Jó fejlesztési és tesztelési környezet

### 8.2 VMware és VirtualBox
- Inferno futhat VirtualBox-ban és VMware-ban
- Jó fejlesztési és tesztelési környezet

## 9. Inferno tanulságai
- A disztribúlt rendszerek elve ma is használatos
- A Diszk virtuális gép koncepciója ma is használatos
- A Limbo nyelv egyszerűsége ma is használatos

## 10. Összefoglalás
Az Inferno egy nagyon jó, de elfelejtett operációs rendszer. A Diszk virtuális gép, a Limbo nyelv, és a Styx protokoll ma is használatosak. Az Inferno a Plan 9 öröksége, de saját úton halad.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
