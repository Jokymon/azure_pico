. ./azure/config.ps1

# TODO: consider using a parameter file?
az deployment sub create --location $Location --template-file .\azure\resourcegroup.bicep --parameters rg_name=$ResourceGroup rg_location=$Location
az deployment group create --template-file .\azure\iothub.bicep -g $ResourceGroup --parameters hub_name=$IothubName hub_location=$Location
