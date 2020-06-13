FROM ubuntu:18.04
RUN apt-get update -y
RUN apt-get install -y python3 python3-pip redis-server

# copy directory to /controller
COPY . /controller
WORKDIR /controller

# install requirements according to requirements.txt
RUN pip3 install -r requirements.txt

# change controller name: currently "dummy"
CMD ["bash", "run.sh", "dummy"]