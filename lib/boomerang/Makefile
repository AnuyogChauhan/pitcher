
HOST := 'slow.secret.equipment'

deploy:
	cat boomerang_server.py | sed 's/8000/80/g' > boomerang_server1.py
	cp boomerang_server.py backupabc.py
	mv boomerang_server1.py boomerang_server.py
	fab -f deployment.py initMachine -u ubuntu -H $(HOST) 
	mv backupabc.py boomerang_server.py

connect:
	ssh -i ubuntu@$(HOST)
	#try 'screen -r' first
	#if there's no screen to resume, run 'screen'
	#sudo python boomerang_server.py
	#^a, d, exit

client:
	python boomerang_client.py $(HOST)

clientavg:
	python boomerang_client.py $(HOST) 10
