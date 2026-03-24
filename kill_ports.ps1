$ports = @(3000, 8001)
foreach ($port in $ports) {
    $results = netstat -aon | Where-Object { $_ -match ":$port\s" }
    foreach ($line in $results) {
        $trimmed = $line.Trim()
        $parts = $trimmed -split '\s+'
        $procId = $parts[$parts.Count - 1]
        if ($procId -match '^\d+$' -and [int]$procId -ne 0) {
            Write-Host "Killing PID $procId on port $port"
            taskkill /F /PID $procId 2>$null
        }
    }
}
Write-Host "Done"
