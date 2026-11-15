# Windows GUI startup smoke test for InMan.
#
# Compilation alone cannot prove that the desktop application starts. This
# script launches the real executable, waits for a visible top-level "InMan"
# window owned by that process, verifies that the first UI frame was rendered,
# checks that the process remains alive, closes it with WM_CLOSE and requires a
# clean exit. It then relaunches against the database created by the first run
# to prove the application can reopen. All startup diagnostics are preserved.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Executable,

    # Optional existing SQLite database to copy into the isolated test folder.
    [string]$DatabaseSource,

    [int]$StartupTimeoutSeconds = 90,
    [int]$StabilitySeconds = 10,
    [int]$ShutdownTimeoutSeconds = 30
)

$ErrorActionPreference = 'Stop'

Add-Type -TypeDefinition @"
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;

public static class InManWin32
{
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc callback, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool IsWindow(IntPtr hWnd);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int maxCount);

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);

    [DllImport("user32.dll")]
    public static extern bool PostMessage(IntPtr hWnd, uint message, IntPtr wParam, IntPtr lParam);

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }
}
"@

function Get-VisibleWindowsForProcess {
    param([int]$ProcessId)

    $windows = [System.Collections.Generic.List[object]]::new()
    $callback = [InManWin32+EnumWindowsProc]{
        param([IntPtr]$handle, [IntPtr]$state)

        [uint32]$owner = 0
        [void][InManWin32]::GetWindowThreadProcessId($handle, [ref]$owner)
        if ($owner -ne $ProcessId -or -not [InManWin32]::IsWindowVisible($handle)) {
            return $true
        }

        $title = [System.Text.StringBuilder]::new(512)
        [void][InManWin32]::GetWindowText($handle, $title, $title.Capacity)

        $rect = New-Object InManWin32+RECT
        [void][InManWin32]::GetWindowRect($handle, [ref]$rect)
        $windows.Add([pscustomobject]@{
            Handle = $handle
            Title  = $title.ToString()
            Width  = $rect.Right - $rect.Left
            Height = $rect.Bottom - $rect.Top
        })
        return $true
    }

    [void][InManWin32]::EnumWindows($callback, [IntPtr]::Zero)
    return $windows
}

function Read-LogAfterOffset {
    param([string]$Path, [long]$Offset)

    if (-not (Test-Path -LiteralPath $Path)) { return '' }
    $stream = [System.IO.File]::Open(
        $Path,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read,
        [System.IO.FileShare]::ReadWrite)
    try {
        if ($Offset -gt $stream.Length) { $Offset = 0 }
        $stream.Position = $Offset
        $reader = [System.IO.StreamReader]::new($stream, [System.Text.Encoding]::UTF8)
        try { return $reader.ReadToEnd() } finally { $reader.Dispose() }
    }
    finally {
        $stream.Dispose()
    }
}

function Read-LogLength {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return [long]0 }
    return [long](Get-Item -LiteralPath $Path).Length
}

function Wait-ForLogText {
    param(
        [string]$Path,
        [long]$Offset,
        [string]$Pattern,
        [int]$TimeoutSeconds
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        $text = Read-LogAfterOffset -Path $Path -Offset $Offset
        if ($text -match $Pattern) { return $text }
        Start-Sleep -Milliseconds 250
    } while ((Get-Date) -lt $deadline)
    return $null
}

function Wait-ForVisibleWindow {
    param(
        [int]$ProcessId,
        [string]$ExpectedTitle,
        [int]$TimeoutSeconds
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        if (-not $process) {
            throw "InMan exited before creating a window."
        }
        $window = Get-VisibleWindowsForProcess -ProcessId $ProcessId |
            Where-Object {
                $_.Title -eq $ExpectedTitle -and $_.Width -ge 400 -and $_.Height -ge 300
            } |
            Select-Object -First 1
        if ($window) { return $window }
        Start-Sleep -Milliseconds 250
    } while ((Get-Date) -lt $deadline)

    throw "InMan did not create a visible '$ExpectedTitle' window within $TimeoutSeconds seconds."
}

function Close-InManWindow {
    param(
        [System.Diagnostics.Process]$Process,
        [IntPtr]$WindowHandle,
        [int]$TimeoutSeconds
    )

    [void][InManWin32]::PostMessage($WindowHandle, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) # WM_CLOSE
    if (-not $Process.WaitForExit($TimeoutSeconds * 1000)) {
        try { $Process.Kill() } catch { }
        throw "InMan did not close cleanly within $TimeoutSeconds seconds."
    }
    if ($Process.ExitCode -ne 0) {
        throw "InMan exited with code $($Process.ExitCode) instead of 0 after WM_CLOSE."
    }
}

$executablePath = (Resolve-Path -LiteralPath $Executable).Path
if (-not (Test-Path -LiteralPath $executablePath -PathType Leaf)) {
    throw "Executable not found: $Executable"
}

$logPath = Join-Path $env:LOCALAPPDATA 'InMan\logs\inman.log'
$artifactDirectory = Join-Path (Get-Location) 'target\startup-smoke'
New-Item -ItemType Directory -Force -Path $artifactDirectory | Out-Null

$testDirectory = Join-Path ([System.IO.Path]::GetTempPath()) "inman-startup-smoke-$PID"
if (Test-Path -LiteralPath $testDirectory) {
    Remove-Item -LiteralPath $testDirectory -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $testDirectory | Out-Null

if ($DatabaseSource) {
    if (-not (Test-Path -LiteralPath $DatabaseSource -PathType Leaf)) {
        throw "Database source not found: $DatabaseSource"
    }
    Copy-Item -LiteralPath $DatabaseSource -Destination (Join-Path $testDirectory 'inventory.db')
    Write-Host "Using a copy of $DatabaseSource"
}

function Invoke-InManStartupCheck {
    param(
        [string]$Label,
        [string]$WorkingDirectory,
        [string]$ExpectedDatabase
    )

    $logOffset = Read-LogLength -Path $logPath
    $process = Start-Process -FilePath $executablePath -WorkingDirectory $WorkingDirectory -PassThru
    try {
        Write-Host "[$Label] started pid $($process.Id)"
        $window = Wait-ForVisibleWindow -ProcessId $process.Id -ExpectedTitle 'InMan' `
            -TimeoutSeconds $StartupTimeoutSeconds
        Write-Host "[$Label] visible window: handle=$($window.Handle) size=$($window.Width)x$($window.Height) title='$($window.Title)'"

        $process.Refresh()
        if ($process.HasExited) {
            throw "[$Label] InMan exited immediately after showing its window."
        }
        if (-not $process.Responding) {
            throw "[$Label] InMan's window is not responding."
        }

        $logText = Wait-ForLogText -Path $logPath -Offset $logOffset `
            -Pattern 'first UI frame rendered' -TimeoutSeconds 30
        if (-not $logText) {
            throw "[$Label] The window appeared but no UI frame was recorded in the startup log."
        }

        Start-Sleep -Seconds $StabilitySeconds
        $process.Refresh()
        if ($process.HasExited) {
            throw "[$Label] InMan terminated unexpectedly $StabilitySeconds seconds after startup."
        }
        if (-not [InManWin32]::IsWindow($window.Handle) -or
            -not [InManWin32]::IsWindowVisible($window.Handle)) {
            throw "[$Label] The InMan window disappeared while the process was still running."
        }

        if ($ExpectedDatabase -and -not (Test-Path -LiteralPath $ExpectedDatabase)) {
            throw "[$Label] InMan did not create or open the inventory database at $ExpectedDatabase."
        }

        $logText = Read-LogAfterOffset -Path $logPath -Offset $logOffset
        if ($logText -match 'panic on thread|InMan failed to start|eframe could not start') {
            throw "[$Label] Startup log contains a fatal error:`n$logText"
        }

        # Guard the Windows startup fix: Vulkan must not be selected implicitly.
        if (-not $env:WGPU_BACKEND -and
            $logText -notmatch 'configured wgpu backend\(s\): Backends\(DX12\)') {
            throw "[$Label] Windows startup did not configure the DX12 backend:`n$logText"
        }
        if ($logText -match 'backend Vulkan|Backends\(VULKAN') {
            throw "[$Label] InMan selected the Vulkan backend, which crashed the affected Intel driver:`n$logText"
        }

        Close-InManWindow -Process $process -WindowHandle $window.Handle `
            -TimeoutSeconds $ShutdownTimeoutSeconds
        Write-Host "[$Label] closed cleanly with exit code 0"
    }
    catch {
        $logText = Read-LogAfterOffset -Path $logPath -Offset $logOffset
        if ($logText) {
            Write-Host "[$Label] startup log:"
            Write-Host $logText
        }
        if (-not $process.HasExited) {
            try { $process.Kill() } catch { }
        }
        throw
    }
}

try {
    $databasePath = Join-Path $testDirectory 'inventory.db'
    if ($DatabaseSource) {
        Invoke-InManStartupCheck -Label 'existing-database' -WorkingDirectory $testDirectory `
            -ExpectedDatabase $databasePath
        Write-Host 'First launch used the supplied database copy.'
    }
    else {
        # The unactivated application must show its activation screen without
        # creating a database or bypassing product-key verification. A database
        # is initialized only after successful product activation.
        Invoke-InManStartupCheck -Label 'first-launch-unactivated' -WorkingDirectory $testDirectory
        Write-Host 'First launch displayed the activation screen without requiring a database.'
    }

    if ($DatabaseSource) {
        Invoke-InManStartupCheck -Label 'reopen-existing-database' -WorkingDirectory $testDirectory `
            -ExpectedDatabase $databasePath
    } else {
        Invoke-InManStartupCheck -Label 'reopen-unactivated' -WorkingDirectory $testDirectory
    }
    Write-Host 'InMan reopened and closed cleanly a second time.'
}
finally {
    if (Test-Path -LiteralPath $logPath) {
        Copy-Item -LiteralPath $logPath -Destination (Join-Path $artifactDirectory 'inman.log') -Force
    }
    if (Test-Path -LiteralPath $testDirectory) {
        Copy-Item -LiteralPath $testDirectory -Destination (Join-Path $artifactDirectory 'test-directory') -Recurse -Force
        Remove-Item -LiteralPath $testDirectory -Recurse -Force -ErrorAction SilentlyContinue
    }
}

