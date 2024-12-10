
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class InputBlocker {{
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool BlockInput(bool fBlockIt);
}}
"@

    [InputBlocker]::BlockInput($true)
    