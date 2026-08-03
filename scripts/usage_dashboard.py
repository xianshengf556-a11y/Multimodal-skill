"""Tkinter dashboard showing how many images were recognized and how many
tokens each model consumed. Launch with:  python scripts/usage_dashboard.py

Optional:  python scripts/usage_dashboard.py --screenshot out.png
(Windows only; renders the window and saves a PNG for documentation.)
"""
import argparse
import sys

import usage_tracker


def build_tree(parent, cols, widths):
    from tkinter import ttk
    tree = ttk.Treeview(parent, columns=cols, show="headings", height=12)
    for c, w in zip(cols, widths):
        tree.heading(c, text=c)
        tree.column(c, width=w, anchor="center")
    vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    return tree, vsb


def refresh(root, summary_label, model_tree, record_tree):
    data = usage_tracker.summarize()
    summary_label.config(
        text=(
            f"  总调用次数: {data['calls']}     "
            f"识别图片数: {data['total_images']}     "
            f"总 Token: {data['total_tokens']}"
        )
    )
    model_tree.delete(*model_tree.get_children())
    for (provider, model), m in sorted(data["per_model"].items()):
        model_tree.insert("", "end", values=(provider, model, m["calls"], m["images"], m["tokens"]))
    record_tree.delete(*record_tree.get_children())
    for r in data["records"][-200:]:
        record_tree.insert(
            "", "end",
            values=(r["ts"], r["provider"], r["model"], r["images"],
                    r["prompt_tokens"], r["completion_tokens"], r["total_tokens"],
                    (r["question"] or "")[:24]),
        )
    root.after(5000, refresh, root, summary_label, model_tree, record_tree)


def main():
    import tkinter as tk
    from tkinter import ttk

    parser = argparse.ArgumentParser()
    parser.add_argument("--screenshot", metavar="OUT.png", help="render and save a PNG, then exit")
    args = parser.parse_args()

    root = tk.Tk()
    root.title("Vision Usage Dashboard")
    root.geometry("980x620")

    summary_label = tk.Label(root, text="加载中...", anchor="w", font=("Microsoft YaHei UI", 12))
    summary_label.pack(fill="x", padx=10, pady=(10, 4))

    top = ttk.Frame(root)
    top.pack(fill="x", padx=10)
    ttk.Label(top, text="按模型统计", font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w")
    model_cols = ("Provider", "模型", "调用次数", "图片数", "Token")
    model_tree, model_vsb = build_tree(top, model_cols, (110, 240, 90, 90, 120))
    model_tree.pack(side="left", fill="both", expand=True)
    model_vsb.pack(side="right", fill="y")

    bottom = ttk.Frame(root)
    bottom.pack(fill="both", expand=True, padx=10, pady=(10, 4))
    ttk.Label(bottom, text="最近调用记录", font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w")
    rec_cols = ("时间", "Provider", "模型", "图片", "输入Token", "输出Token", "总Token", "问题")
    record_tree, rec_vsb = build_tree(bottom, rec_cols, (130, 90, 230, 55, 90, 90, 90, 220))
    record_tree.pack(side="left", fill="both", expand=True)
    rec_vsb.pack(side="right", fill="y")

    refresh(root, summary_label, model_tree, record_tree)

    if args.screenshot:
        root.update()
        root.after(800, root.update)
        try:
            from PIL import ImageGrab
            x = root.winfo_rootx()
            y = root.winfo_rooty()
            w = root.winfo_width()
            h = root.winfo_height()
            ImageGrab.grab(bbox=(x, y, x + w, y + h)).save(args.screenshot)
            print("saved", args.screenshot)
        except Exception as exc:  # pragma: no cover
            print("screenshot failed:", exc)
        root.destroy()
        return 0

    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
