# Deploy Via Helm

Deployments are managed for BC Water Tool Consolidation via [Helm](https://helm.sh/docs/).

To perform the following command, it is assumed you are within `./charts/okd/app`.

```bash
helm upgrade --install bcwat . --namespace bcwat --create-namespace -f values.yaml
```

This creates a helm release, and creates a:
    - Frontend/Deployment
    - Frontend/Service
    - FrontEnd/ConfigMap
    - Backend/Deployment
    - Backend/Service

It is assumed that docker images for the FrontEnd/API/Migrations all exist within the azure container registry.
