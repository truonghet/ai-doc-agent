// infra/bicep/main.bicep (skeleton)
param location string = resourceGroup().location
param searchName string
param appPlanName string
param appWebhookName string
param appRagName string

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: appPlanName
  location: location
  sku: { name: 'B1', tier: 'Basic', capacity: 1 }
}

resource appWebhook 'Microsoft.Web/sites@2023-12-01' = {
  name: appWebhookName
  location: location
  properties: { serverFarmId: plan.id }
}

resource appRag 'Microsoft.Web/sites@2023-12-01' = {
  name: appRagName
  location: location
  properties: { serverFarmId: plan.id }
}
