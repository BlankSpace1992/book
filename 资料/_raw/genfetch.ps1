$ProgressPreference = 'SilentlyContinue'
$OutDir = "D:\Book\资料\_raw"
foreach ($it in $Targets) {
  $k = $it[0]; $u = $it[1]
  $hp = Join-Path $OutDir "$k.html"; $tp = Join-Path $OutDir "$k.txt"
  if ((Test-Path $tp) -and ((Get-Item $tp).Length -gt 2000)) { Write-Output "SKIP $k"; continue }
  $code = curl.exe -s -L -m 60 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36" -o $hp -w "%{http_code}" $u 2>$null
  if (-not (Test-Path $hp)) { Write-Output "FAIL $k http=$code"; continue }
  $raw = Get-Content -Path $hp -Raw -Encoding UTF8
  if (-not $raw) { Write-Output "EMPTY $k http=$code"; continue }
  $raw = [regex]::Replace($raw, '(?is)<(script|style|noscript|svg|head|nav|footer)[^>]*>.*?</\1>', ' ')
  $raw = [regex]::Replace($raw, '(?i)</?(p|div|br|li|tr|h[1-6]|table|ul|ol|section|article|td|th|dt|dd|blockquote)[^>]*>', "`n")
  $raw = [regex]::Replace($raw, '(?s)<[^>]+>', ' ')
  $raw = $raw -replace '&nbsp;', ' ' -replace '&amp;', '&' -replace '&lt;', '<' -replace '&gt;', '>' -replace '&quot;', '"' -replace '&#39;', "'"
  $raw = [regex]::Replace($raw, '&#x?[0-9A-Fa-f]+;', ' ')
  $raw = [regex]::Replace($raw, '[ \t\u00a0]+', ' ')
  $raw = [regex]::Replace($raw, '(\r?\n\s*){2,}', "`n")
  Set-Content -Path $tp -Value $raw.Trim() -Encoding UTF8
  Write-Output ("OK $k http=$code txtlen=" + (Get-Item $tp).Length)
}
