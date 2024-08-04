$apiUrl = "https:\\192.168.10.118\8000\add_user_logs"

function Send-UserData {
    param(
        [string]$firstName,
        [string]$lastName,
        [string]$middleName
    )

    $userData = @{
        firstName = $firstName
        lastName = $lastName
        middleName = $middleName
        dateTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }

    try {
        $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Body $userData -ContentType "application/json"
        if ($response.StatusCode -eq 200) {
            Write-Host "Data sent successfully!"
        } else {
            Write-Host "API call failed with status code: $($response.StatusCode)"
        }
    } catch [System.Net.WebException] {
        Write-Host "An error occurred: $_"
    }
}

$user = Get-ADUser -Identity $env:USERNAME

$firstName = $user.GivenName
$lastName = $user.Surname
$middleName = $user.MiddleName 

Send-UserData -firstName $firstName -lastName $lastName -middleName $middleName

$value = "5"
Add-Content -Path "C:\Users\Administrator\Desktop\logon_log.txt" -Value $value