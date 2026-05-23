<div align="center">

# ⚗️ VR-CRC
## Visible Reasoning for Colorectal Cancer

**We didn't build a medical AI. We built the nervous system of the surgeon who hasn't been born yet.**

[![License: MIT](https://img.shields.io/badge/License-MIT-violet.svg)](LICENSE)
[![Model: deepseek-r1:8b](https://img.shields.io/badge/Model-deepseek--r1%3A8b-blue.svg)](https://ollama.com/library/deepseek-r1)
[![Privacy: Zero-Cloud](https://img.shields.io/badge/Privacy-Zero--Cloud-brightgreen.svg)](#zero-cloud-privacy)
[![Cost: $0.00](https://img.shields.io/badge/API%20Cost-%240.00%20USD-gold.svg)](#hardware)
[![Platform: M4 Mac](https://img.shields.io/badge/Platform-Apple%20M4%20Mac-silver.svg)](#hardware)

</div>

---

## 🌀 The Problem with Medical AI Today

Every major AI system deployed in medicine today commits the same unforgivable sin: **it whispers its conclusions and silences its reasoning.**

Radiologists trust a heatmap. Oncologists trust a percentage. Surgeons trust a recommendation. And when the patient dies—when the cancer returns at month 18, when the liver lights up on the PET scan—nobody can ask the machine *why*. The black box doesn't answer. It never did.

The regulatory bodies (FDA, PMDA/厚労省) don't reject AI because it's wrong. They reject it because **it cannot explain itself in a language that holds up in a courtroom.**

We rejected that paradigm entirely.

---

## ⚡ What is VR-CRC?

VR-CRC is a **local-first, zero-cloud, zero-cost clinical intelligence system** for colorectal cancer prognosis and dynamic therapy optimization. It runs entirely on a single Apple M4 Mac with 24GB unified memory. No subscriptions. No data transmission. No API bills. No HIPAA violations.

It controls a locally-hosted `deepseek-r1:8b` model via Ollama and forces it to perform **Medical Chain-of-Thought (M-CoT)**—a structured, auditable, real-time broadcast of every inference step the model takes, rendered in clinical Japanese, visible to any physician, reviewable by any ethics board.

This is not Explainable AI. Explainable AI is a post-hoc apology.

**This is Visible Reasoning. The thinking happens out loud, before the conclusion.**

---

## 🔬 Core Pillars

### 1. Zero-Cloud Privacy 🔒

```
Patient data enters the system.
Patient data never leaves the machine.
End of story.
```

All weights, all inference, all logs are stored on a physically isolated external SSD (`/Volumes/<SSD>/vr-crc-workspace`). The Ollama model store is redirected via `OLLAMA_MODELS` environment variable. Your patient's genomic profile has never touched AWS, Azure, GCP, or any inference API. The attack surface is zero. The cost is zero. The privacy guarantee is absolute.

This is **not** a compliance checkbox. This is a **geopolitical posture**—in an era where medical infrastructure is a strategic target, an air-gapped AI is an act of institutional survival.

---

### 2. Visible Reasoning Framework 🧠

The foundational insight of VR-CRC is this: **the most dangerous moment in AI-assisted medicine is the silence between the input and the output.**

We destroy that silence.

```
<think>
右側大腸癌...T3N2M0...RAS Mutant...
待て。ここで一瞬止まれ。
RAS変異があるということは、Cetuximab/Panitumumabの上乗せ効果は期待できない。
しかし、もっと根本的な問題がある—右側という原発部位そのものが、
腸内細菌叢、胎生期起源、エピゲノムの観点から、
左側大腸癌とは全く別の「病気」として扱われるべきだ。
SEERデータを見ると、同ステージでも右側は左側より5年生存率が約12%低い...
これはN2の重みと相乗的に作用する。局所再発よりも、
まず肝転移の早期スクリーニング体制の確立を最優先に提言すべきではないか...
</think>

{
  "predicted_15y_survival_rate": "34%",
  "estimated_recurrence_risk": "High(72%)",
  ...
}
```

Every `<think>` block is streamed in real-time to the physician's screen. The model's doubts, its recalibrations, its recognition of edge cases—all of it is rendered in a scrolling terminal. The physician is not reading a verdict. **They are watching a colleague think.**

---

### 3. Showa-EndoAI & ASCO-Sidedness Integration 🏥

VR-CRC's clinical intelligence framework is built on three interlocking knowledge systems:

#### 3a. Showa University Endoscopy AI Paradigm (CADe/CADx)
The `cT1(SM)` pathway—endoscopic submucosal dissection (ESD) versus additional surgical resection—is one of the most consequential decision points in early-stage colorectal cancer. A `SM invasion depth ≥1000μm`, positive lymphovascular invasion, poor differentiation, or tumor budding Grade 2+ are not merely features. They are **probabilistic sentences**. VR-CRC encodes these risk factors as first-class features in its JSON patient schema and forces the model to explicitly interrogate each one before concluding.

The `25% right-sided colon cancer miss rate in colonoscopy` (driven by flat morphology, haustral folds, and bowel prep failure at the cecum) is a known, quantified tragedy. VR-CRC treats it as a prior that shapes every right-sided T1 case.

#### 3b. ASCO 2024+ mCRC Guidelines (Sidedness Doctrine)
The ASCO consensus on metastatic colorectal cancer is unambiguous:

| Feature | Right-Sided | Left-Sided |
|---|---|---|
| Embryonic Origin | Midgut | Hindgut |
| MSI-H Prevalence | ~22% | ~4% |
| BRAF V600E | High | Low |
| anti-EGFR Response (RAS WT) | ❌ Ineffective | ✅ Highly Effective |
| 5-yr Survival (Stage IV) | ~8% | ~19% |
| Recommended 1st-line (RAS WT) | Bev + chemo | Cetux/Panit + chemo |

VR-CRC's feature schema encodes `sidedness` as a top-level, first-order variable. The model is instructed to interrogate it before any other variable. This mirrors how a true oncology expert thinks.

#### 3c. Total Neoadjuvant Therapy (TNT) for LARC
For locally advanced rectal cancer (LARC: cT3-4 or N+), the RAPIDO and PRODIGE-23 trials have established TNT—chemotherapy delivered *before* chemoradiation—as the new standard of care. VR-CRC models this as a binary variable (`TNT: true/false`) and weights its survival benefit explicitly in the prompt architecture.

---

### 4. Hardware Optimization for Apple M4 Mac 🖥️

```
Chip:         Apple M4 (10-core CPU, 10-core GPU, 16-core Neural Engine)
Memory:       24GB Unified Memory (CPU + GPU share the same physical DRAM)
Model:        deepseek-r1:8b (≈4.7GB in Q4_K_M quantization)
Runtime:      Ollama 0.13.x
Inference:    ~35-55 tokens/second on M4 (no VRAM bottleneck)
External SSD: 2TB (Model weights, patient data, logs—isolated from boot drive)
```

The M4's unified memory architecture eliminates the CPU-GPU memory transfer bottleneck that cripples x86 systems running local LLMs. The model lives in memory. Inference is fast. The machine is silent. The intelligence is real.

---

## 🗂️ Repository Structure

```
vr-crc-workspace/
├── README.md                     ← You are here
├── setup_env.sh                  ← Phase 1: Env & Ollama setup
├── src/
│   ├── app.py                    ← Phase 4: Flask server (Ollama proxy + logs)
│   ├── index.html                ← Phase 4: Co-Pilot Web UI (single file)
│   ├── reasoning_engine.py       ← Phase 3: Visible Reasoning engine (CLI)
│   └── sanity_check.py           ← Phase 1: API connectivity test
├── data/
│   └── patients.json             ← Phase 2: 20 mock patients (SEER/TCGA-derived)
├── logs/
│   └── discrepancy_log.json      ← Phase 4: Auto-calibration feedback log
└── assets/
    └── qr_vrcrc.png              ← Phase 5: QR code for instant access
```

---

## 🚀 Quickstart

### Prerequisites
- Apple Mac with M-series chip (M1 or later)
- [Ollama](https://ollama.com) installed
- Python 3.10+, Flask (`pip install flask`)
- External SSD mounted (optional but recommended)

### Step 1: Environment Setup
```bash
chmod +x setup_env.sh
./setup_env.sh
```

This pulls `deepseek-r1:8b` to your external SSD and configures `OLLAMA_MODELS`.

### Step 2: Sanity Check
```bash
python3 src/sanity_check.py
```

### Step 3: Launch Co-Pilot UI
```bash
pip install flask
python3 src/app.py
# → Open http://localhost:5000
```

### Step 4: CLI Reasoning (Optional)
```bash
python3 src/reasoning_engine.py VRC-005
```

---

## 🧬 Feature Vector Schema

Each patient is encoded as a flat JSON object optimized for LLM attention:

```json
{
  "patient_id": "VRC-005",
  "sidedness": "Right",
  "anatomical_location": "上行結腸",
  "T": "1(SM)", "N": "0", "M": "0",
  "SM_invasion_depth_um": 1500,
  "lymphovascular_invasion": true,
  "tumor_budding": "Grade2",
  "differentiation": "Poor",
  "RAS": "Wild", "BRAF": "V600E", "MMR": "dMMR/MSI-H",
  "surgery": "ESD → Right Hemicolectomy(追加切除)",
  "TNT": false,
  "adjuvant_chemo": "Pembrolizumab",
  "targeted": "Pembrolizumab"
}
```

---

## 💬 The Philosophy

> *"The purpose of medicine is to subdue uncertainty. The purpose of AI in medicine is to make uncertainty legible."*

We didn't build this to automate oncologists. We built this to give every oncologist a partner that never sleeps, never forgets the RAPIDO trial, never confuses right-sided and left-sided biology, and—critically—**always shows its work.**

The black box era of medical AI is over.

The era of Visible Reasoning has begun.

---

## ⚖️ Ethics & Data

- All patient data in `data/patients.json` is **fully synthetic**, generated to reflect statistical distributions from public datasets (SEER, TCGA). No real patient data is present or required.
- This system is a **research and demonstration prototype**. It is not a certified medical device. Clinical decisions must always involve qualified physicians.
- Zero external API calls. Zero cost. Zero data transmission. ✅

---

## 📡 QR Code Access

<div align="center">
<img src="assets/qr_vrcrc.png" width="200" alt="VR-CRC QR Code"/>
<p><em>Instant access to this workspace</em></p>
</div>

---

<div align="center">

**Built with 🔬 by the VR-CRC Team**
*Inspired by the Showa University Endoscopy AI Research Group & ASCO Clinical Oncology Guidelines*

*"We make the invisible visible. We make the silent speak."*

</div>
