param(
  [string]$Repo = "https://github.com/obnoxiousmods/obbyconfigs.git",
  [string]$Ref = "main",
  [string]$Workdir = "",
  [string]$WslDistro = "",
  [switch]$InstallFonts,
  [switch]$PrintScheme
)

$ErrorActionPreference = "Stop"

$Scheme = @'
{
  "background": "#1A1B26",
  "black": "#15161E",
  "blue": "#7AA2F7",
  "brightBlack": "#414868",
  "brightBlue": "#7AA2F7",
  "brightCyan": "#7DCFFF",
  "brightGreen": "#9ECE6A",
  "brightPurple": "#BB9AF7",
  "brightRed": "#F7768E",
  "brightWhite": "#C0CAF5",
  "brightYellow": "#E0AF68",
  "cursorColor": "#C0CAF5",
  "cyan": "#7DCFFF",
  "foreground": "#C0CAF5",
  "green": "#9ECE6A",
  "name": "Tokyo Night",
  "purple": "#BB9AF7",
  "red": "#F7768E",
  "selectionBackground": "#33467C",
  "white": "#A9B1D6",
  "yellow": "#E0AF68"
}
'@

function Need($Command) {
  return [bool](Get-Command $Command -ErrorAction SilentlyContinue)
}

function Install-MesloFonts {
  $fontDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
  New-Item -ItemType Directory -Force -Path $fontDir | Out-Null

  $base = "https://github.com/romkatv/powerlevel10k-media/raw/master"
  $fonts = @(
    "MesloLGS%20NF%20Regular.ttf",
    "MesloLGS%20NF%20Bold.ttf",
    "MesloLGS%20NF%20Italic.ttf",
    "MesloLGS%20NF%20Bold%20Italic.ttf"
  )

  foreach ($font in $fonts) {
    $fileName = [uri]::UnescapeDataString($font)
    $target = Join-Path $fontDir $fileName
    if (-not (Test-Path $target)) {
      Invoke-WebRequest -Uri "$base/$font" -OutFile $target
    }
    New-ItemProperty -Path "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts" -Name "$fileName (TrueType)" -Value $target -PropertyType String -Force | Out-Null
  }
}

function Quote-BashArg([string]$Value) {
  return "'" + $Value.Replace("'", "'\''") + "'"
}

if ($PrintScheme) {
  Write-Output $Scheme
}

if ($InstallFonts) {
  Install-MesloFonts
  Write-Output "Installed MesloLGS NF fonts for the current Windows user."
}

if ($WslDistro -ne "") {
  if (-not (Need "wsl.exe")) {
    throw "wsl.exe was not found. Install WSL first, then rerun this script."
  }
  $joinedArgs = ($args | ForEach-Object { Quote-BashArg $_ }) -join " "
  $linuxCommand = "curl -fsSL https://raw.githubusercontent.com/obnoxiousmods/obbyconfigs/$Ref/install.sh | bash -s -- $joinedArgs"
  wsl.exe -d $WslDistro -- bash -lc $linuxCommand
  exit $LASTEXITCODE
}

if (-not (Need "git")) {
  throw "git was not found. Install Git for Windows or run this script with -WslDistro."
}

$python = $null
if (Need "py") {
  $python = "py"
} elseif (Need "python") {
  $python = "python"
} elseif (Need "python3") {
  $python = "python3"
} else {
  throw "Python 3 was not found. Install Python or run this script with -WslDistro."
}

if ($Workdir -eq "") {
  $Workdir = Join-Path ([System.IO.Path]::GetTempPath()) ("obbyconfigs-" + [System.Guid]::NewGuid().ToString("N"))
}

if (Test-Path (Join-Path $Workdir ".git")) {
  git -C $Workdir fetch --depth=1 origin $Ref
  git -C $Workdir checkout FETCH_HEAD
} else {
  git clone --depth=1 --branch $Ref $Repo $Workdir
}

Push-Location $Workdir
try {
  & $python obbyinstaller.py @args
  exit $LASTEXITCODE
} finally {
  Pop-Location
}
