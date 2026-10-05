param(
    [switch]$Remove
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$taskName = "AlphaEdge Daily Update"
$desktop = [Environment]::GetFolderPath("Desktop")
$startBat = Join-Path $root "Start AlphaEdge.bat"
$updateBat = Join-Path $root "Update AlphaEdge.bat"

if ($Remove) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $desktop "AlphaEdge AI.lnk") -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $desktop "Update AlphaEdge.lnk") -Force -ErrorAction SilentlyContinue
    Write-Output "AlphaEdge automation removed."
    exit 0
}

foreach ($path in @($startBat, $updateBat)) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Required launcher missing: $path" }
}

# 4:15 PM Mon-Fri, retry after a missed start, and never create a duplicate
# concurrent updater.  The updater itself also holds a durable SQLite lock.
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 4:15PM
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 12) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 15) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -WakeToRun
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument ('/c ""{0}" /scheduled"' -f $updateBat)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null

$iconDirectory = Join-Path $root "assets\icons"
$iconPath = Join-Path $iconDirectory "alphaedge-ai.ico"
if (-not (Test-Path -LiteralPath $iconPath)) {
    throw "AlphaEdge desktop icon is missing: $iconPath"
}

$shell = New-Object -ComObject WScript.Shell
foreach ($definition in @(
    @{ Name = "AlphaEdge AI"; Target = $startBat; Description = "Start AlphaEdge AI Dashboard" },
    @{ Name = "Update AlphaEdge"; Target = $updateBat; Description = "Safely update AlphaEdge Dhan EOD data" }
)) {
    $shortcut = $shell.CreateShortcut((Join-Path $desktop ("{0}.lnk" -f $definition.Name)))
    $shortcut.TargetPath = $definition.Target
    $shortcut.WorkingDirectory = $root
    $shortcut.Description = $definition.Description
    if (Test-Path -LiteralPath $iconPath) { $shortcut.IconLocation = "$iconPath,0" }
    $shortcut.WindowStyle = 7
    $shortcut.Save()
}

$task = Get-ScheduledTask -TaskName $taskName
Write-Output ("Task={0}; State={1}; Desktop={2}" -f $task.TaskName, $task.State, $desktop)
