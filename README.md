# WebEng IoT Testbed: resource-controller

Source codes of resource controllers in WebEng IoT testbed, written in Python  
Docker + Flask + Redis + Gunicorn

---
## How to run a controller

1. install [docker](https://www.docker.com/)
2. modify Dockerfile's CMD line: choose appropriate filename of controller to run
```
CMD ["bash", "run.sh", "{controller name}"]
```

3. build docker image from Dockerfile:
```
docker build -t webeng-{controller name}-controller:latest .
```

4. run the docker image to construct a container:
```
docker run -d -p 8000:8000 webeng-{controller name}-controller:latest
```
The format of port option is `{host's port}:{container's port}`.  
You can also set a name of the container by using `--name {name}` option.

---
## How to add a new controller
You can copy <code>dummy_controller.py</code>, or following below instruction
1. add a new controller file, name as <code>{controller name}_controller.py</code>
2. from <code>base.py</code>, import <code>ResourceAPI</code> and define new resource's API by inherit it, name as <code>class {controller name}API</code>
3. implement all abstract methods
4. write execution code of flask app

---
### TODO
- [x] WSGI: Gunicorn integrated
- [ ] Visualization of the architecture

### Issue
- [x] Docker compose (divide Flask, Redis, NginX to different containers): maintain one container for each controller

---
### Frequently used commands of Docker
- `docker ps` shows every containers. `-a` option shows stopped containers. `-l` option shows latest containers.
- `docker logs {container ID}` shows execution logs of the container.
- `docker kill {container ID}` kills the container by sending a `SIGKILL` signal.
- `docker system prune` removes all stopped containers, dangling images, unused networks.
- `docker rm $(docker ps -a -q)` removes all docker containers
