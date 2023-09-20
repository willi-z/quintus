
- https://phoenixnap.com/kb/kubernetes-mongodb

```sh
echo -n '<user_name>' | base64
<base64 encoded user_name>
```

```sh
echo -n '<password>' | base64
<base64 encoded password>
```


mongo/secrets.yaml
```yaml
apiVersion: v1
data:
  db-username: <base64 encoded user_name>
  db-password: <base64 encoded password>
kind: Secret
metadata:
  name: mongo-secrets
type: Opaque
```

postgres/secrets.yaml
```yaml
apiVersion: v1
data:
  db-username: <base64 encoded user_name>
  db-password: <base64 encoded password>
kind: Secret
metadata:
  name: postgres-secrets
type: Opaque
```


Build config
```sh
kubectl kustomize . > quintus.yaml
```
