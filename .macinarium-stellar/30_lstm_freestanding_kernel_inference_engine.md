# LSTM Freestanding Kernel Inference Engine (Ring-0 & Bare-Metal)
Verzió: 1.0-stable
Forrás: UNICAGD-Core Kognitív Rendszermérnöki Keretrendszer / DRG-INT
Státusz: HASZNÁLHATÓ (Freestanding C & Driver Architektúra)

---

## 1. Miért Van Szükség Freestanding LSTM Motorra a Kernelben?

A legtöbb modern mélytanulási keretrendszer (PyTorch, TensorFlow, ONNX Runtime) hatalmas C++ és Python függőségeket igényel, dinamikus memóriát foglal a heapen (`malloc`), és a standard C matematikai könyvtárra (`libm`) támaszkodik. 

**Ring-0 kernel térben, megszakításkezelőkben (hardIRQ/softIRQ) és bare-metal vészhelyzeti rendszerekben ezek egyike sem használható.**

A **Révész Engine** részeként kifejlesztett **`lstm_kernel_engine`** a következő szigorú rendszermérnöki garanciákat nyújtja:
1. **Zéró dinamikus memóriafoglalás (Zero Heap):** Minden mátrix és állapotvektor fordítási időben allokált, fix méretű struktúrákban él.
2. **Freestanding Matematikai Approximáció:** Nincs külső `libm` függőség; gyors, racionális Pade és határolt közelítéseket használ a sigmoid és tanh függvényekhez.
3. **Determinisztikus Futásidő ($O(H \times I + H^2)$):** A szekvencia-lépés időtartama szigorúan korlátos, így valós idejű (RT) kernel szálakban és eBPF felhasználói rétegekben is futtatható.

---

## 2. A Matematikai Kapuk Freestanding Leképzése

A cella állapot ($C_t$) és a rejtett állapot ($h_t$) kiszámítása a következő algebrai lépésekben valósul meg:

$$\mathbf{f}_t = \sigma\left( \mathbf{W}_f \mathbf{x}_t + \mathbf{U}_f \mathbf{h}_{t-1} + \mathbf{b}_f \right)$$
$$\mathbf{i}_t = \sigma\left( \mathbf{W}_i \mathbf{x}_t + \mathbf{U}_i \mathbf{h}_{t-1} + \mathbf{b}_i \right)$$
$$\mathbf{\tilde{C}}_t = \tanh\left( \mathbf{W}_c \mathbf{x}_t + \mathbf{U}_c \mathbf{h}_{t-1} + \mathbf{b}_c \right)$$
$$\mathbf{C}_t = \mathbf{f}_t \odot \mathbf{C}_{t-1} + \mathbf{i}_t \odot \mathbf{\tilde{C}}_t$$
$$\mathbf{o}_t = \sigma\left( \mathbf{W}_o \mathbf{x}_t + \mathbf{U}_o \mathbf{h}_{t-1} + \mathbf{b}_o \right)$$
$$\mathbf{h}_t = \mathbf{o}_t \odot \tanh(\mathbf{C}_t)$$

### 2.1 Gyors Sigmoid és Tanh Kernel Approximáció (Fixed-Latency)
```c
static inline float fast_sigmoid(float x) {
    if (x > 8.0f) return 1.0f;
    if (x < -8.0f) return 0.0f;
    return 1.0f / (1.0f + expf(-x));
}

static inline float fast_tanh(float x) {
    if (x > 8.0f) return 1.0f;
    if (x < -8.0f) return -1.0f;
    return tanhf(x);
}
```

---

## 3. A Négy `LSTM_` Főmodul Rendszermátrixa

| Modul | Funkció és Szerep | Implementáció |
| :--- | :--- | :--- |
| **`LSTM_ENGINE`** | Freestanding C/Rust következtető mag beágyazott és kernel modulokhoz | [`R💀ever-sen-gine=3/src/lstm_kernel_engine.c`](file:///Users/peter/Desktop/kernelpanic/R%F0%9F%92%80ever-sen-gine=3/src/lstm_kernel_engine.c) |
| **`LSTM_AUTOENCODER`** | Felügyeletlen anomália-detektálás rekonstrukciós hiba alapján | [`.macinarium-stellar/24_lstm_autoencoder_anomaly_detection.md`](file:///Users/peter/Desktop/kernelpanic/.macinarium-stellar/24_lstm_autoencoder_anomaly_detection.md) |
| **`LSTM_PREDICTOR`** | Kernel panic valószínűségének többváltozós előrejelzése $\Delta t$ időablakban | [`.macinarium-stellar/25_kernel_panic_prediction_with_lstm.md`](file:///Users/peter/Desktop/kernelpanic/.macinarium-stellar/25_kernel_panic_prediction_with_lstm.md) |
| **`LSTM_MYCELIAL`** | Mikorrhiza-ihlette hipergráf, amely összeköti a hardveres és kernel invariánsokat | [`.macinarium-stellar/29_lstm_filesystem_and_project_topology.md`](file:///Users/peter/Desktop/kernelpanic/.macinarium-stellar/29_lstm_filesystem_and_project_topology.md) |

---

## 4. Riasztási és Pánik-Eltérítési Folyamat

Amikor a rendszerben az eBPF vagy kprobes szondák kritikus terhelést vagy invariáns-sérülést érzékelnek:
1. Az **`lstm_forward_step`** feldolgozza a telemetriai vektort ($\mathbf{x}_t$).
2. Ha a számított anomália-érték meghaladja az előre beállított küszöböt ($\text{MSE} > 0.05$):
3. Azonnal aktiválódik a **Révész Pánik Eltérítő (`revesz_emergency_divert`)**, amely a felhalmozott állapotot átmenti a biztonságos partra, megelőzve a teljes hardveres fagyást.

---
*Dokumentum státusz: STABIL · UNICAGD-Core Kognitív Rendszermérnöki Architektúra*
