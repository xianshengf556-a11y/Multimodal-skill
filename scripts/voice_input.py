#!/usr/bin/env python3
"""豆包语音听写工具：说话 -> 豆包 ASR 转文字 -> 自动粘贴到当前输入框。

实现"打开 Codex 后说话，文字直接进输入框"的全自动听写。

依赖:
    pip install sounddevice numpy pyperclip pynput requests

环境变量（豆包语音服务）:
    DOUBAO_APP_ID    豆包语音 App ID
    DOUBAO_TOKEN     豆包语音 Access Token
    DOUBAO_CLUSTER   语音服务集群名

用法:
    python voice_input.py [--hotkey <按键>] [--format wav] [--paste]

交互:
    按 F9 开始录音，再按 F9 结束并识别；按 Esc 退出。
    --paste 时识别结果会自动粘贴到当前聚焦的输入框（如 Codex 对话框）。
"""

import argparse
import base64
import io
import os
import sys
import tempfile
import time
import wave

import numpy as np
import pyperclip
import requests
import sounddevice as sd
from pynput import keyboard

from asr_recognize import build_app, query, submit


SAMPLE_RATE = 16000
CHANNELS = 1


class VoiceRecorder:
    """按热键开始/停止录音，保存为 wav 字节。"""

    def __init__(self, hotkey="<f9>"):
        self.hotkey = hotkey.lower()
        self.recording = False
        self.chunks: list[np.ndarray] = []
        self.last_result = ""
        self.should_exit = False

    def start_stop(self):
        if not self.recording:
            self.recording = True
            self.chunks = []
            print("[录音中] 再说一次 F9 结束...", file=sys.stderr)
        else:
            self.recording = False
            print("[已结束] 正在识别...", file=sys.stderr)

    def on_audio(self, indata, frames, time_info, status):
        if self.recording:
            self.chunks.append(indata.copy())

    def audio_to_wav(self) -> bytes:
        data = np.concatenate(self.chunks, axis=0) if self.chunks else np.zeros((1, CHANNELS), dtype=np.float32)
        pcm = (np.clip(data, -1.0, 1.0) * 32767).astype(np.int16)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(pcm.tobytes())
        return buf.getvalue()


def recognize_audio(recorder: VoiceRecorder) -> str:
    app = build_app()
    wav_bytes = recorder.audio_to_wav()
    audio = {"data": base64.b64encode(wav_bytes).decode("utf-8")}
    task_id = submit(app, audio, "wav")
    return query(app, task_id)


def on_press(key, recorder: VoiceRecorder):
    try:
        if key == keyboard.Key.esc:
            recorder.should_exit = True
            return False
    except Exception:
        pass

    try:
        if getattr(key, "name", None) and f"<{key.name.lower()}>" == recorder.hotkey:
            recorder.start_stop()
        elif isinstance(key, keyboard.Key) and f"<{key.name.lower()}>" == recorder.hotkey:
            recorder.start_stop()
    except Exception as exc:
        print(f"按键处理失败: {exc}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="豆包语音听写工具")
    parser.add_argument("--hotkey", default="<f9>", help="录音开关热键，默认 F9")
    parser.add_argument("--paste", action="store_true", help="识别后自动粘贴到当前输入框")
    args = parser.parse_args()

    recorder = VoiceRecorder(hotkey=args.hotkey)

    def on_press_wrapper(key):
        return on_press(key, recorder)

    try:
        listener = keyboard.Listener(on_press=on_press_wrapper)
        listener.start()
    except Exception as exc:
        sys.exit(f"无法启动键盘监听（可能需要管理员权限）: {exc}")

    print("豆包语音听写已启动。按 F9 开始/结束录音，按 Esc 退出。", file=sys.stderr)
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=recorder.on_audio):
        while not recorder.should_exit:
            time.sleep(0.1)
            if not recorder.recording and recorder.chunks:
                try:
                    text = recognize_audio(recorder)
                    recorder.chunks = []
                    recorder.last_result = text
                    print(f"[识别] {text}", file=sys.stderr)
                    if args.paste and text:
                        pyperclip.copy(text)
                        # Ctrl+V 粘贴到当前聚焦输入框（Codex 对话框）
                        from pynput.keyboard import Controller

                        kb = Controller()
                        with kb.pressed(keyboard.Key.ctrl):
                            kb.press("v")
                            kb.release("v")
                except Exception as exc:
                    recorder.chunks = []
                    print(f"[失败] {exc}", file=sys.stderr)

    listener.stop()
    print("已退出。", file=sys.stderr)


if __name__ == "__main__":
    main()
