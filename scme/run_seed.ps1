param(
    [string]$ServerInstance = ".\\SQLEXPRESS"
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$sqlFile = Join-Path $scriptDir 'seed.sql'
if (-not (Test-Path $sqlFile)) { Write-Error "seed.sql not found"; exit 1 }

$content = Get-Content -Raw -Path $sqlFile
$batches = $content -split "(?im)^GO\s*$"

$connString = "Server=$ServerInstance;Database=ReportesSistemaSeguridad;Integrated Security=SSPI;TrustServerCertificate=True;"

$batchIndex = 0
foreach ($b in $batches) {
    $batchIndex++
    $t = $b.Trim()
    if ($t -eq '') { continue }
    Write-Host "Executing batch $batchIndex (len=$($t.Length))"
    try {
        $conn = New-Object System.Data.SqlClient.SqlConnection $connString
        $conn.Open()
        $cmd = $conn.CreateCommand(); $cmd.CommandTimeout = 1200; $cmd.CommandText = $t
        $cmd.ExecuteNonQuery() | Out-Null
        $conn.Close()
        Write-Host "Batch $batchIndex OK"
    } catch {
        Write-Host "Batch $batchIndex ERROR: $($_.Exception.Message)"
        if ($conn -and $conn.State -eq 'Open') { $conn.Close() }
    }
}

# Run verification selects and print results
$ver = @(
"SELECT 'TipoSangre' AS tabla, IdSangre, Nombre FROM dbo.TipoSangre ORDER BY IdSangre;",
"SELECT 'PersonaEmergencia' AS tabla, IdPersonaEmergencia, Nombres, Apellidos, TelefonoPersonal FROM dbo.PersonaEmergencia ORDER BY IdPersonaEmergencia;",
"SELECT 'Persona' AS tabla, IdPersona, Nombres, Apellidos, Correo, CI FROM dbo.Persona ORDER BY IdPersona;",
"SELECT 'Tarjeta' AS tabla, IdTarjeta, TarjetaUID, FechaFabricacion FROM dbo.Tarjeta ORDER BY IdTarjeta;",
"SELECT 'Enrolar' AS tabla, IdEnrolar, IdPersona, TarjetaUID, IdPerfilAccesoLab FROM dbo.Enrolar ORDER BY IdEnrolar;",
"SELECT 'RegistroAcceso' AS tabla, IdRegistroAcceso, TarjetaUID, FechaHora, IdTipoMovimiento, IdTipoDispositivo, Descripcion FROM dbo.RegistroAcceso ORDER BY IdRegistroAcceso DESC;"
)

$conn = New-Object System.Data.SqlClient.SqlConnection $connString
$conn.Open()
foreach ($q in $ver) {
    Write-Host "\n--- Query: $q`n"
    $cmd = $conn.CreateCommand(); $cmd.CommandText = $q
    $da = New-Object System.Data.SqlClient.SqlDataAdapter $cmd
    $dt = New-Object System.Data.DataTable
    [void]$da.Fill($dt)
    Write-Host "Rows: $($dt.Rows.Count)"
    if ($dt.Rows.Count -gt 0) { $dt | Format-Table -AutoSize }
}
$conn.Close()
Write-Host "Seed complete."