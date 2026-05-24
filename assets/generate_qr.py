#!/usr/bin/env python3
"""
VR-CRC Phase 5: QR Code Generator
高解像度QRコード画像をワークスペース内に自動生成する
"""

import os
import sys

def install_and_import(package, import_name=None):
    import importlib
    import subprocess
    name = import_name or package
    try:
        return importlib.import_module(name)
    except ImportError:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])
        return importlib.import_module(name)

qrcode = install_and_import("qrcode")
PIL    = install_and_import("Pillow", "PIL")
from PIL import Image, ImageDraw, ImageFont

# ── Configuration ──────────────────────────────────────────────────
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_PATH   = os.path.join(WORKSPACE_DIR, "assets", "qr_vrcrc.png")

# QR content: local workspace path + GitHub URL
QR_CONTENT = "\n".join([
    "VR-CRC | Visible Reasoning for Colorectal Cancer",
    f"Local Workspace: {WORKSPACE_DIR}",
    "GitHub: https://github.com/syntheon-masa-adm/vr-crc",
    "Launch: python3 src/app.py  →  http://localhost:5050",
])

# ── QR Code Generation ──────────────────────────────────────────────
def make_qr(content: str, output_path: str, box_size: int = 14, border: int = 4):
    """カスタムスタイルのQRコードを生成し保存する"""

    # 1. QRコード本体の生成
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 高耐障害性
        box_size=box_size,
        border=border,
    )
    qr.add_data(content)
    qr.make(fit=True)

    # カスタムカラー（ダークテーマに合わせた配色）
    QR_DARK  = (30,  27,  75)   # indigo-950 (dark modules)
    QR_LIGHT = (248, 250, 252)  # slate-50   (light modules)

    img = qr.make_image(fill_color=QR_DARK, back_color=QR_LIGHT).convert("RGB")
    w, h = img.size

    # 2. タイトルバナーを追加
    BANNER_H = 60
    canvas = Image.new("RGB", (w, h + BANNER_H), QR_DARK)
    canvas.paste(img, (0, BANNER_H))

    draw = ImageDraw.Draw(canvas)

    # テキスト描画（フォントはシステム依存のため安全にデフォルトにフォールバック）
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
        font_sub   = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub   = font_title

    title_text = "⚗️  VR-CRC"
    sub_text   = "Visible Reasoning for Colorectal Cancer"

    # Center texts
    t_bbox = draw.textbbox((0, 0), title_text, font=font_title)
    s_bbox = draw.textbbox((0, 0), sub_text,   font=font_sub)
    t_x = (w - (t_bbox[2] - t_bbox[0])) // 2
    s_x = (w - (s_bbox[2] - s_bbox[0])) // 2

    draw.text((t_x, 6),  title_text, fill=(167, 139, 250), font=font_title)  # purple-400
    draw.text((s_x, 36), sub_text,   fill=(148, 163, 184), font=font_sub)    # slate-400

    # 3. 保存
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    canvas.save(output_path, "PNG", dpi=(300, 300))
    print(f"✅ QR Code saved → {output_path}")
    print(f"   Size: {canvas.size[0]}×{canvas.size[1]}px @ 300 DPI")
    return output_path


if __name__ == "__main__":
    print("🔲 VR-CRC QR Code Generator")
    print("=" * 50)
    print(f"📋 QR Content:\n{QR_CONTENT}\n")
    result = make_qr(QR_CONTENT, OUTPUT_PATH)
    print(f"\n🎯 Complete. Open the image:\n   open \"{result}\"")
