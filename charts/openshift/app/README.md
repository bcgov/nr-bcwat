# Deploy Via Helm

Deployments are managed for BC Water Tool Consolidation via [Helm](https://helm.sh/docs/).

BCGov Openshift - Dev

```bash
helm upgrade --install bcwat . --namespace cdd771-dev -f values.yaml
```
