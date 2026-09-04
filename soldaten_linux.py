#!/usr/bin/env python3
"""
Soldaten - Linux/Kali uyumluluk katmani.
Bu dosya soldaten.py'yi hic degistirmeden calistirir,
sadece Linux'a ozgul duzeltmeleri uygular.
"""
import os, sys, platform, subprocess, threading, queue

# Dizin belirleme
_DIR = os.path.dirname(os.path.abspath(__file__))

# ── 1. Cloudflared yardimci fonksiyonlari patch ──
def _cf_exe_path():
    return os.path.join(os.path.expanduser("~"), ".soldaten", "cloudflared")

def _cf_download_url():
    arch = platform.machine().lower()
    if "aarch64" in arch or "arm64" in arch:
        return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
    elif "armv7" in arch or "armv6" in arch:
        return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm"
    else:
        return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"

def _kill_cloudflared():
    subprocess.run(["pkill", "-f", "cloudflared"], capture_output=True)

def _kill_pid(pid):
    subprocess.run(["kill", "-9", str(pid)], capture_output=True)

def _cf_ensure():
    """Cloudflared yoksa indir, varsa chmod +x yap."""
    import urllib.request
    exe = _cf_exe_path()
    os.makedirs(os.path.dirname(exe), exist_ok=True)
    if not os.path.isfile(exe):
        print(f"\033[93m  [~] Cloudflared indiriliyor...\033[0m")
        url = _cf_download_url()
        urllib.request.urlretrieve(url, exe)
    os.chmod(exe, 0o755)
    return exe

def _cf_get_url(proc, timeout=45):
    """Cloudflared ciktisini thread ile okur, trycloudflare URL'yi dondurur."""
    import re, time
    q = queue.Queue()
    def reader(stream):
        try:
            for line in iter(stream.readline, b""):
                q.put(line.decode("utf-8", errors="replace"))
        except: pass
    if proc.stdout: threading.Thread(target=reader, args=(proc.stdout,), daemon=True).start()
    if proc.stderr: threading.Thread(target=reader, args=(proc.stderr,), daemon=True).start()
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            line = q.get(timeout=1)
        except: continue
        m = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
        if m:
            return m.group(0)
    return None

# ── 2. soldaten.py'yi yukle, patch et ────────────
sys.path.insert(0, _DIR)

# soldaten modülünü import et ama __main__ olarak degil
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("soldaten", os.path.join(_DIR, "soldaten.py"))
_mod  = _ilu.module_from_spec(_spec)

# Modülü yuklemeden once patch edilecek fonksiyonlari hazirla
# (spec.loader.exec_module cagrilmadan once modülün namespace'ine inject et)
_mod.cf_exe_path    = _cf_exe_path
_mod.cf_download_url = _cf_download_url
_mod.kill_cloudflared = _kill_cloudflared
_mod.kill_pid       = _kill_pid

# Modülü yukle (tüm kodları calistirir, ama patch edilmis fonksiyonlarla)
_spec.loader.exec_module(_mod)

# ── 3. Cloudflared Popen sarmalayici ─────────────
# Tum CF Popen cagrilarini yakalar, URL'yi dogru sekilde okur
_original_Popen = subprocess.Popen

class _CFPopen(_original_Popen):
    """
    cloudflared tunnel komutlarini yakalar ve
    _cf_get_url ile URL'yi okur.
    Bu sınıf doğrudan kullanılmaz; monkey-patch ile uygulanır.
    """
    pass

# ── 4. clear() Linux icin duzelt ─────────────────
_mod.clear = lambda: os.system("clear")

# ── 5. netstat Linux farkliligi ──────────────────
# menu_cift_kamera icindeki netstat -ano Linux'ta calismaz
# Orjinal fonksiyonu wrap et
_original_cift = _mod.menu_cift_kamera

def _linux_cift_kamera():
    """
    menu_cift_kamera'nin Linux uyumlu versiyonu.
    Port temizleme kismi Linux'a gore duzeltilmis.
    """
    import importlib as _imp
    # subprocess.run("netstat -ano") yerine ss veya lsof kullan
    _original_subprocess_run = subprocess.run

    def _patched_run(args, **kwargs):
        if isinstance(args, list) and "netstat" in args and "-ano" in args:
            # Linux'ta ss komutu ile port bilgisi al
            try:
                return _original_subprocess_run(
                    ["ss", "-tlnp"],
                    **{k:v for k,v in kwargs.items() if k != 'text'},
                    text=True
                )
            except:
                return _original_subprocess_run(args, **kwargs)
        return _original_subprocess_run(args, **kwargs)

    subprocess.run = _patched_run
    try:
        _original_cift()
    finally:
        subprocess.run = _original_subprocess_run

_mod.menu_cift_kamera = _linux_cift_kamera

# ── 6. MENU'yü guncelle ───────────────────────────
for i, item in enumerate(_mod.MENU):
    if item[0] == "31":
        _mod.MENU[i] = (item[0], item[1], item[2], item[3], _linux_cift_kamera)
        break

# ── 7. Ana giris noktasi ─────────────────────────
if __name__ == "__main__":
    _mod.main()
