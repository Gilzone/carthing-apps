$ErrorActionPreference = 'Continue'
$py = 'C:\Users\Gilzh\AppData\Local\Programs\Python\Python312\python.exe'
$dllDir = 'C:\Users\Gilzh\AppData\Roaming\Python\Python312\site-packages\libusb\_platform\windows\x86_64'
$env:PATH = $dllDir + ';' + 'C:\Users\Gilzh\carthing-handshake\usb_driver\amd64;' + $env:PATH
Set-Location 'C:\Users\Gilzh\carthing-handshake\superbird-tool'
$log = 'C:\Users\Gilzh\carthing-handshake\retry-handshake.log'

function Log($msg) {
    $line = '{0} {1}' -f (Get-Date -Format 'HH:mm:ss'), $msg
    Add-Content -Path $log -Value $line
    Write-Host $line
}

Log 'watching for Car Thing 1b8e:c003 ...'
$deadline = (Get-Date).AddMinutes(5)
$attempted = $false

while ((Get-Date) -lt $deadline) {
    $out = & $py .\superbird_tool.py --find_device 2>&1 | Out-String
    if ($out -match 'USB Burn Mode') {
        Log 'HANDSHAKE_OK already in USB Burn Mode'
        Write-Host 'DONE'
        exit 0
    }
    if ($out -match 'USB Mode') {
        Log 'device in USB Mode; running --burn_mode'
        $burn = & $py .\superbird_tool.py --burn_mode 2>&1 | Out-String
        Add-Content -Path $log -Value $burn
        Write-Host $burn
        Start-Sleep -Seconds 8
        $out2 = & $py .\superbird_tool.py --find_device 2>&1 | Out-String
        Log $out2.Trim()
        if ($out2 -match 'USB Burn Mode') {
            Log 'HANDSHAKE_OK entered USB Burn Mode'
            Write-Host 'DONE'
            exit 0
        }
        $attempted = $true
        Log 'burn_mode did not stick; will retry if device returns'
    } else {
        Log 'not present yet'
    }
    Start-Sleep -Seconds 3
}

Log 'TIMEOUT device did not stay in burn mode'
Write-Host 'FAILED'
exit 1
