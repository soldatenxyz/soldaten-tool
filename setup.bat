@echo off
setlocal enabledelayedexpansion
title SOLDATEN - Otomatik Kurulum
color 0A
chcp 65001 >nul 2>&1

cls
echo.
echo  ============================================================
echo    SOLDATEN - Otomatik Kurulum
echo    Her sey otomatik kurulur, hicbir sey elle yapilmaz
echo  ============================================================
echo.
echo  Kurulacaklar:
echo    [1] Python 3.11
echo    [2] Python modulleri
echo    [3] Tor Browser  (IP degistirme)
echo    [4] Cloudflared  (QR internet modu - hesap/token YOK)
echo    [5] Windows Defender imza guncelleme
echo    [6] Port ve process temizligi
echo    [7] Masaustu kisayolu
echo.
echo  Devam etmek icin bir tusa basin...
pause >nul
cls

:: ─────────────────────────────────────────────
::  ADIM 1 — PYTHON
:: ─────────────────────────────────────────────
echo.
echo  [1/7] Python kontrol ediliyor...
echo.

python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
    echo  [+] !PYVER! zaten yuklu.
    goto python_ok
)

echo  [-] Python bulunamadi. Kuruluyor...
echo.

winget --version >nul 2>&1
if %errorlevel% equ 0 (
    echo  [~] winget ile Python 3.11 kuruluyor...
    winget install -e --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts"
    python --version >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
        echo  [+] !PYVER! winget ile kuruldu!
        goto python_ok
    )
)

echo  [~] Python installer indiriliyor...
set PY_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
set PY_INST=%TEMP%\python_setup.exe
powershell -Command "Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_INST%' -UseBasicParsing"
if exist "%PY_INST%" (
    echo  [~] Python kuruluyor...
    "%PY_INST%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del "%PY_INST%" >nul 2>&1
    set "PATH=%PATH%;C:\Program Files\Python311;C:\Program Files\Python311\Scripts"
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts"
    python --version >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
        echo  [+] !PYVER! kuruldu!
        goto python_ok
    )
    echo.
    echo  [!] Python kuruldu ama PATH guncellenmedi.
    echo      Bu pencereyi KAPATIP YONETICI olarak TEKRAR calistir.
    pause
    exit /b 1
) else (
    echo  [-] Python indirilemedi. Manuel kur: https://www.python.org/downloads/
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

:python_ok
echo.

:: ─────────────────────────────────────────────
::  ADIM 2 — PIP + MODULLER
:: ─────────────────────────────────────────────
echo  [2/7] Python modulleri kuruluyor...
echo.

python -m pip install --upgrade pip --quiet
echo  [+] pip guncellendi.
echo.

set MOD_HATA=0

echo  [~] requests        - web istekleri / IP sorgu
python -m pip install requests --quiet
if %errorlevel% equ 0 (echo  [+] requests        OK) else (echo  [-] requests        HATA & set MOD_HATA=1)

echo  [~] stem             - Tor kontrolu
python -m pip install stem --quiet
if %errorlevel% equ 0 (echo  [+] stem             OK) else (echo  [-] stem             HATA & set MOD_HATA=1)

echo  [~] PySocks          - SOCKS5 proxy
python -m pip install PySocks --quiet
if %errorlevel% equ 0 (echo  [+] PySocks          OK) else (echo  [-] PySocks          HATA & set MOD_HATA=1)

echo  [~] cryptography     - AES sifreleme
python -m pip install cryptography --quiet
if %errorlevel% equ 0 (echo  [+] cryptography     OK) else (echo  [-] cryptography     HATA & set MOD_HATA=1)

echo  [~] qrcode           - QR kod uretici
python -m pip install qrcode --quiet
if %errorlevel% equ 0 (echo  [+] qrcode           OK) else (echo  [-] qrcode           HATA & set MOD_HATA=1)

echo  [~] pillow           - Ekran goruntüsü (PIL)
python -m pip install pillow --quiet
if %errorlevel% equ 0 (echo  [+] pillow           OK) else (echo  [-] pillow           HATA & set MOD_HATA=1)

echo  [~] colorama         - Renk destegi
python -m pip install colorama --quiet
if %errorlevel% equ 0 (echo  [+] colorama         OK) else (echo  [-] colorama         HATA)

if %MOD_HATA%==1 (
    echo.
    echo  [!] Bazi moduller yuklenemedi. Internet baglantini kontrol et.
    echo      setup.bat tekrar calistirarak yeniden deneyebilirsin.
) else (
    echo.
    echo  [+] Tum moduller basariyla kuruldu!
)
echo.

:: ─────────────────────────────────────────────
::  ADIM 3 — TOR BROWSER
:: ─────────────────────────────────────────────
echo  [3/7] Tor Browser kontrol ediliyor...
echo.

set TOR_YUKLU=0
if exist "%APPDATA%\Tor Browser\Browser\firefox.exe"              set TOR_YUKLU=1
if exist "%LOCALAPPDATA%\Tor Browser\Browser\firefox.exe"         set TOR_YUKLU=1
if exist "C:\Program Files\Tor Browser\Browser\firefox.exe"       set TOR_YUKLU=1
if exist "%USERPROFILE%\Desktop\Tor Browser\Browser\firefox.exe"  set TOR_YUKLU=1

for /d %%d in ("%USERPROFILE%\Desktop\*") do (
    if exist "%%d\Browser\firefox.exe" set TOR_YUKLU=1
)
for /d %%d in ("%USERPROFILE%\Downloads\*") do (
    if exist "%%d\Browser\firefox.exe" set TOR_YUKLU=1
)

if %TOR_YUKLU%==1 (
    echo  [+] Tor Browser zaten yuklu!
    set TOR_CEVAP=H
    goto tor_ok
)

echo  [!] Tor Browser bulunamadi.
echo.
set /p TOR_CEVAP=  [?] Tor Browser indirilsin mi? (E/H): 

if /i "!TOR_CEVAP!"=="E" (
    echo.
    echo  [~] Tor Browser indiriliyor ~100MB...
    set TOR_URL=https://www.torproject.org/dist/torbrowser/13.5.6/torbrowser-install-win64-13.5.6_ALL.exe
    set TOR_INST=%TEMP%\tor_setup.exe
    powershell -Command "Invoke-WebRequest -Uri '!TOR_URL!' -OutFile '!TOR_INST!' -UseBasicParsing"
    if exist "!TOR_INST!" (
        echo  [~] Tor Browser kuruluyor...
        "!TOR_INST!" /S
        del "!TOR_INST!" >nul 2>&1
        echo  [+] Tor Browser kuruldu!
    ) else (
        echo  [!] Otomatik indirme basarisiz.
        start https://www.torproject.org/download/
        echo  Kurduktan sonra Enter'a basin.
        pause >nul
    )
) else (
    echo  [!] Tor Browser atlandi.
)

:tor_ok
echo.

:: ─────────────────────────────────────────────
::  ADIM 4 — CLOUDFLARED
:: ─────────────────────────────────────────────
echo  [4/7] Cloudflared kontrol ediliyor...
echo.

set CF_DIR=%USERPROFILE%\.soldaten
set CF_EXE=%CF_DIR%\cloudflared.exe

if not exist "%CF_DIR%" mkdir "%CF_DIR%"

if exist "%CF_EXE%" (
    echo  [+] Cloudflared zaten yuklu!
    goto cf_ok
)

echo  [~] Cloudflared indiriliyor ~30MB...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile '%CF_EXE%' -UseBasicParsing"
if exist "%CF_EXE%" (
    echo  [+] Cloudflared indirildi! Hesap veya token gerekmez.
) else (
    echo  [!] Cloudflared indirilemedi. QR internet modu ilk kullanımda tekrar dener.
)

:cf_ok
echo.

:: ─────────────────────────────────────────────
::  ADIM 5 — DEFENDER GUNCELLEME
:: ─────────────────────────────────────────────
echo  [5/7] Windows Defender imzalari guncelleniyor...
echo.
powershell -Command "Update-MpSignature -ErrorAction SilentlyContinue" >nul 2>&1
if %errorlevel% equ 0 (
    echo  [+] Defender imzalari guncellendi!
) else (
    echo  [!] Defender guncellemesi basarisiz (yonetici yetkisi gerekebilir).
)
echo.

:: ─────────────────────────────────────────────
::  ADIM 6 — PORT VE PROCESS TEMIZLIGI
::  Soldaten'in kullandigi portlari tutan kalan
::  process'leri temizler (cloudflared + python)
:: ─────────────────────────────────────────────
echo  [6/7] Port ve process temizligi yapiliyor...
echo.

:: Kalan cloudflared process'lerini kapat
taskkill /F /IM cloudflared.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo  [+] Kalan cloudflared process temizlendi.
) else (
    echo  [i] Temizlenecek cloudflared yok.
)

:: Soldaten'in kullandigi portlari temizle
:: Port listesi: 5757, 5858, 5959, 6060, 6161, 6262, 7070, 7171, 7272, 7373, 7474
powershell -Command ^
  "$ports = @(5757,5858,5959,6060,6161,6262,7070,7171,7272,7373,7474,7575); ^
   $cleaned = 0; ^
   foreach ($port in $ports) { ^
     $r = netstat -ano 2>$null | Select-String \":$port\s\" | Select-String 'LISTENING'; ^
     foreach ($line in $r) { ^
       $pid = ($line -split '\s+')[-1]; ^
       if ($pid -match '^\d+$' -and $pid -ne '0') { ^
         try { Stop-Process -Id $pid -Force -ErrorAction Stop; $cleaned++ } catch {} ^
       } ^
     } ^
   }; ^
   Write-Host \"  [+] $cleaned port temizlendi.\""

echo.
echo  [+] Temizlik tamamlandi.
echo.

:: ─────────────────────────────────────────────
::  ADIM 7 — MASAUSTU KISAYOLU
:: ─────────────────────────────────────────────
echo  [7/7] Masaustu kisayolu olusturuluyor...
echo.

set "SOLD_DIR=%~dp0"
set "SOLD_PY=%~dp0soldaten.py"
set "SOLD_BAT=%~dp0calistir.bat"

:: calistir.bat olustur
python -c "
import os
bat = r'%SOLD_BAT%'
py  = r'%SOLD_PY%'
content = (
    '@echo off\n'
    'title SOLDATEN\n'
    'color 0A\n'
    'chcp 65001 >nul 2>&1\n'
    'cd /d \"%~dp0\"\n'
    ':: Her baslarken kalan portlari ve cloudflared temizle\n'
    'taskkill /F /IM cloudflared.exe >nul 2>&1\n'
    'python \"' + py + '\"\n'
    'if %errorlevel% neq 0 (\n'
    '    echo.\n'
    '    echo  [!] Hata olustu. setup.bat calistirin.\n'
    '    pause\n'
    ')\n'
)
open(bat, 'w', encoding='utf-8').write(content)
print('OK')
"

:: Masaustu kisayolu
python -c "
import os, subprocess
try:
    import win32com.client as wc
    s  = wc.Dispatch('WScript.Shell')
    sc = s.CreateShortcut(os.path.join(os.path.expanduser('~'),'Desktop','SOLDATEN.lnk'))
    sc.TargetPath       = r'%SOLD_BAT%'
    sc.WorkingDirectory = r'%SOLD_DIR%'
    sc.Description      = 'Soldaten Gizlilik Araci'
    sc.Save()
    print('[+] Kisayol olusturuldu (win32com)')
except ImportError:
    ps = (
        r'\$s=New-Object -COM WScript.Shell; '
        r'\$sc=\$s.CreateShortcut([Environment]::GetFolderPath(''Desktop'')+''\SOLDATEN.lnk''); '
        r'\$sc.TargetPath=''%SOLD_BAT%''; '
        r'\$sc.WorkingDirectory=''%SOLD_DIR%''; '
        r'\$sc.Description=''Soldaten Gizlilik Araci''; '
        r'\$sc.Save()'
    )
    subprocess.run(['powershell','-Command',ps], capture_output=True)
    print('[+] Kisayol olusturuldu (powershell)')
"

if exist "%USERPROFILE%\Desktop\SOLDATEN.lnk" (
    echo  [+] Masaustu kisayolu hazir!
) else (
    echo  [!] Kisayol olusturulamadi - calistir.bat dosyasini elle calistir.
)
echo.

:: ─────────────────────────────────────────────
::  OZET
:: ─────────────────────────────────────────────
cls
echo.
echo  ============================================================
echo    SOLDATEN - Kurulum Tamamlandi
echo  ============================================================
echo.
echo  Durum kontrol ediliyor...
echo.

python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo    [+] Python           %%i
) else (
    echo    [-] Python           YUKLU DEGIL
)

python -c "import requests"     >nul 2>&1 && echo    [+] requests         OK || echo    [-] requests         EKSIK
python -c "import cryptography" >nul 2>&1 && echo    [+] cryptography     OK || echo    [-] cryptography     EKSIK
python -c "import qrcode"       >nul 2>&1 && echo    [+] qrcode           OK || echo    [-] qrcode           EKSIK
python -c "import stem"         >nul 2>&1 && echo    [+] stem             OK || echo    [-] stem             EKSIK
python -c "import PIL"          >nul 2>&1 && echo    [+] pillow           OK || echo    [-] pillow           EKSIK
python -c "import socks"        >nul 2>&1 && echo    [+] PySocks          OK || echo    [-] PySocks          EKSIK

if %TOR_YUKLU%==1 (
    echo    [+] Tor Browser      Zaten Yukluydu
) else if /i "!TOR_CEVAP!"=="E" (
    echo    [+] Tor Browser      Kuruldu
) else (
    echo    [-] Tor Browser      Atlandi
)

if exist "%CF_EXE%" (
    echo    [+] Cloudflared      Hazir
) else (
    echo    [-] Cloudflared      Indirilemedi
)

if exist "%SOLD_BAT%" (
    echo    [+] calistir.bat     Hazir
) else (
    echo    [-] calistir.bat     Olusturulamadi
)

echo.
echo  ============================================================
echo.
echo  NOT: Soldaten her baslarken kalan portlari otomatik temizler.
echo  Sorun yasarsan setup.bat tekrar calistir.
echo.
echo  Baslatmak icin masaustundeki SOLDATEN kisayoluna cift tikla.
echo.
echo  ============================================================
echo.

set /p BASLAT=  [?] Soldaten simdi baslatilsin mi? (E/H): 
if /i "!BASLAT!"=="E" (
    python "%SOLD_PY%"
)

endlocal
