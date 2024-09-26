# Define blocklist path and read content
$blocklistPath = "C:\powershell\students_blocklist.txt"
$sites = Get-Content -Path $blocklistPath

# Loop through each site and create a firewall rule
foreach ($site in $sites) {
    # Resolve IP addresses for the site
    $ipAddresses = (Resolve-DnsName -Name $site -Type A).IPAddress

    # Create a firewall rule for each IP address
    foreach ($ip in $ipAddresses) {
        New-NetFirewallRule -DisplayName "Block $ip" -Direction Outbound -Action Block -RemoteAddress $ip
    }
}