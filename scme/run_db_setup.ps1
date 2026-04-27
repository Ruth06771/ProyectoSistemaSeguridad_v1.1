<#
run_db_setup.ps1
Usage: run in PowerShell on a machine with sqlcmd available and access to SQL Server.
Example: .\run_db_setup.ps1 -ServerInstance ".\SQLEXPRESS" -UseWindowsAuth
#>
param(
    [string]$ServerInstance = ".\SQLEXPRESS",
    [switch]$UseWindowsAuth,
    [string]$SqlFile = "SQLQuery2_improved.sql",
    [string]$OutputFile = "db_setup_report.txt"
)

function Check-SqlCmd {
    $sq = Get-Command sqlcmd -ErrorAction SilentlyContinue
    if ($null -eq $sq) { return $false }
    return $true
}

if (-not (Test-Path (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) $SqlFile))) {
    Write-Error "SQL file '$SqlFile' not found in script directory."
    exit 1
}

if (-not (Check-SqlCmd)) {
    Write-Error "sqlcmd not found in PATH. Please install SQL Server tools (sqlcmd) or run from SSMS." ; exit 2
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$fullSql = Join-Path $scriptDir $SqlFile
$out = Join-Path $scriptDir $OutputFile
if (Test-Path $out) { Remove-Item $out -Force }

Write-Host "Running DB setup using sqlcmd against instance: $ServerInstance" | Tee-Object -FilePath $out -Append

# Build auth params
if ($UseWindowsAuth) { $authParams = "-E" } else { $authParams = "-U sa -P <YourPasswordHere>" }

# Execute the SQL file
Write-Host "Executing SQL file: $fullSql" | Tee-Object -FilePath $out -Append
$sqlcmdCmd = "sqlcmd -S `"$ServerInstance`" $authParams -i `"$fullSql`""
Write-Host "Command: $sqlcmdCmd" | Tee-Object -FilePath $out -Append
try {
    iex $sqlcmdCmd 2>&1 | Tee-Object -FilePath $out -Append
} catch {
    Write-Host "Execution failed: $_" | Tee-Object -FilePath $out -Append
    exit 3
}

Write-Host "Running verification queries..." | Tee-Object -FilePath $out -Append
$verQueries = @(
    "USE ReportesSistemaSeguridad; SELECT 'Tables' AS Item, TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES ORDER BY TABLE_SCHEMA, TABLE_NAME;",
    "USE ReportesSistemaSeguridad; SELECT fk.name AS FKName, tp.name AS ParentTable, rc.name AS ReferencedTable FROM sys.foreign_keys fk JOIN sys.tables tp ON fk.parent_object_id = tp.object_id JOIN sys.tables rc ON fk.referenced_object_id = rc.object_id;",
    "USE ReportesSistemaSeguridad; SELECT name, type_desc FROM sys.indexes WHERE object_id = OBJECT_ID('RegistroAcceso');",
    "USE ReportesSistemaSeguridad; SELECT name, type_desc FROM sys.indexes WHERE object_id = OBJECT_ID('Enrolar');"
)

foreach ($q in $verQueries) {
    Write-Host "-- Query: $q" | Tee-Object -FilePath $out -Append
    sqlcmd -S "$ServerInstance" $authParams -Q "$q" 2>&1 | Tee-Object -FilePath $out -Append
}

Write-Host "Verification complete. Report saved to $out" | Tee-Object -FilePath $out -Append
Write-Host "Done." | Tee-Object -FilePath $out -Append
