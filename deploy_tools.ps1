$ErrorActionPreference = 'Continue'
$src = "$PSScriptRoot\launcher"
$envf = "$PSScriptRoot\kiosk-env"
$ssh = @('-o','StrictHostKeyChecking=no','-o','UserKnownHostsFile=NUL','-o','ConnectTimeout=8')
$ip = if ($env:CARTHING_IP) { $env:CARTHING_IP } else { '10.42.1.242' }

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

& ssh @ssh "root@$ip" 'mkdir -p /opt/nocturne/webapps/player/tools && mkdir -p /var/nocturne-data/kws && ln -sfn /var/nocturne-data/kws /opt/nocturne/webapps/player/tools/kws'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }


& scp @ssh "$src\index.html" "root@${ip}:/opt/nocturne/webapps/player/index.html"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Copying tools recursively..."
& scp @ssh -r "$src\tools\*" "root@${ip}:/opt/nocturne/webapps/player/tools/"
if ($LASTEXITCODE -ne 0) { throw "scp failed copying tools" }

& scp @ssh $envf "root@${ip}:/opt/nocturne/kiosk-env"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& ssh @ssh "root@$ip" @'
set -e
ls -la /opt/nocturne/webapps/player/tools
cat /opt/nocturne/kiosk-env
systemctl restart chromium-kiosk
sleep 4
systemctl is-active chromium-kiosk
journalctl -u chromium-kiosk -n 8 --no-pager
echo DEPLOY_OK
'@
exit $LASTEXITCODE
