"""Dark tech-style Tkinter dashboard for vision usage statistics.

Shows how many images were recognized and how many tokens each model consumed:
summary cards, a per-model token-share bar chart, and recent calls.

Usage:
    python scripts/usage_dashboard.py
    python scripts/usage_dashboard.py --screenshot out.png   # Windows: export PNG
"""
import argparse
import sys

import usage_tracker


# ------------------------------------------------------------- dark palette
BG = "#0B1220"          # deep navy background
CARD = "#111A2E"        # card background
CARD2 = "#0E1626"       # alternate row
BORDER = "#1E2A44"      # card border
TEXT = "#E2E8F0"
MUTED = "#8B9BB4"
CYAN = "#22D3EE"
PURPLE = "#818CF8"
GREEN = "#34D399"
ORANGE = "#F59E0B"
SELECT = "#123049"

PROVIDER_COLORS = {
    "doubao": CYAN,
    "openai": GREEN,
    "qwen": PURPLE,
    "zhipu": ORANGE,
    "custom": "#94A3B8",
    "?": "#64748B",
}


def provider_color(name):
    return PROVIDER_COLORS.get(name, "#64748B")


# ---------------------------------------------------------------- helpers
def card(parent, label, accent):
    """A summary card with a glowing accent line."""
    import tkinter as tk
    frame = tk.Frame(parent, bg=CARD, highlightbackground=BORDER,
                     highlightthickness=1, bd=0)
    tk.Label(frame, text=label, bg=CARD, fg=MUTED,
             font=("Microsoft YaHei UI", 9)).pack(anchor="w", padx=16, pady=(10, 2))
    value = tk.Label(frame, text="0", bg=CARD, fg=accent,
                     font=("Segoe UI", 22, "bold"))
    value.pack(anchor="w", padx=16)
    tk.Frame(frame, bg=accent, height=3).pack(fill="x", side="bottom")
    return frame


def style_tree(style, columns, widths, height=8):
    """A dark styled Treeview; returns (tree, scrollbar)."""
    from tkinter import ttk
    tree = ttk.Treeview(columns=columns, show="headings", height=height,
                        style="Dark.Treeview")
    for c, w in zip(columns, widths):
        tree.heading(c, text=c, anchor="center")
        tree.column(c, width=w, anchor="center", stretch=(c == columns[-1]))
    vsb = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    return tree, vsb


def strip_tree_rows(tree):
    """Toggle alternate-row shading for readability."""
    for i, item in enumerate(tree.get_children()):
        tree.tag_configure("odd" if i % 2 else "even", background=CARD2)
        tree.item(item, tags=("odd" if i % 2 else "even",))


# ---------------------------------------------------------------- main UI
def build_ui(root):
    import tkinter as tk
    from tkinter import ttk

    root.configure(bg=BG)
    root.title("Vision Usage Dashboard")
    root.geometry("1080x700")
    root.minsize(960, 620)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure("Dark.Treeview", background=CARD, fieldbackground=CARD,
                    foreground=TEXT, rowheight=26, font=("Microsoft YaHei UI", 9),
                    bordercolor=BORDER)
    style.map("Dark.Treeview",
              background=[("selected", SELECT)],
              foreground=[("selected", TEXT)])
    style.configure("Dark.Treeview.Heading", background="#15203A",
                    foreground=CYAN, relief="flat", font=("Microsoft YaHei UI", 9, "bold"))
    style.map("Dark.Treeview.Heading", background=[("active", "#1B2A4A")])
    style.configure("Dark.TButton", font=("Microsoft YaHei UI", 9),
                    padding=(14, 6), background=CYAN, foreground="#04222B",
                    bordercolor=CYAN)
    style.map("Dark.TButton",
              background=[("active", "#67E8F9")],
              foreground=[("active", "#04222B")])

    # header
    header = tk.Frame(root, bg=BG)
    header.pack(fill="x", padx=18, pady=(14, 6))
    title_row = tk.Frame(header, bg=BG)
    title_row.pack(anchor="w")
    tk.Label(title_row, text="●", bg=BG, fg=GREEN,
             font=("Segoe UI", 11)).pack(side="left")
    tk.Label(title_row, text="  Vision Usage Dashboard", bg=BG, fg=TEXT,
             font=("Microsoft YaHei UI", 16, "bold")).pack(side="left")
    tk.Label(header, text="多模态用量统计 · 数据保存在本地 usage.json · 每 5 秒自动刷新",
             bg=BG, fg=MUTED, font=("Microsoft YaHei UI", 9)).pack(anchor="w", pady=(2, 0))

    # summary cards
    cards = tk.Frame(root, bg=BG)
    cards.pack(fill="x", padx=18, pady=(10, 4))
    card_call = card(cards, "累计调用", CYAN)
    card_img = card(cards, "识别图片", GREEN)
    card_tok = card(cards, "总 Token", ORANGE)
    for c in (card_call, card_img, card_tok):
        c.pack(side="left", expand=True, fill="x", padx=(0, 10))

    # middle: token share chart + per-model table
    middle = tk.Frame(root, bg=BG)
    middle.pack(fill="both", expand=True, padx=18, pady=(8, 4))

    chart_box = tk.Frame(middle, bg=CARD, highlightbackground=BORDER,
                         highlightthickness=1, bd=0)
    chart_box.pack(side="left", fill="both", expand=True, padx=(0, 10))
    tk.Label(chart_box, text="模型 Token 占比", bg=CARD, fg=TEXT,
             font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w", padx=12, pady=(10, 4))
    canvas = tk.Canvas(chart_box, bg=CARD, highlightthickness=0, height=170)
    canvas.pack(fill="both", expand=True, padx=12, pady=(0, 10))

    model_box = tk.Frame(middle, bg=CARD, highlightbackground=BORDER,
                         highlightthickness=1, bd=0)
    model_box.pack(side="right", fill="both", expand=True)
    tk.Label(model_box, text="按模型统计", bg=CARD, fg=TEXT,
             font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w", padx=12, pady=(10, 4))
    model_tree, model_vsb = style_tree(style,
                                       ("Provider", "模型", "调用", "图片", "Token"),
                                       (90, 230, 60, 60, 100), height=6)
    model_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # recent calls
    rec_box = tk.Frame(root, bg=CARD, highlightbackground=BORDER,
                       highlightthickness=1, bd=0)
    rec_box.pack(fill="both", expand=True, padx=18, pady=(4, 10))
    tk.Label(rec_box, text="最近调用", bg=CARD, fg=TEXT,
             font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w", padx=12, pady=(10, 4))
    rec_tree, rec_vsb = style_tree(
        style,
        ("时间", "Provider", "模型", "图片", "输入", "输出", "总 Token", "问题"),
        (130, 80, 220, 45, 70, 70, 80, 220), height=8)
    rec_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # footer
    footer = tk.Frame(root, bg=BG)
    footer.pack(fill="x", padx=18, pady=(0, 10))
    ttk.Button(footer, text="立即刷新", style="Dark.TButton",
               command=lambda: refresh(root, card_call, card_img, card_tok,
                                       model_tree, rec_tree, canvas)).pack(side="left")
    tk.Label(footer, text="切换 Provider 后在此查看各模型用量 · 深色主题 v2",
             bg=BG, fg=MUTED, font=("Microsoft YaHei UI", 9)).pack(side="left", padx=12)
    return card_call, card_img, card_tok, model_tree, rec_tree, canvas


def draw_bars(canvas, per_model, total_tokens):
    """Horizontal token-share bars."""
    canvas.delete("all")
    items = sorted(per_model.items(), key=lambda kv: -kv[1]["tokens"])
    if not items or total_tokens <= 0:
        canvas.create_text(80, 40, anchor="nw", text="暂无数据",
                           fill=MUTED, font=("Microsoft YaHei UI", 10))
        return
    bar_h, gap = 24, 14
    start_y = 8
    for i, ((provider, model), m) in enumerate(items):
        y = start_y + i * (bar_h + gap)
        label = f"{provider} / {model}"
        canvas.create_text(4, y + bar_h / 2, anchor="w", text=label,
                           fill=TEXT, font=("Microsoft YaHei UI", 8))
        w = max(8.0, (m["tokens"] / total_tokens) * 300.0)
        canvas.create_rectangle(4, y, 4 + w, y + bar_h,
                                fill=provider_color(provider), outline="")
        pct = m["tokens"] / total_tokens * 100 if total_tokens else 0
        canvas.create_text(4 + w + 6, y + bar_h / 2, anchor="w",
                           text=f"{m['tokens']:,} ({pct:.1f}%)",
                           fill=TEXT, font=("Microsoft YaHei UI", 8))


def set_card_value(frame, value):
    import tkinter as tk
    text = f"{value:,}"
    for child in frame.winfo_children():
        if isinstance(child, tk.Label) and child.cget("font").endswith("bold"):
            child.configure(text=text)


def refresh(root, card_call, card_img, card_tok, model_tree, rec_tree, canvas):
    data = usage_tracker.summarize()
    set_card_value(card_call, data["calls"])
    set_card_value(card_img, data["total_images"])
    set_card_value(card_tok, data["total_tokens"])

    model_tree.delete(*model_tree.get_children())
    for (provider, model), m in sorted(data["per_model"].items()):
        model_tree.insert("", "end", values=(provider, model, m["calls"], m["images"],
                                             f"{m['tokens']:,}"))
    strip_tree_rows(model_tree)

    rec_tree.delete(*rec_tree.get_children())
    for r in data["records"][-200:][::-1]:
        rec_tree.insert("", "end", values=(
            r["ts"], r["provider"], r["model"], r["images"],
            f"{r['prompt_tokens']:,}", f"{r['completion_tokens']:,}",
            f"{r['total_tokens']:,}", (r["question"] or "")[:22]))
    strip_tree_rows(rec_tree)

    draw_bars(canvas, data["per_model"], data["total_tokens"])
    root.after(5000, refresh, root, card_call, card_img, card_tok,
               model_tree, rec_tree, canvas)


def main():
    import tkinter as tk

    parser = argparse.ArgumentParser()
    parser.add_argument("--screenshot", metavar="OUT.png",
                        help="render and save a PNG, then exit")
    args = parser.parse_args()

    root = tk.Tk()
    card_call, card_img, card_tok, model_tree, rec_tree, canvas = build_ui(root)
    refresh(root, card_call, card_img, card_tok, model_tree, rec_tree, canvas)

    if args.screenshot:
        root.attributes("-topmost", True)
        root.lift()
        root.update()
        root.after(1600, root.update)
        try:
            from PIL import Image
            import ctypes
            from ctypes import wintypes

            class BITMAPINFOHEADER(ctypes.Structure):
                _fields_ = [
                    ("biSize", wintypes.DWORD),
                    ("biWidth", wintypes.LONG),
                    ("biHeight", wintypes.LONG),
                    ("biPlanes", wintypes.WORD),
                    ("biBitCount", wintypes.WORD),
                    ("biCompression", wintypes.DWORD),
                    ("biSizeImage", wintypes.DWORD),
                    ("biXPelsPerMeter", wintypes.LONG),
                    ("biYPelsPerMeter", wintypes.LONG),
                    ("biClrUsed", wintypes.DWORD),
                    ("biClrImportant", wintypes.DWORD),
                ]

            class BITMAPINFO(ctypes.Structure):
                _fields_ = [("bmiHeader", BITMAPINFOHEADER)]

            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32
            hwnd = root.winfo_id()
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            hdc_win = user32.GetWindowDC(hwnd)
            hdc_mem = gdi32.CreateCompatibleDC(hdc_win)
            bmp = gdi32.CreateCompatibleBitmap(hdc_win, w, h)
            gdi32.SelectObject(hdc_mem, bmp)
            user32.PrintWindow(hwnd, hdc_mem, 2)  # PW_RENDERFULLCONTENT
            info = BITMAPINFO()
            info.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
            info.bmiHeader.biWidth = w
            info.bmiHeader.biHeight = -h
            info.bmiHeader.biPlanes = 1
            info.bmiHeader.biBitCount = 32
            buf = ctypes.create_string_buffer(w * h * 4)
            gdi32.GetDIBits(hdc_mem, bmp, 0, h, buf, ctypes.byref(info), 0)
            img = Image.frombuffer("RGB", (w, h), buf, "raw", "BGRX", 0, 1)
            gdi32.DeleteObject(bmp)
            gdi32.DeleteDC(hdc_mem)
            user32.ReleaseDC(hwnd, hdc_win)
            img.save(args.screenshot)
            print("saved", args.screenshot, img.size)
        except Exception as exc:  # pragma: no cover
            print("screenshot failed:", exc)
        root.attributes("-topmost", False)
        root.destroy()
        return 0

    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
