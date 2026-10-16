$ProgressPreference = 'SilentlyContinue'
$OutDir = "D:\Book\资料\_raw"
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }
foreach ($n in $Names) {
  $enc = [uri]::EscapeDataString($n)
  $url = "https://wapbaike.baidu.com/item/$enc"
  $htmlPath = Join-Path $OutDir "bk_$n.html"
  $txtPath  = Join-Path $OutDir "bk_$n.txt"
  if ((Test-Path $txtPath) -and ((Get-Item $txtPath).Length -gt 3000)) { Write-Output "SKIP $n"; continue }
  $code = curl.exe -s -L -m 45 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36" -o $htmlPath -w "%{http_code}" $url 2>$null
  if (-not (Test-Path $htmlPath)) { Write-Output "FAIL $n http=$code"; continue }
  $raw = Get-Content -Path $htmlPath -Raw -Encoding UTF8
  if (-not $raw) { Write-Output "EMPTY $n http=$code"; continue }
  $raw = [regex]::Replace($raw, '(?is)<(script|style|noscript|svg|head)[^>]*>.*?</\1>', ' ')
  $raw = [regex]::Replace($raw, '(?i)</?(p|div|br|li|tr|h[1-6]|table|ul|ol|section|article|td|th|dt|dd|blockquote|span)[^>]*>', "`n")
  $raw = [regex]::Replace($raw, '(?s)<[^>]+>', ' ')
  $raw = $raw -replace '&nbsp;', ' ' -replace '&amp;', '&' -replace '&lt;', '<' -replace '&gt;', '>' -replace '&quot;', '"' -replace '&#39;', "'"
  $raw = [regex]::Replace($raw, '&#x?[0-9A-Fa-f]+;', ' ')
  $raw = [regex]::Replace($raw, '[ \t\u00a0]+', ' ')
  $raw = [regex]::Replace($raw, '(\r?\n\s*){2,}', "`n")
  Set-Content -Path $txtPath -Value $raw.Trim() -Encoding UTF8
  Write-Output ("OK $n http=$code txtlen=" + (Get-Item $txtPath).Length)
}
