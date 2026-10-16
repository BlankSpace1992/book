param(
  [string]$Name,
  [string]$Url,
  [string]$OutDir = "D:\Book\资料\_raw"
)
$ProgressPreference = 'SilentlyContinue'
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }
$htmlPath = Join-Path $OutDir "$Name.html"
$txtPath  = Join-Path $OutDir "$Name.txt"
$code = curl.exe -s -L -m 45 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36" -o $htmlPath -w "%{http_code}" $Url 2>$null
if (-not (Test-Path $htmlPath)) { Write-Output "$Name  FAIL http=$code"; exit }
$raw = Get-Content -Path $htmlPath -Raw -Encoding UTF8
if (-not $raw) { Write-Output "$Name  FAIL empty http=$code"; exit }
# strip script/style/noscript blocks
$raw = [regex]::Replace($raw, '(?is)<(script|style|noscript|svg|head)[^>]*>.*?</\1>', ' ')
# block-level tags -> newline
$raw = [regex]::Replace($raw, '(?i)</?(p|div|br|li|tr|h[1-6]|table|ul|ol|section|article|td|th|dt|dd|blockquote)[^>]*>', "`n")
# remove all remaining tags
$raw = [regex]::Replace($raw, '(?s)<[^>]+>', ' ')
# html entities
$raw = $raw -replace '&nbsp;', ' ' -replace '&amp;', '&' -replace '&lt;', '<' -replace '&gt;', '>' -replace '&quot;', '"' -replace '&#39;', "'" -replace '&ldquo;', '“' -replace '&rdquo;', '”' -replace '&mdash;', '—' -replace '&hellip;', '…'
$raw = [regex]::Replace($raw, '&#x?[0-9A-Fa-f]+;', ' ')
$raw = [regex]::Replace($raw, '[ \t\u00a0]+', ' ')
$raw = [regex]::Replace($raw, '(\r?\n\s*){2,}', "`n")
Set-Content -Path $txtPath -Value $raw.Trim() -Encoding UTF8
Write-Output ("$Name  http=$code  htmllen=" + (Get-Item $htmlPath).Length + "  txtlen=" + (Get-Item $txtPath).Length)
