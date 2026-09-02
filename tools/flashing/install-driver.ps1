$ErrorActionPreference = 'Continue'
$dir = 'C:\Users\Gilzh\carthing-handshake'
$ct = Join-Path $dir 'CTDrvInst.exe'
$dest = Join-Path $dir 'usb_driver'
$log = Join-Path $dir 'install-driver.log'
$exitFile = Join-Path $dir 'install-driver.exit'

function Log($msg) {
    $line = '{0} {1}' -f (Get-Date -Format o), $msg
    Add-Content -Path $log -Value $line
    Write-Host $line
}

Set-Content -Path $log -Value ('start ' + (Get-Date -Format o))
$wid = [Security.Principal.WindowsIdentity]::GetCurrent()
$prin = New-Object Security.Principal.WindowsPrincipal($wid)
Log ('user=' + $wid.Name)
Log ('admin=' + $prin.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))

$argList = @(
    '-v', '0x1B8E',
    '-p', '0xC003',
    '-n', 'WorldCup Device',
    '-t', '0',
    '-d', $dest,
    '-l', '0',
    '-o', '120000'
)
Log ('running ' + $ct + ' ' + ($argList -join ' '))

$p = Start-Process -FilePath $ct -ArgumentList $argList -Wait -PassThru -NoNewWindow
$code = $p.ExitCode
Log ('CTDrvInst exit=' + $code)
Set-Content -Path $exitFile -Value ([string]$code)

Get-PnpDevice | Where-Object { $_.InstanceId -like '*VID_1B8E*' -or $_.FriendlyName -match 'WorldCup|GX-CHIP' } |
    ForEach-Object { Log ('device status=' + $_.Status + ' name=' + $_.FriendlyName + ' problem=' + $_.ProblemDescription) }

exit $code
