#!/usr/bin/env python3
"""
VR-CRC Phase 3: Visible Reasoning Engine
Medical Chain-of-Thought via deepseek-r1:8b (Ollama)
"""

import json
import urllib.request
import urllib.error
import re
import os
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "deepseek-r1:8b"
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
DISCREPANCY_LOG = os.path.join(LOG_DIR, "discrepancy_log.json")

SYSTEM_PROMPT = """あなたは世界最高峰の臨床腫瘍医（大腸がん専門）であり、最先端内視鏡AI（CADe/CADx）の思想とASCOガイドラインを完全にマスターしたAIです。
入力された患者の多次元特徴量ベクトルを、解剖学的再発リスク、左右差（Sidedness）による生物学的悪性度、遺伝子変異（RAS/BRAF/MMR）、TNTおよびロボット手術の生存ベネフィットの観点から冷徹に分析しなさい。

1. 【潜在空間と思考の連動】
   必ず最初に <think> タグの内部で、臨床ガイドラインや大規模疫学データ（SEER/TCGA等）の傾向を踏まえた医師の「直感的な違和感」「リスクの嗅覚」「長考プロセス（M-CoT）」を、思考が変遷していく実況中継形式で日本語で詳細に書き出しなさい。

2. <think> の外側（タグ終了後）には、厳密に以下のJSON構造のみを出力しなさい：
{
  "predicted_15y_survival_rate": "XX%",
  "estimated_recurrence_risk": "Low/Moderate/High(XX%)",
  "estimated_distant_metastasis_risk": "Low/Moderate/High(XX%)",
  "key_clinical_reasoning": "（150文字以内の日本語で決定的要因を記述）",
  "treatment_optimization": "（推奨される追加治療・モニタリング戦略）"
}"""


def build_patient_prompt(patient: dict) -> str:
    """患者データからプロンプトを構築"""
    sm_info = ""
    if patient.get("T") == "1(SM)":
        sm_info = f"""
- SM浸潤深さ: {patient.get('SM_invasion_depth_um', '不明')} μm
- 脈管侵襲: {'あり' if patient.get('lymphovascular_invasion') else 'なし'}
- 腫瘍出芽(Budding): {patient.get('tumor_budding', '不明')}
- 分化度: {patient.get('differentiation', '不明')}"""

    return f"""{SYSTEM_PROMPT}

---
【患者ID】: {patient['patient_id']}
【原発部位】: {patient['anatomical_location']}（{patient['sidedness']}側大腸癌）
【TNM分類】: T{patient['T']} N{patient['N']} M{patient['M']} / Stage {patient['stage_group']}{sm_info}
【遺伝子プロファイル】:
- RAS変異: {patient['RAS']}
- BRAF変異: {patient['BRAF']}
- MMR/MSIステータス: {patient['MMR']}
【治療】:
- 術式: {patient['surgery']}
- 術前CRT: {'あり' if patient.get('preop_CRT') else 'なし'}
- TNT療法: {'あり（最新局所進行直腸癌プロトコル）' if patient.get('TNT') else 'なし'}
- 術後化学療法: {patient.get('adjuvant_chemo', 'None')}
- 分子標的薬: {patient.get('targeted', 'None')}
---

上記患者の15年生存率・再発リスクを、<think>タグ内で段階的に推論し、最後にJSONで出力せよ。"""


def parse_response(raw: str) -> dict:
    """レスポンスから<think>とJSONを分離"""
    think_match = re.search(r"<think>(.*?)</think>", raw, re.DOTALL)
    think_content = think_match.group(1).strip() if think_match else ""

    # JSONブロックを抽出
    json_match = re.search(r"\{[^{}]*\"predicted_15y_survival_rate\"[^{}]*\}", raw, re.DOTALL)
    parsed_json = {}
    if json_match:
        try:
            parsed_json = json.loads(json_match.group(0))
        except json.JSONDecodeError:
            parsed_json = {"error": "JSON parse failed", "raw": json_match.group(0)}

    return {"think": think_content, "result": parsed_json}


def run_inference(patient: dict, stream_callback=None) -> dict:
    """Ollama APIに推論リクエストを送信（ストリーミング対応）"""
    prompt = build_patient_prompt(patient)
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": 0.15,
            "num_predict": 2048,
            "top_p": 0.9,
            "repeat_penalty": 1.1
        }
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    full_response = ""
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            for line in resp:
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    token = chunk.get("response", "")
                    full_response += token
                    if stream_callback:
                        stream_callback(token)
                    if chunk.get("done"):
                        break
    except Exception as e:
        return {"error": str(e), "think": "", "result": {}}

    return parse_response(full_response)


def load_discrepancy_log() -> list:
    os.makedirs(LOG_DIR, exist_ok=True)
    if os.path.exists(DISCREPANCY_LOG):
        with open(DISCREPANCY_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_discrepancy(patient_id: str, predicted: str, actual: str, delta: float):
    """予測と実績のズレをログに記録"""
    log = load_discrepancy_log()
    log.append({
        "timestamp": datetime.now().isoformat(),
        "patient_id": patient_id,
        "predicted_15y_survival": predicted,
        "actual_15y_survival": actual,
        "delta_percent": delta,
        "correction_note": f"AIが{abs(delta):.1f}%{'過大' if delta > 0 else '過小'}評価した事例"
    })
    with open(DISCREPANCY_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    return log


def generate_few_shot_prefix(log: list) -> str:
    """過去のズレから自動Few-Shot修正プレフィックスを生成"""
    if not log:
        return ""
    recent = log[-5:]  # 直近5件
    prefix = "【AIキャリブレーション履歴（過去の予測誤差の自動修正）】\n"
    for entry in recent:
        prefix += f"- {entry['patient_id']}: {entry['correction_note']} (Δ={entry['delta_percent']:+.1f}%)\n"
    prefix += "\n上記の傾向を踏まえ、本予測を慎重に補正せよ。\n\n"
    return prefix


if __name__ == "__main__":
    import sys
    patients_path = os.path.join(os.path.dirname(__file__), "..", "data", "patients.json")
    with open(patients_path, "r", encoding="utf-8") as f:
        patients = json.load(f)

    target_id = sys.argv[1] if len(sys.argv) > 1 else "VRC-001"
    patient = next((p for p in patients if p["patient_id"] == target_id), patients[0])

    print(f"\n🧬 VR-CRC Inference Engine | Patient: {patient['patient_id']}")
    print("=" * 65)

    def stream_print(token):
        print(token, end="", flush=True)

    result = run_inference(patient, stream_callback=stream_print)
    print("\n\n" + "=" * 65)
    print("📊 Structured Output:")
    print(json.dumps(result["result"], ensure_ascii=False, indent=2))
