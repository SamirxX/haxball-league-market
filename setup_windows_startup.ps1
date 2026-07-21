$WshShell = New-Object -comObject WScript.Shell
$StartupFolder = [System.Environment]::GetFolderPath('Startup')
$ShortcutPath = [System.IO.Path]::Combine($StartupFolder, "HaxballLeagueBot.lnk")

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = '-WindowStyle Hidden -Command "python ''C:\Users\Lenovo LoQ\.gemini\antigravity\scratch\haxball_discord_league\bot_adaptive.py''"'
$Shortcut.WorkingDirectory = "C:\Users\Lenovo LoQ\.gemini\antigravity\scratch\haxball_discord_league"
$Shortcut.WindowStyle = 7
$Shortcut.Save()

Write-Host "✅ Added Haxball League Bot to Windows Startup Folder successfully!"
