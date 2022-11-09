# BE_blanball

## Install docker desktop 

>1. sudo apt update
>2. sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
>3. curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
>4. sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
>5. sudo apt install docker-ce

## Install docker-compose

>1. sudo curl -L "https://github.com/docker/compose/releases/download/1.29.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
>2. sudo chmod +x /usr/local/bin/docker-compose

## Run project

In the main directory `BE_blanball/project` run the command `sudo docker-compose up` or `sudo docker-compose up -d` this command will start the project without taking up your console
