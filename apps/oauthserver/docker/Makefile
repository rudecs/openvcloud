ssh-key:
	[[ -f ssh-key -a -f ssh-key.pub ]] || ssh-keygen -f ssh-key

build: ssh-key
	docker build -t oauth .

run:
	docker run -itd --name oauth \
		-v ${HOME}/dockerfs/oauth:/root/go \
		oauth

enter:
	docker-enter oauth

stop:
	docker stop oauth
	docker rm oauth
