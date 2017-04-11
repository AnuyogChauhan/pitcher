
tag = car-network
ports = -p 5002:5002
broadcasttag = 127.0.0.1:5000/ens/car-network-ens-broadcast
clienttag = 127.0.0.1:5000/ens/car-network-ens-client

build: stop
	docker rmi -f $(tag) || echo "no such image"
	cp Dockerfile.traditional Dockerfile
	sudo docker rmi -f car-network || echo "no car-network image"
	docker build -t $(tag) ./
	rm Dockerfile

runinteractive: stop
	docker run -it --name=$(tag) $(ports) $(tag)
	
run: stop
	docker run -d --name=$(tag) $(ports) $(tag)

buildens:
	#cp Dockerfile.ens-client Dockerfile
	docker rmi -f $(clienttag) || echo "no such image"
	docker build -t $(clienttag) ./
	docker push $(clienttag)
	#cp Dockerfile.ens-broadcast Dockerfile
	docker rmi -f $(broadcasttag) || echo "no such image"
	docker build -t $(broadcasttag) ./
	docker push $(broadcasttag)
	#rm Dockerfile

init:
	if [ ! -d "env" ]; then /usr/bin/virtualenv -p /usr/bin/python3 env; fi
	#git submodule update --init
	. env/bin/activate
	env/bin/pip install parse
	env/bin/pip install python-osc
	env/bin/pip install pyserial


stop:
	docker stop $(tag) || echo "$(tag) not running"
	docker rm $(tag) || echo "$(tag) container not found"

test:
	python tests.py
