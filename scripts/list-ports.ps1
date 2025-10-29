param([int[]]$Ports, [int]$StartPort, [int]$EndPort)
if (-not $Ports -and $StartPort -and $EndPort) { $Ports = $StartPort..$EndPort }
if (-not $Ports) { $Ports = @(3000..3010); $Ports += 5173; $Ports += 8080 }
$Ports = $Ports | Sort-Object -Unique
foreach($p in $Ports){
  try { $c = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction Stop } catch { $c=@() }
  if($c){
    $pids = $c | Select-Object -ExpandProperty OwningProcess -Unique
    $names = @(); foreach($pid in $pids){ $names += (Get-Process -Id $pid -ErrorAction SilentlyContinue).ProcessName }
    Write-Host ("LISTEN {0} PIDs: {1} Names: {2}" -f $p, ($pids -join ','), ($names -join ','))
  } else {
    Write-Host ("FREE   {0}" -f $p)
  }
}
