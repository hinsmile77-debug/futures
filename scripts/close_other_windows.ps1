# close_other_windows.ps1
# 미륵이 런처 실행 전 다른 창들을 최소화하여 Cybos GUI 자동화 간섭 방지
# 사용법: powershell -File close_other_windows.ps1 -KeepTitle "제목"
param(
    [string]$KeepTitle = ""
)

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WinAPI {
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);
    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
}
"@

$SW_MINIMIZE = 6
$protected = @("Mireuk", "CREON", "Cybos", "CpStart", "CMD", "PowerShell", "cmd.exe")
if ($KeepTitle) { $protected += $KeepTitle }

$minimized = 0
[WinAPI]::EnumWindows({
    param($hwnd, $lParam)
    if (-not [WinAPI]::IsWindowVisible($hwnd)) { return $true }
    $sb = New-Object System.Text.StringBuilder 256
    [void][WinAPI]::GetWindowText($hwnd, $sb, 256)
    $title = $sb.ToString()
    if (-not $title) { return $true }
    foreach ($p in $protected) {
        if ($title -match [regex]::Escape($p)) { return $true }
    }
    [void][WinAPI]::ShowWindow($hwnd, $SW_MINIMIZE)
    $script:minimized++
    return $true
}, [IntPtr]::Zero) | Out-Null

Write-Host "[INFO] $minimized 개 창 최소화 완료."
