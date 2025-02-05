
```sh
sudo systemctl start docker
docker pull mongo:latest
```

```sh
sudo docker run -d \
    -p 27017:27017 \
    --name quintus-mongo \
    -v mongo-data:/data/db \
    mongo:latest
```


```sh
sudo docker start quintus-mongo
```

```sh
mongodb-compass
```

```sh
sudo docker stop quintus-mongo
```
