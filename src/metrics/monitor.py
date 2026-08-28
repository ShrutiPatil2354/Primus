import os
import platform
import subprocess
import time
from collections import deque

import psutil

from src.config import MODEL_NAME, START_TIME, BASE_DIR
from src.core import engine, llm, memory, executor
from src.perception.vision import VISION

CPU_H = deque([0] * 30, maxlen=30)
RAM_H = deque([0] * 30, maxlen=30)
VRAM_H = deque([0] * 30, maxlen=30)
NET_H = deque([0] * 30, maxlen=30)
DISK_H = deque([0] * 30, maxlen=30)
_last_net = None
GPU_STATIC = None


def _nvidia(fmt):
    try:
        out = subprocess.check_output(
            ["nvidia-smi", f"--query-gpu={fmt}", "--format=csv,noheader,nounits"],
            stderr=subprocess.DEVNULL, timeout=2,
        ).decode().strip()
        return [line.split(", ") for line in out.splitlines()] if out else []
    except Exception:
        return []


def gpu_static():
    global GPU_STATIC
    if GPU_STATIC is None:
        rows = _nvidia("name,memory.total")
        if rows:
            name, total = rows[0][0], rows[0][1]
        else:
            name, total = "N/A", "0"
        cores = 3072 if "4060" in name else 2048
        GPU_STATIC = {"name": name, "vram_total": total, "cores": cores}
    return GPU_STATIC


def gpu_dynamic():
    rows = _nvidia("utilization.gpu,memory.used,temperature.gpu,power.draw")
    if rows:
        u, used, temp, power = rows[0]
        return {"util": u, "used": used, "temp": temp, "power": power}
    return {"util": "0", "used": "0", "temp": "0", "power": "0"}


def uptime_str():
    s = int(time.time() - START_TIME)
    return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"


def sparkline(vals, color, w=110, h=26):
    vals = list(vals) or [0, 0]
    mn, mx = min(vals), max(vals)
    rng = (mx - mn) or 1
    pts = []
    for i, v in enumerate(vals):
        x = i * (w / (len(vals) - 1))
        y = h - 3 - ((v - mn) / rng) * (h - 6)
        pts.append(f"{x:.1f},{y:.1f}")
    return (f'<svg width="{w}" height="{h}">'
            f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="2"/></svg>')


def _disk_path():
    drive = os.path.splitdrive(BASE_DIR)[0]
    return f"{drive}\\" if drive else "/"


def sample():
    global _last_net
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()
    try:
        disk = psutil.disk_usage(_disk_path())
    except Exception:
        disk = psutil.disk_usage("/")
    g = gpu_dynamic()
    gs = gpu_static()
    vram_pct = (float(g["used"]) / float(gs["vram_total"])) * 100 if float(gs["vram_total"]) else 0

    net_mbps = 0.0
    try:
        io = psutil.net_io_counters()
        now = time.time()
        if _last_net is not None:
            dt = max(0.1, now - _last_net[0])
            net_mbps = round(((io.bytes_recv + io.bytes_sent) - _last_net[1]) * 8 / dt / 1e6, 1)
        _last_net = (now, io.bytes_recv + io.bytes_sent)
    except Exception:
        pass

    CPU_H.append(cpu)
    RAM_H.append(ram.percent)
    VRAM_H.append(vram_pct)
    NET_H.append(net_mbps)
    DISK_H.append(disk.percent)

    return {"cpu": cpu, "ram": ram, "disk": disk, "gpu": g, "gs": gs,
            "vram_pct": vram_pct, "net": net_mbps}


def _card(title, value, sub, color, spark):
    return f'''
    <div style="flex:1;min-width:180px;background:#080f1b;border:1px solid #1c3252;border-radius:12px;padding:14px 16px;box-sizing:border-box">
      <div style="color:#94a3b8;font-size:.74rem;font-weight:600">{title}</div>
      <div style="color:{color};font-size:1.5rem;font-weight:800;margin:2px 0">{value}</div>
      <div style="color:#64748b;font-size:.72rem">{sub}</div>{spark}
    </div>'''


def header_html():
    gs = gpu_static()
    chip = lambda icon, k, v: f'''
    <div style="display:flex;align-items:center;gap:8px;background:#080f1b;border:1px solid #1c3252;border-radius:10px;padding:8px 14px">
      <span>{icon}</span>
      <div><div style="color:#94a3b8;font-size:.68rem">{k}</div>
      <div style="color:#ffffff;font-size:.82rem;font-weight:700">{v}</div></div>
    </div>'''
    return f'''
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:14px;width:100%">
      <div>
        <div style="font-size:1.6rem;font-weight:800;color:#ffffff">PRIMUS
          <span style="background:#2563eb;color:#ffffff;font-size:.65rem;border-radius:20px;padding:3px 10px;vertical-align:middle;font-weight:800">STUDIO</span>
        </div>
        <div style="color:#94a3b8;font-size:.80rem">Zero-Prior • Tabula Rasa • Autonomous Cognitive Core</div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        {chip("🖥", "OS", f"{platform.system()} {platform.release()}")}
        {chip("🟢", "GPU", gs['name'])}
        {chip("🧠", "LLM", MODEL_NAME)}
        {chip("⚙", "Runner", "Ollama")}
        {chip("⏱", "Uptime", uptime_str())}
      </div>
    </div>'''


def stats_html(m):
    return f'''
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:14px;width:100%;box-sizing:border-box">
      {_card("CPU Usage", f"{m['cpu']:.0f}%", "", "#38bdf8", sparkline(CPU_H, "#38bdf8"))}
      {_card("RAM Usage", f"{m['ram'].used / 1024 ** 3:.1f} GB", f"{m['ram'].percent:.0f}%", "#a855f7", sparkline(RAM_H, "#a855f7"))}
      {_card("VRAM Usage", f"{float(m['gpu']['used']) / 1024:.1f} GB", f"{m['vram_pct']:.0f}%", "#22c55e", sparkline(VRAM_H, "#22c55e"))}
      {_card("GPU Temp", f"{m['gpu']['temp']}°C", "Normal", "#f97316", sparkline(VRAM_H, "#f97316"))}
      {_card("Disk Usage", f"{m['disk'].percent:.0f}%", f"{m['disk'].total / 1024 ** 3:.0f} GB", "#e2e8f0", sparkline(DISK_H, "#38bdf8"))}
    </div>'''


def _kv(k, v, color="#ffffff"):
    return f'''<div style="display:flex;justify-content:space-between;margin:6px 0;font-size:.80rem">
      <span style="color:#94a3b8">{k}</span><span style="color:{color};font-weight:700">{v}</span></div>'''


def panels_html(m):
    st = memory.stats()
    ex = executor.stats()
    try:
        loadavg = ", ".join(f"{x:.2f}" for x in os.getloadavg())
    except (AttributeError, OSError):
        loadavg = "Not available on Windows"
    return f'''
    <div style="display:flex;gap:14px;flex-wrap:wrap;width:100%;box-sizing:border-box">
      <div style="flex:1;min-width:260px;background:#080f1b;border:1px solid #1c3252;border-radius:12px;padding:14px 16px;box-sizing:border-box">
        <div style="color:#38bdf8;font-weight:800;font-size:.88rem;margin-bottom:8px">AI &amp; Model Metrics</div>
        {_kv("Model", MODEL_NAME)}
        {_kv("Context Length", "4,096 tokens")}
        {_kv("Inference Time", f"{llm.LAST['inference_ms']} ms")}
        {_kv("Token/sec", llm.LAST['tokens_per_sec'])}
        {_kv("Confidence (Avg.)", st['avg_confidence'])}
        {_kv("Skills Stored", st['skills'])}
        {_kv("Engine", engine.status())}
      </div>
      <div style="flex:1;min-width:260px;background:#080f1b;border:1px solid #1c3252;border-radius:12px;padding:14px 16px;box-sizing:border-box">
        <div style="color:#22c55e;font-weight:800;font-size:.88rem;margin-bottom:8px">System Performance</div>
        {_kv("Latency (End-to-End)", f"{llm.LAST['latency_ms']} ms", "#ffffff")}
        {_kv("FPS (Camera)", VISION.fps)}
        {_kv("Network (I/O)", f"{m['net']} Mbps")}
        {_kv("Power Usage", f"{m['gpu']['power']} W")}
        {_kv("Uptime", uptime_str())}
        {_kv("Processes", len(psutil.pids()))}
        {_kv("Load Average", loadavg)}
      </div>
      <div style="flex:1;min-width:260px;background:#080f1b;border:1px solid #1c3252;border-radius:12px;padding:14px 16px;box-sizing:border-box">
        <div style="color:#a855f7;font-weight:800;font-size:.88rem;margin-bottom:8px">Perception &amp; Memory</div>
        {_kv("Objects Detected", len(VISION.labels))}
        {_kv("Hand Tracking", f"{VISION.hands} hands")}
        {_kv("YOLO Confidence", VISION.conf)}
        {_kv("Episodes", st['episodes'])}
        {_kv("Semantic Facts", st['facts'])}
        {_kv("Action Success", ex['success_rate'])}
        {_kv("Reward (RL)", f"+{ex['reward']}" if ex['reward'] >= 0 else ex['reward'], "#ffffff")}
      </div>
    </div>'''


def hardware_html():
    gs = gpu_static()
    ram_total = psutil.virtual_memory().total / 1024 ** 3
    try:
        disk_total = psutil.disk_usage(_disk_path()).total / 1024 ** 3
    except Exception:
        disk_total = psutil.disk_usage("/").total / 1024 ** 3
    try:
      if platform.system() == "Windows":
        cpu_name = platform.processor() or platform.machine() or "CPU"
      else:
        with open("/proc/cpuinfo") as f:
          cpu_name = next(l.split(":", 1)[1].strip() for l in f if "model name" in l)
    except (OSError, StopIteration):
      cpu_name = platform.machine() or "CPU"
    cell = lambda k, v, c="#e5e7eb": f'''
      <div style="flex:1;min-width:120px"><div style="color:#8b96ab;font-size:.68rem">{k}</div>
      <div style="color:{c};font-size:.8rem;font-weight:700">{v}</div></div>'''
    return f'''
    <div style="display:flex;gap:14px;flex-wrap:wrap;background:rgba(255,255,255,0.07);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.16);border-radius:12px;padding:12px 14px;margin-top:12px">
      {cell("GPU", gs['name'], "#ffffff")}
      {cell("CUDA Cores", f"{gs['cores']:,}")}
      {cell("VRAM", f"{float(gs['vram_total']) / 1024:.0f} GB GDDR6")}
      {cell("CPU", cpu_name)}
      {cell("RAM", f"{ram_total:.0f} GB")}
      {cell("Storage", f"{disk_total:.0f} GB")}
    </div>'''
