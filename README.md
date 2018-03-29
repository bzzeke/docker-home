# Home infrastructure management

How to setup:
```
git clone --recursive git@github.com:bzzeke/docker-home.git
cd docker-home
cp .env.dist .env
vi .env
```

Latest version of docker must be installed to support `ARG` before `FROM` in `Dockerfile`!

How to build:
* `docker-compose build` - builds default (`amd64`) arch
* `docker-compose build --build-arg arch=arm32v6` - builds images for Raspberry Pi

How to run:

`docker-compose run SERVICE_NAME`
