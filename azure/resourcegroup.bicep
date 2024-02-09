targetScope='subscription'

param rg_name string
param rg_location string

resource newRG 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: rg_name
  location: rg_location
}
