
build:
	docker build -t shield -f docker/Dockerfile docker
	docker build -t shield-crontab -f docker/Dockerfile.crontab docker

server-run:
	docker run -p 3333:3333 -v $(PWD)/server:/server shield

restart-shield:
	docker-compose exec proxy nginx -s quit && docker-compose restart shield && docker-compose start proxy

fetch-code:
	git fetch && git stash && git merge origin/master && git stash pop

