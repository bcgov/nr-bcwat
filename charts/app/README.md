# Deploy Via Helm

Deployments are managed for BC Water Tool Consolidation via [Helm](https://helm.sh/docs/).

To perform the following command, it is assumed you are within `./charts/app`.

Currently, the only release that exists is on the Foundry OKD. Therefore, the only command that we run from this directory is the following:

```bash
helm upgrade --install bcwat . --namespace bcwat --create-namespace -f values.base.yaml -f values.okd.yaml
```

This creates a helm release, and creates a:
    - Client Deployment
    - Client Service
    - Backend Deployment
    - Backend Service
    - Config Map

This assumes that docker images exist for both the client & api and are present on the OKD internal registry.
