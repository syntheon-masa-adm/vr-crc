#!/usr/bin/env python3
"""
VR-CRC Phase 4: Light-weight Backend Server
- Serves the Single-File Web UI
- Proxies requests to local Ollama API to handle CORS and streaming
- Handles Feedback writing to discrepancy_log.json
"""

from flask import Flask, request, Response, send_file, jsonify
import urllib.request
import json
import os

app = Flask(__name__)

# Paths
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(WORKSPACE_DIR, "logs")
DISCREPANCY_LOG = os.path.join(LOG_DIR, "discrepancy_log.json")
OLLAMA_API = "http://localhost:11434/api/generate"
MODEL_NAME = "deepseek-r1:8b"

SYSTEM_PROMPT = """あなたは世界最高峰の臨床腫瘍医（大腸がん専門）であり、最先端内視鏡AIの思想とASCOガイドラインを完全にマスターしたAIです。
入力された患者の多次元特徴量ベクトルを、解剖学的再発リスク、左右差（Sidedness）による生物学的悪性度、遺伝子変異（RAS/BRAF/MMR）、TNTおよびロボット手術の生存ベネフィットの観点から冷徹に分析しなさい。

1. 【潜在空間と思考の連動】
   必ず最初に <think> タグの内部で、臨床ガイドラインや大規模疫学データの傾向を踏まえた医師の「直感的な違和感」「リスクの嗅覚」「長考プロセス」を、思考が変遷していく実況中継形式で日本語で詳細に書き出しなさい。

2. <think> の外側には、厳密に以下のJSON構造のみを出力しなさい：
{
  "predicted_15y_survival_rate": "XX%",
  "estimated_recurrence_risk": "Low/Moderate/High(XX%)",
  "estimated_distant_metastasis_risk": "Low/Moderate/High(XX%)",
  "key_clinical_reasoning": "（150文字以内の日本語で決定的要因を記述）"
}"""

def generate_few_shot_context():
    """discrepancy_logからキャリブレーション情報を取得してプロンプトに埋め込む"""
    if not os.path.exists(DISCREPANCY_LOG):
        return ""
    try:
        with open(DISCREPANCY_LOG, "r", encoding="utf-8") as f:
            logs = json.load(f)
            if not logs: return ""
            recent = logs[-3:] # 直近3件のフィードバック
            context = "【過去のキャリブレーション実績（以下を参考に予測を補正せよ）】\n"
            for log in recent:
                context += f"- 予測 {log['predicted']}% に対し、実績は {log['actual']}% でした (誤差 {log['delta']}%)\n"
            return context + "\n"
    except:
        return ""

@app.route('/')
def serve_ui():
    """単一ファイルUIを配信"""
    return send_file('index.html')

@app.route('/api/predict', methods=['POST'])
def proxy_predict():
    """Ollama APIへのリクエストをプロキシし、ストリーミングでクライアントへ返す"""
    data = request.json
    
    # プロンプトの組み立て
    calibration = generate_few_shot_context()
    
    patient_info = f"""
【原発部位】: {data.get('location', '')}（{data.get('sidedness', '')}）
【TNM分類】: T{data.get('T','')} N{data.get('N','')} M{data.get('M','')}
【遺伝子】: RAS={data.get('RAS','')}, BRAF={data.get('BRAF','')}, MMR={data.get('MMR','')}
【治療】:
- 術式: {data.get('surgery','')}
- 術前CRT: {'あり' if data.get('preop_crt') else 'なし'}
- TNT療法: {'あり' if data.get('tnt') else 'なし'}
- 術後化学療法/分子標的薬: {data.get('adjuvant','') or 'なし'}
"""
    
    prompt = f"{SYSTEM_PROMPT}\n\n{calibration}\n---患者データ---\n{patient_info}"

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True,
        "options": {"temperature": 0.2, "num_predict": 2048}
    }

    req = urllib.request.Request(
        OLLAMA_API, 
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    def generate():
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                for line in resp:
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        if "response" in chunk:
                            yield chunk["response"]
        except Exception as e:
            yield f"\n\n<Ollama Error: {str(e)}>"

    return Response(generate(), mimetype="text/plain")

@app.route('/api/feedback', methods=['POST'])
def save_feedback():
    """フィードバック（ズレ）をローカルファイルに記録"""
    data = request.json
    os.makedirs(LOG_DIR, exist_ok=True)
    
    logs = []
    if os.path.exists(DISCREPANCY_LOG):
        try:
            with open(DISCREPANCY_LOG, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except:
            pass
            
    logs.append(data)
    
    with open(DISCREPANCY_LOG, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
        
    return jsonify({"status": "success", "message": "Feedback saved to discrepancy_log.json"})

if __name__ == '__main__':
    print(f"🚀 VR-CRC Co-Pilot UI Server Started!")
    print(f"🌐 以下のURLにブラウザでアクセスしてください: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
