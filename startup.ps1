param(
    [switch]$Install,
    [switch]$Remove
)

$startup = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startup 'My Ganesha.lnk'

if ($Remove) {
    if (Test-Path $shortcutPath) { Remove-Item $shortcutPath }
    exit 0
}

if ($Install) {
    $appDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $pythonw = Join-Path $appDir '.venv\Scripts\pythonw.exe'
    $app = Join-Path $appDir 'app.py'
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $pythonw
    $shortcut.Arguments = '"' + $app + '"'
    $shortcut.WorkingDirectory = $appDir
    $shortcut.Description = 'My Ganesha desktop companion'
    $shortcut.Save()
}
