# Verify platform health endpoints
$endpoints = @(
    @{ Name = "API Gateway"; Url = "http://localhost:5000/health" },
    @{ Name = "Auth"; Url = "http://localhost:5001/health" },
    @{ Name = "Product"; Url = "http://localhost:5002/health" },
    @{ Name = "Cart"; Url = "http://localhost:5003/health" },
    @{ Name = "Order"; Url = "http://localhost:5004/health" },
    @{ Name = "Payment"; Url = "http://localhost:5005/health" },
    @{ Name = "Notification"; Url = "http://localhost:5006/health" },
    @{ Name = "Frontend"; Url = "http://localhost:3000/" }
)

Write-Host "=== Platform Health Verification ===" -ForegroundColor Cyan
$passed = 0
foreach ($ep in $endpoints) {
    try {
        $r = Invoke-WebRequest -Uri $ep.Url -TimeoutSec 5 -UseBasicParsing
        Write-Host "[PASS] $($ep.Name) - $($r.StatusCode)" -ForegroundColor Green
        $passed++
    } catch {
        Write-Host "[FAIL] $($ep.Name) - $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host "`nResult: $passed/$($endpoints.Count) services reachable" -ForegroundColor $(if ($passed -eq $endpoints.Count) { "Green" } else { "Yellow" })
