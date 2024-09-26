# Path to the blocklist file
$blocklistPath = "C:\powershell\admins_blocklist.txt"

# Read the blocklist from the file
$blocklist = Get-Content -Path $blocklistPath

foreach ($site in $blocklist) {
    # Remove existing rule if it exists
    Remove-NetFirewallRule -DisplayName "Block $site" -ErrorAction SilentlyContinue
    
    # Add a new rule to block the site
    New-NetFirewallRule -DisplayName "Block $site" -Direction Outbound -Action Block -RemoteAddress $site
}