#!/bin/bash
# ═══════════════════════════════════════════════════
#  SOLDATEN - Linux / Kali Otomatik Kurulum
#  Kullanim: chmod +x setup.sh && ./setup.sh
# ═══════════════════════════════════════════════════

GREEN='\033[92m'
RED='\033[91m'
YELLOW='\033[93m'
CYAN='\033[96m'
R='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

clear
echo ""
echo -e "  ${GREEN}╔══════════════════════════════════════════╗${R}"
echo -e "  ${GREEN}║         SOLDATEN - Kurulum               ║${R}"
echo -e "  ${GREEN}╚══════════════════════════════════════════╝${R}"
echo ""

# ── 1. Python3 ──────────────────────────────────
echo -e "  ${YELLOW}[1/4] Python3 kontrol ediliyor...${R}"

if ! command -v python3 &>/dev/null; then
    echo -e "  ${RED}[-] Python3 bulunamadi. Kuruluyor...${R}"
    sudo apt update -qq
    sudo apt install -y python3 python3-pip python3-venv python3-full 2>/dev/null || \
    sudo apt install -y python3 python3-pip python3-venv 2>/dev/null
fi

# python3-venv ayrıca kontrol et (Kali'de bazen eksik olabilir)
if ! python3 -m venv --help &>/dev/null; then
    echo -e "  ${YELLOW}[~] python3-venv kuruluyor...${R}"
    sudo apt install -y python3-venv python3-full 2>/dev/null || \
    sudo apt install -y python3-venv 2>/dev/null
fi

echo -e "  ${GREEN}[+] $(python3 --version) hazir${R}"
echo ""

# ── 2. Sanal ortam (venv) ───────────────────────
echo -e "  ${YELLOW}[2/4] Sanal ortam kuruluyor...${R}"

if [ ! -d "$SCRIPT_DIR/venv" ]; then
    python3 -m venv "$SCRIPT_DIR/venv"
    if [ $? -ne 0 ]; then
        echo -e "  ${RED}[-] Sanal ortam olusturulamadi!${R}"
        echo -e "  ${YELLOW}    sudo apt install python3-venv python3-full${R}"
        exit 1
    fi
    echo -e "  ${GREEN}[+] Sanal ortam olusturuldu.${R}"
else
    echo -e "  ${GREEN}[+] Sanal ortam zaten mevcut.${R}"
fi

# Aktifleştir
source "$SCRIPT_DIR/venv/bin/activate"
pip install --upgrade pip --quiet 2>/dev/null
echo ""

# ── 3. Python modülleri ─────────────────────────
echo -e "  ${YELLOW}[3/4] Python modulleri yukleniyor...${R}"
echo ""

MODULES="requests stem PySocks cryptography qrcode pillow colorama"
FAILED=0

for mod in $MODULES; do
    printf "  %-20s" "$mod"
    pip install "$mod" --quiet 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}OK${R}"
    else
        echo -e "${RED}HATA${R}"
        FAILED=1
    fi
done

if [ $FAILED -eq 1 ]; then
    echo ""
    echo -e "  ${RED}[!] Bazi moduller yuklenemedi. Internet baglantini kontrol et.${R}"
fi
echo ""

# ── 4. Cloudflared ──────────────────────────────
echo -e "  ${YELLOW}[4/4] Cloudflared kuruluyor...${R}"

CF_DIR="$HOME/.soldaten"
CF_EXE="$CF_DIR/cloudflared"
mkdir -p "$CF_DIR"

if [ ! -f "$CF_EXE" ]; then
    ARCH=$(uname -m)
    case "$ARCH" in
        x86_64)  CF_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64" ;;
        aarch64) CF_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64" ;;
        armv7l)  CF_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm" ;;
        *)       CF_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64" ;;
    esac

    echo -e "  ${YELLOW}[~] $ARCH mimari icin indiriliyor (~30MB)...${R}"
    wget -q --show-progress "$CF_URL" -O "$CF_EXE" && chmod +x "$CF_EXE"

    if [ -f "$CF_EXE" ]; then
        echo -e "  ${GREEN}[+] Cloudflared hazir. Hesap/token gerekmez.${R}"
    else
        echo -e "  ${RED}[-] Cloudflared indirilemedi. QR internet modu calismazsa tekrar dene.${R}"
    fi
else
    echo -e "  ${GREEN}[+] Cloudflared zaten yuklu.${R}"
fi
echo ""

# ── run.sh oluştur ──────────────────────────────
cat > "$SCRIPT_DIR/run.sh" << RUNEOF
#!/bin/bash
cd "\$(dirname "\${BASH_SOURCE[0]}")"
source venv/bin/activate
python soldaten.py
RUNEOF
chmod +x "$SCRIPT_DIR/run.sh"

# ── Özet ────────────────────────────────────────
echo -e "  ${GREEN}╔══════════════════════════════════════════╗${R}"
echo -e "  ${GREEN}║      Kurulum Tamamlandi!                 ║${R}"
echo -e "  ${GREEN}╚══════════════════════════════════════════╝${R}"
echo ""
echo -e "  ${CYAN}Baslatmak icin:${R}"
echo -e "  ${GREEN}  ./run.sh${R}"
echo ""

read -rp "  Soldaten simdi baslatilsin mi? (e/h): " BASLAT
if [[ "$BASLAT" =~ ^[eE]$ ]]; then
    python soldaten.py
fi
