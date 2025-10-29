$c = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
if($c){
  $pids = $c | Select-Object -ExpandProperty OwningProcess -Unique
  foreach($pid in $pids){
    $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
    Write-Host "Port 3000: PID $pid - $($proc.ProcessName) - $($proc.Path)"
    Stop-Process -Id $pid -Force
    Write-Host "Killed PID $pid"
  }
} else {
  Write-Host 'Port 3000 is free'
}
