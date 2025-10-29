param(
  [int[]]$Ports,
  [int]$StartPort,
  [int]$EndPort
)

# Build target port list
if (-not $Ports -and $StartPort -and $EndPort) {
  $Ports = $StartPort..$EndPort
}
if (-not $Ports) {
  # Default: common FE/BE dev ports
  $Ports = @(3000..3010)
  $Ports += 5173
  $Ports += 8080
  $Ports += 8000
  $Ports += 8001
}

$Ports = $Ports | Sort-Object -Unique

foreach($p in $Ports){
  try{
    $conns = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction Stop
  } catch {
    $conns = @()
  }
  if($conns.Count -gt 0){
    $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
    foreach($pid in $pids){
      try{
        $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
        Write-Host "Killing PID $pid ($($proc.ProcessName)) on port $p"
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
      } catch {
        Write-Host "Failed to kill PID $pid on port $p"
      }
    }
  } else {
    Write-Host "No listener on port $p"
  }
}

# Summary of remaining listeners
Write-Host "--- Post-kill check ---"
foreach($p in $Ports){
  $left = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
  if($left){ Write-Host "Still listening on port $p" } else { Write-Host "Port $p is free" }
}
