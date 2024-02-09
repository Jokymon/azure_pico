// Not using any file upload functions so far
// @secure()
// param IotHubs_rpipicohub_connectionString string
// @secure()
// param IotHubs_rpipicohub_containerName string

param hub_name string
param hub_location string

resource IotHubs_rpipicohub_name_resource 'Microsoft.Devices/IotHubs@2023-06-30' = {
  name: hub_name
  location: hub_location
  sku: {
    name: 'F1'
    capacity: 1
  }
  identity: {
    type: 'None'
  }
  properties: {
    ipFilterRules: []
    eventHubEndpoints: {
      events: {
        retentionTimeInDays: 1
        partitionCount: 2
      }
    }
    routing: {
      endpoints: {
        serviceBusQueues: []
        serviceBusTopics: []
        eventHubs: []
        storageContainers: []
        cosmosDBSqlContainers: []
      }
      routes: []
      fallbackRoute: {
        name: '$fallback'
        source: 'DeviceMessages'
        condition: 'true'
        endpointNames: [
          'events'
        ]
        isEnabled: true
      }
    }
    // Not using any file upload functions so far
    // storageEndpoints: {
    //   '$default': {
    //     sasTtlAsIso8601: 'PT1H'
    //     connectionString: IotHubs_rpipicohub_connectionString
    //     containerName: IotHubs_rpipicohub_containerName
    //   }
    // }
    messagingEndpoints: {
      fileNotifications: {
        lockDurationAsIso8601: 'PT1M'
        ttlAsIso8601: 'PT1H'
        maxDeliveryCount: 10
      }
    }
    enableFileUploadNotifications: false
    cloudToDevice: {
      maxDeliveryCount: 10
      defaultTtlAsIso8601: 'PT1H'
      feedback: {
        lockDurationAsIso8601: 'PT1M'
        ttlAsIso8601: 'PT1H'
        maxDeliveryCount: 10
      }
    }
    features: 'RootCertificateV2'
    disableLocalAuth: false
    allowedFqdnList: []
    enableDataResidency: false
  }
}
