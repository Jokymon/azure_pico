param(
    [Parameter(Mandatory=$true)]
    [string]$DeviceId
)
. ./azure/config.ps1

$response=az iot hub device-identity create --hub-name $IothubName --device-id $DeviceId

$ResponseJson = $Response | ConvertFrom-Json
$PrimaryKey = $ResponseJson.authentication.symmetricKey.primaryKey
$HostName = "$IothubName.azure-devices.net"

$Output = @{
    'deviceid' = $DeviceId
    'hostname' = $HostName
    'primarykey' = $PrimaryKey
}

$Output | ConvertTo-Json | Out-File -FilePath .\pico_config\azure-$DeviceId.json -Encoding utf8