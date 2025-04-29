# Persistent Volume/Persistent Volume Claim

This requires an NFS Server to be configured.

On the Foundry OnPrem server, we have an NFS Server mounted on `controlplane0`.

To ensure logs persist even when a Pod is evicted, this is required.

Pods also will not get scheduled properly via the scheduler, due to our `pod_templates`  expecting a volume to exist titled `airflow-logs`.

Therefore, these must be configured prior to deploying on Openshift.

To create PV/PVC onPrem:

```bash
oc apply -f okd/
```
