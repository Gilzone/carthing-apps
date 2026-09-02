$ErrorActionPreference = 'Continue'
$py = 'C:\Users\Gilzh\AppData\Local\Programs\Python\Python312\python.exe'
if (-not (Test-Path $py)) { $py = 'python' }
& $py 'C:\Users\Gilzh\carthing-handshake\nocturne\make_launcher.py'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$src = 'C:\Users\Gilzh\carthing-handshake\nocturne\launcher'
$envf = 'C:\Users\Gilzh\carthing-handshake\nocturne\kiosk-env'
$ssh = @('-o','StrictHostKeyChecking=no','-o','UserKnownHostsFile=NUL','-o','ConnectTimeout=8')
$ip = '10.42.1.242'

Write-Host "Waiting for Car Thing at $ip ..."
$deadline = (Get-Date).AddMinutes(8)
$ok = $false
while ((Get-Date) -lt $deadline) {
    $r = & ssh @ssh "root@$ip" 'echo SSH_OK' 2>$null
    if ($r -match 'SSH_OK') { $ok = $true; break }
    Start-Sleep -Seconds 2
}
if (-not $ok) { Write-Host 'TIMEOUT no SSH'; exit 1 }
Write-Host 'SSH_OK'

& ssh @ssh "root@$ip" 'mkdir -p /opt/nocturne/webapps/player/games'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& scp @ssh "$src\index.html" "root@${ip}:/opt/nocturne/webapps/player/index.html"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Get-ChildItem "$src\games" -File | ForEach-Object {
    Write-Host ("copy " + $_.Name)
    & scp @ssh $_.FullName ("root@${ip}:/opt/nocturne/webapps/player/games/" + $_.Name)
    if ($LASTEXITCODE -ne 0) { throw ("scp failed " + $_.Name) }
}

& scp @ssh $envf "root@${ip}:/opt/nocturne/kiosk-env"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& ssh @ssh "root@$ip" @'
set -e
ls -la /opt/nocturne/webapps/player /opt/nocturne/webapps/player/games
wc -c /opt/nocturne/webapps/player/index.html /opt/nocturne/webapps/player/games/*
grep -c HOME /opt/nocturne/webapps/player/games/2048.html
systemctl restart chromium-kiosk
sleep 4
systemctl is-active chromium-kiosk
journalctl -u chromium-kiosk -n 12 --no-pager
echo DEPLOY_OK
'@
exit $LASTEXITCODE
