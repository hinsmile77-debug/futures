<#
    ComTaskRunLevel.ps1  (MW0601 705cha, 2026-10-22)
    KEEP THIS FILE PURE ASCII (PowerShell 5.1 reads BOM-less files as ANSI).

    Single source for "which RunLevel must a scheduled task that calls Cybos/CREON COM use".
    Dot-source it:   . (Join-Path $PSScriptRoot 'lib\ComTaskRunLevel.ps1')

    The rule is: the task must run at the SAME integrity level as the API session (CpStart /
    DibServer). If it differs, COM does not attach to the logged-in DibServer - it spawns a
    fresh, logged-out one, IsConnect=0, every request fails, and the task still "ran".

    Why not just "BROKER=creon -> Highest" (option_flow_backfill_task.ps1 until 705cha)
      BROKER is a proxy. What actually decides the session's integrity level is:
        (1) UAC (EnableLUA). With UAC OFF there is no split token: Limited and Highest both get
            the full admin token, so the level can never differ. MW0601 runs with EnableLUA=0
            (measured 2026-10-22): its Limited COM tasks connect (connect=1) and its Highest
            EodSessionCleanup connects too (was_connected=1).
        (2) With UAC ON: how the session was launched. LAUNCH_API.bat / start_mireuk.bat
            self-elevate for BROKER=creon; for cybos the session follows the RunLevel of the
            'Cybos Plus' launch task (switch_broker.ps1 sets it to Highest, MW0601 had it
            Limited until 2026-10-13).
      2026-09-21..10-02 MW0601 (UAC on, Cybos Limited) registered the backfill as Highest
      and failed 8 trading days in a row. The BROKER rule fixed that PC at that time, but it
      is wrong for a creon PC with UAC off (no difference) and for a cybos PC whose launch
      task is Highest (Limited would fail).

    Resolution order
      1. UAC off                    -> the level step 3 would give (Limited == Highest today, so pick
                                       the one that stays right if UAC is re-enabled)
      2. CpStart.exe running        -> its measured elevation
      3. machine.cfg BROKER=creon   -> Highest   (the launchers self-elevate)
         BROKER=cybos               -> RunLevel of the 'Cybos Plus' task (missing -> Limited)
      4. none of the above          -> RunLevel = $null  (caller must refuse; do not guess)
#>

function Get-UacEnabled {
    # $true / $false, or $null when unreadable (unmeasured != false)
    try {
        $v = (Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' `
                               -Name EnableLUA -ErrorAction Stop).EnableLUA
        return ([int]$v -ne 0)
    } catch { return $null }
}

function Get-MachineBroker([string]$Root) {
    $cfg = Join-Path $Root 'machine.cfg'
    if (-not (Test-Path -LiteralPath $cfg)) { return '' }
    $b = ''
    foreach ($ln in (Get-Content -LiteralPath $cfg -Encoding UTF8)) {
        if ($ln -match '^\s*BROKER\s*=\s*([A-Za-z]+)\s*$') { $b = $Matches[1].ToLower() }
    }
    return $b
}

function Test-CurrentElevated {
    $me = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $me.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-ProcessElevation([int]$ProcessId) {
    # $true / $false, or $null when it cannot be measured
    if (-not ('MireukTokenProbe' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class MireukTokenProbe {
    [DllImport("kernel32.dll", SetLastError=true)] static extern IntPtr OpenProcess(uint a, bool i, int pid);
    [DllImport("kernel32.dll", SetLastError=true)] static extern bool CloseHandle(IntPtr h);
    [DllImport("advapi32.dll", SetLastError=true)] static extern bool OpenProcessToken(IntPtr p, uint a, out IntPtr t);
    [DllImport("advapi32.dll", SetLastError=true)] static extern bool GetTokenInformation(IntPtr t, int c, out int v, int l, out int r);
    // 1 elevated, 0 not elevated, -1 process not openable, -2 token access denied, -3 query failed
    public static int Probe(int pid) {
        IntPtr p = OpenProcess(0x1000, false, pid);
        if (p == IntPtr.Zero) return -1;
        try {
            IntPtr t;
            if (!OpenProcessToken(p, 0x0008, out t)) return Marshal.GetLastWin32Error() == 5 ? -2 : -3;
            try { int v, r; return GetTokenInformation(t, 20, out v, 4, out r) ? (v != 0 ? 1 : 0) : -3; }
            finally { CloseHandle(t); }
        } finally { CloseHandle(p); }
    }
}
'@
    }
    $r = [MireukTokenProbe]::Probe($ProcessId)
    if ($r -eq 1) { return $true }
    if ($r -eq 0) { return $false }
    # A non-elevated caller is denied the token of an elevated process -> that denial is the answer.
    if ($r -eq -2 -and -not (Test-CurrentElevated)) { return $true }
    return $null
}

function Resolve-ComTaskRunLevel([string]$Root, [switch]$AssumeUacOn) {
    # -AssumeUacOn: "what would be needed if UAC were turned back on" (audit's latent check).
    # It skips the UAC and live-CpStart branches - with UAC off every process reads as elevated.
    $uac    = Get-UacEnabled
    $broker = Get-MachineBroker $Root
    $o = [ordered]@{ RunLevel = $null; Basis = ''; Reason = ''; Uac = $uac; Broker = $broker }

    if ($AssumeUacOn) { $uac = $true }
    if ($uac -eq $false) {
        # Both levels get the same token today, so pick the one that stays right if UAC is
        # re-enabled (a reboot away). Registering Highest needs no prompt: with UAC off the
        # installer already holds the full admin token.
        $f = Resolve-ComTaskRunLevel $Root -AssumeUacOn
        $o.RunLevel = $(if ($f.RunLevel) { $f.RunLevel } else { 'Limited' }); $o.Basis = 'uac_off'
        $o.Reason = ('UAC off (EnableLUA=0): Limited and Highest get the same full token today; ' +
                     'choosing {0}, the level needed if UAC is re-enabled ({1}).' -f $o.RunLevel, $f.Basis)
        return [pscustomobject]$o
    }

    $cp = @()
    if (-not $AssumeUacOn) { $cp = @(Get-Process -Name CpStart -ErrorAction SilentlyContinue) }
    if ($cp.Count) {
        $e = Get-ProcessElevation $cp[0].Id
        if ($null -ne $e) {
            $o.RunLevel = $(if ($e) { 'Highest' } else { 'Limited' }); $o.Basis = 'cpstart_live'
            $o.Reason = ('running CpStart pid={0} elevated={1} - the task must match it.' -f $cp[0].Id, $e)
            return [pscustomobject]$o
        }
    }

    if ($broker -eq 'creon') {
        $o.RunLevel = 'Highest'; $o.Basis = 'broker_creon'
        $o.Reason = 'UAC on + BROKER=creon: LAUNCH_API.bat / start_mireuk.bat self-elevate, so CpStart runs elevated.'
    } elseif ($broker -eq 'cybos') {
        $lt = Get-ScheduledTask -TaskName 'Cybos Plus' -ErrorAction SilentlyContinue
        if ($lt) {
            $o.RunLevel = [string]$lt.Principal.RunLevel; $o.Basis = 'cybos_launch_task'
            $o.Reason = ("UAC on + BROKER=cybos: the session follows the 'Cybos Plus' launch task RunLevel={0}." -f $lt.Principal.RunLevel)
        } else {
            $o.RunLevel = 'Limited'; $o.Basis = 'broker_cybos'
            $o.Reason = "UAC on + BROKER=cybos, no 'Cybos Plus' task: LAUNCH_API.bat does not self-elevate for cybos."
        }
    } else {
        $o.Basis = 'unknown'
        $o.Reason = ("cannot decide: UAC={0}, BROKER='{1}', CpStart not measurable. Refusing to guess - pass -RunLevel." -f $uac, $broker)
    }
    return [pscustomobject]$o
}

function Write-ComRunLevelDecision($Decision, [string]$Explicit) {
    # Prints the decision; returns the RunLevel to use (explicit wins) or $null to refuse.
    Write-Host ("[runlevel] resolved={0} basis={1}" -f $(if ($Decision.RunLevel) { $Decision.RunLevel } else { '?' }), $Decision.Basis)
    Write-Host ("           {0}" -f $Decision.Reason)
    if ($Explicit) {
        if ($Decision.RunLevel -and $Explicit -ne $Decision.RunLevel -and $Decision.Basis -ne 'uac_off') {
            Write-Host ("[WARN] explicit -RunLevel {0} differs from the resolved {1} - the task will see IsConnect=0 every day." -f $Explicit, $Decision.RunLevel) -ForegroundColor Yellow
        }
        return $Explicit
    }
    if (-not $Decision.RunLevel) {
        Write-Host '[FAIL] RunLevel could not be resolved - not registering (a wrong level fails silently every day).' -ForegroundColor Red
    }
    return $Decision.RunLevel
}

function Test-CanRegisterRunLevel([string]$RunLevel) {
    if ($RunLevel -ne 'Highest') { return $true }
    if (Test-CurrentElevated) { return $true }
    Write-Host '[FAIL] RunLevel Highest must be registered from an elevated (admin) PowerShell.' -ForegroundColor Red
    return $false
}
