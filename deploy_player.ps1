$ErrorActionPreference = 'Continue'
$py = 'C:\Users\Gilzh\AppData\Local\Programs\Python\Python312\python.exe'
& $py 'C:\Users\Gilzh\carthing-handshake\nocturne\make_carthing_html.py' | Out-Host
$html = 'C:\Users\Gilzh\carthing-handshake\nocturne\mp3_player_carthing.html'
$svc = 'C:\Users\Gilzh\carthing-handshake\nocturne\player-httpd.service'
$envf = 'C:\Users\Gilzh\carthing-handshake\nocturne\kiosk-env'
$ssh = @('-o','StrictHostKeyChecking=no','-o','UserKnownHostsFile=NUL','-o','ConnectTimeout=8')

function Host-Up {
    if (Test-Connection -ComputerName 10.42.1.242 -Count 1 -Quiet -ErrorAction SilentlyContinue) { return '10.42.1.242' }
    try {
        $r = Resolve-DnsName nocturne.local -ErrorAction Stop | Select-Object -First 1
        if ($r.IPAddress) { return $r.IPAddress }
    } catch {}
    return $null
}

Write-Host 'Waiting for Car Thing USB gadget (plug in WITHOUT 1+4)...'
$deadline = (Get-Date).AddMinutes(10)
$ip = $null
while ((Get-Date) -lt $deadline) {
    $ip = Host-Up
    if ($ip) { break }
    Start-Sleep -Seconds 2
}
if (-not $ip) { Write-Host 'TIMEOUT no device'; exit 1 }
Write-Host "found $ip"
Start-Sleep -Seconds 2
ssh @ssh "root@$ip" 'mkdir -p /opt/nocturne/webapps/player'
scp @ssh $html "root@${ip}:/opt/nocturne/webapps/player/index.html"
scp @ssh $svc "root@${ip}:/opt/nocturne/player-httpd.service"
scp @ssh $envf "root@${ip}:/opt/nocturne/kiosk-env"
ssh @ssh "root@$ip" @'
set -e
mount -o remount,rw /
cp /opt/nocturne/player-httpd.service /etc/systemd/system/player-httpd.service
systemctl daemon-reload
systemctl enable --now player-httpd.service
mount -o remount,ro / || true
systemctl restart chromium-kiosk
sleep 3
systemctl is-active player-httpd chromium-kiosk
wget -q -O- http://127.0.0.1:8090/ | head -c 80
echo
echo DEPLOY_OK
'@
exit $LASTEXITCODE
