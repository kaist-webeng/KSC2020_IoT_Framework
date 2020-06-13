# WebEng IoT Testbed: resource-controller

Source codes of resource controllers in WebEng IoT testbed, written in Python  
Docker + Flask + Redis

---
## How to run a controller

1. install [docker](https://www.docker.com/)
2. modify Dockerfile's CMD line: choose appropriate filename of controller to run
3. build docker image from Dockerfile:
```
docker build -t WebEng-{controller name}-controller:latest .
```

4. run the docker image to construct a container:
```
docker run -d -p 5000:5000 WebEng-{controller name}-controller:latest
```

---
## How to add a new controller
You can copy <code>dummy.py</code>, or following below instruction
1. add a new controller file, name as <code>{controller name}_controller.py</code>
2. from <code>base.py</code>, import <code>ResourceAPI</code> and define new resource's API by inherit it, name as <code>class {controller name}API</code>
3. implement all abstract methods
4. write execution code of flask app

---
## TODO
- [ ] WSGI
- [ ] Visualization of the architecture
- [ ] Docker compose (divide Flask, Redis, NginX to different containers)