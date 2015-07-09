FROM  ubuntu:14.10

RUN apt-get update && apt-get install -y \
    curl \
    git

RUN curl 'https://storage.googleapis.com/golang/go1.4.2.linux-amd64.tar.gz' -o go.tgz
RUN tar -xvzf go.tgz -C /usr/local
RUN rm go.tgz

ADD ssh-key /root/.ssh/id_rsa
ADD ssh-key.pub /root/.ssh/id_rsa.pub
RUN chmod 0600 /root/.ssh/id_rsa

RUN git config --global url."git@git.aydo.com:".insteadOf "https://git.aydo.com/"

ENV GOPATH /root/go
RUN echo 'export PATH=/usr/local/go/bin:$PATH' > ~/.bashrc

RUN mkdir -p /root/.ssh/ && echo "" > /root/.ssh/known_hosts
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts
RUN ssh-keyscan git.aydo.com >> /root/.ssh/known_hosts
RUN cd && mkdir -p go

ADD setup_oauth.sh /root/setup_oauth.sh
ADD run.sh /root/run.sh

CMD [ "/root/run.sh" ]
