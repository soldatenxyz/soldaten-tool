#!/usr/bin/env python3
"""
Soldaten - Linux/Kali giris noktasi.
soldaten.py'yi hic degistirmez, sadece Linux duzeltmelerini uygular.
"""
import os, sys, platform, subprocess, threading, queue, time

_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Linux cloudflared yardimcilari ───────────────
def _cf_exe_path():
    return os.path.join(os.path.expanduser("~"), ".soldaten", "cloudflared")

def _cf_download_url():
    arch = platform.machine().lower()
    if "aarch64" in arch or "arm64" in arch:
        return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
    elif "armv7" in arch or "armv6" in arch:
        return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm"
    return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"

def _kill_cloudflared():
    subprocess.run(["pkill", "-f", "cloudflared"], capture_output=True)

def _kill_pid(pid):
    subprocess.run(["kill", "-9", str(pid)], capture_output=True)

# ── soldaten.py'yi oku ve exec et ────────────────
_src_path = os.path.join(_DIR, "soldaten.py")
with open(_src_path, "r", encoding="utf-8") as _f:
    _src = _f.read()

# Linux patch'lerini kaynak koda enjekte et
_patches = """
# ── LINUX PATCH (soldaten_linux.py tarafindan enjekte edildi) ──
import os as _os_lp, platform as _plat_lp, subprocess as _sub_lp
import threading as _thr_lp, queue as _q_lp, time as _time_lp

IS_WINDOWS = False

def cf_exe_path():
    return _os_lp.path.join(_os_lp.path.expanduser("~"), ".soldaten", "cloudflared")

def cf_download_url():
    arch = _plat_lp.machine().lower()
    if "aarch64" in arch or "arm64" in arch:
        return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
    elif "armv7" in arch or "armv6" in arch:
        return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm"
    return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"

def kill_cloudflared():
    _sub_lp.run(["pkill", "-f", "cloudflared"], capture_output=True)

def kill_pid(pid):
    _sub_lp.run(["kill", "-9", str(pid)], capture_output=True)

def clear():
    _os_lp.system("clear")

def animated_banner():
    \"\"\"Linux'ta segfault'u onlemek icin sadece banner() cagir.\"\"\"
    clear()
    banner()

# ── LINUX PATCH SONU ──
"""

# Patch'i kaynak kodun basina ekle (importlardan sonra)
# IS_WINDOWS ve fonksiyon tanimlamalarini override et
_patched_src = _src + "\n" + _patches

# Global namespace olustur ve calistir
_globs = {"__name__": "__not_main__", "__file__": _src_path}
try:
    exec(compile(_patched_src, _src_path, "exec"), _globs)
except SystemExit:
    pass
except Exception as _e:
    print(f"\n  [HATA] soldaten.py yuklenemedi: {_e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

# Patch edilmis fonksiyonlari guncelle
_globs["IS_WINDOWS"] = False
_globs["cf_exe_path"] = _cf_exe_path
_globs["cf_download_url"] = _cf_download_url
_globs["kill_cloudflared"] = _kill_cloudflared
_globs["kill_pid"] = _kill_pid
_globs["clear"] = lambda: os.system("clear")

# animated_banner'i guveli versiyonla degistir
def _safe_banner():
    os.system("clear")
    # Banner ASCII karakterlerle goster (segfault'u onle)
    GREEN  = "\033[92m"
    DGREEN = "\033[32m"
    WHITE  = "\033[97m"
    GRAY   = "\033[90m"
    R      = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    print()
    print(f"  {GREEN}{'═'*62}{R}")
    print(f"  {BOLD}{GREEN}  SOLDATEN{R}  {DIM}{WHITE}Gizlilik & Kimlik Koruma Araci{R}")
    print(f"  {GREEN}{'═'*62}{R}")
    print(f"\n  {DIM}{WHITE}{'·'*24}  Linux / Kali  {'·'*24}{R}")
    print(f"  {GREEN}{'═'*62}{R}\n")

_globs["animated_banner"] = _safe_banner

# ── netstat -ano Linux uyumu ──────────────────────
# menu_cift_kamera icindeki netstat -ano yerine ss kullan
_orig_menu_cift = _globs.get("menu_cift_kamera")
if _orig_menu_cift:
    _orig_sub_run = subprocess.run
    def _linux_cift():
        def _patched_run(args, **kwargs):
            if isinstance(args, list) and "netstat" in args:
                try:
                    return _orig_sub_run(["ss", "-tlnp"], capture_output=True, text=True)
                except:
                    pass
                # netstat yoksa bos sonuc don
                import subprocess as _s
                class _FakeResult:
                    stdout = ""; returncode = 0
                return _FakeResult()
            return _orig_sub_run(args, **kwargs)
        subprocess.run = _patched_run
        _globs["subprocess"].run = _patched_run
        try:
            _orig_menu_cift()
        finally:
            subprocess.run = _orig_sub_run
            _globs["subprocess"].run = _orig_sub_run
    _globs["menu_cift_kamera"] = _linux_cift
    # MENU'yu guncelle
    if "MENU" in _globs:
        for _i, _item in enumerate(_globs["MENU"]):
            if _item[0] == "31":
                _globs["MENU"][_i] = (_item[0], _item[1], _item[2], _item[3], _linux_cift)
                break

# ── Ana giris ────────────────────────────────────
if __name__ == "__main__":
    if "main" not in _globs:
        print("Hata: main() fonksiyonu bulunamadi.")
        sys.exit(1)
    _globs["main"]()
