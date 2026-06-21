n ?= 100000

setup:
	mkdir -p state

build-client:
	docker build -f ./deployment/client/Dockerfile -t "client:latest" .

build-gateway:
	docker build -f ./deployment/controllers/gateway/Dockerfile  -t "gateway:latest" .

build-result:
	docker build -f ./deployment/controllers/result/Dockerfile  -t "result:latest" .

build-selector:
	docker build -f ./deployment/controllers/selector/Dockerfile  -t "selector:latest" .

build-rentability:
	docker build -f ./deployment/controllers/rentability/Dockerfile  -t "rentability:latest" .

build-sentiment:
	docker build -f ./deployment/controllers/sentiment/Dockerfile  -t "sentiment:latest" .

build-year:
	docker build -f ./deployment/controllers/filter/year/Dockerfile  -t "year:latest" . 

build-containscountry:
	docker build -f ./deployment/controllers/filter/containscountry/Dockerfile  -t "containscountry:latest" .

build-onlyoneprodcountry:
	docker build -f ./deployment/controllers/filter/onlyoneprodcountry/Dockerfile  -t "onlyoneprodcountry:latest" .

build-unwind:
	docker build -f ./deployment/controllers/unwindcredits/Dockerfile  -t "unwindcredits:latest" .

build-sharder:
	docker build -f ./deployment/controllers/sharder/Dockerfile  -t "sharder:latest" .

build-usersplitter:
	docker build -f ./deployment/controllers/usersplitter/Dockerfile  -t "usersplitter:latest" .

build-userdispatcher:
	docker build -f ./deployment/controllers/userdispatcher/Dockerfile  -t "userdispatcher:latest" .

build-joiner:
	docker build -f ./deployment/controllers/joiner/Dockerfile  -t "joiner:latest" .

build-counter:
	docker build -f ./deployment/controllers/counter/Dockerfile  -t "counter:latest" .

build-splitter:
	docker build -f ./deployment/controllers/usersplitter/Dockerfile  -t "usersplitter:latest" .

build-dispatcher:
	docker build -f ./deployment/controllers/userdispatcher/Dockerfile  -t "userdispatcher:latest" .

build-sentiment-server:
	docker build -f ./deployment/sentiment-analyzer/Dockerfile  -t "analyzer:latest" .

build-health-checker:
	docker build -f ./deployment/health.Dockerfile -t "health:latest" .

docker-image: build-client build-gateway build-result build-selector build-year build-containscountry build-onlyoneprodcountry build-rentability build-sentiment build-unwind build-sharder build-splitter build-joiner build-dispatcher build-counter build-sentiment-server build-health-checker

docker-compose-up: docker-image setup
	docker compose -f compose.yml up -d --build

docker-compose-logs:
	docker compose -f compose.yml logs -f

docker-compose-down:
	docker compose -f compose.yml stop -t 1
	docker compose -f compose.yml down 

download-dataset:
	mkdir -p ./data
	curl -C - -L -o ./data/the-movies-dataset.zip https://www.kaggle.com/api/v1/datasets/download/rounakbanik/the-movies-dataset
	unzip -o ./data/the-movies-dataset.zip -d ./data

build-client-binary:
	go build -o bin/client ./cmd/client/main.go

build-binaries:
	go build -o bin/client/main ./cmd/client/main.go
	go build -o bin/controllers/filters/containscountry/main.go ./cmd/controllers/filters/containscountry/main.go
	go build -o bin/controllers/filters/onlyoneprodcountry/main.go ./cmd/controllers/filters/onlyoneprodcountry/main.go
	go build -o bin/controllers/filters/year/main.go ./cmd/controllers/filters/year/main.go
	go build -o bin/controllers/gateway/main.go ./cmd/controllers/gateway/main.go
	go build -o bin/controllers/rentability/main.go ./cmd/controllers/rentability/main.go
	go build -o bin/controllers/result/main.go ./cmd/controllers/result/main.go
	go build -o bin/controllers/selector/main.go ./cmd/controllers/selector/main.go
	go build -o bin/controllers/sentiment/main.go ./cmd/controllers/sentiment/main.go
	go build -o bin/controllers/counter/main.go ./cmd/controllers/counter/main.go
	go build -o bin/controllers/unwindcredits/main.go ./cmd/controllers/unwindcredits/main.go
	

run-sh-client:
	docker compose -f compose.yml run --rm --use-aliases --entrypoint sh client

clean-state:
	rm -f ./state/*

clean-results:
	rm -f ./data/1-*.csv
	rm -f ./data/2-*.csv
	rm -f ./data/3-*.csv
	rm -f ./data/4-*.csv
	rm -f ./data/5-*.csv

reboot: setup
	make docker-compose-down
	make clean-state
	make clean-results
	docker compose -f compose.yml up -d --build

build-base: build-client build-gateway build-result 

build-q1: build-base build-selector build-year build-containscountry

build-q2: build-base build-selector build-onlyoneprodcountry build-sharder

build-q4: build-base build-selector

build-q5: build-base build-selector build-rentability build-sentiment build-sentiment-server

sample-all:
	make sample file=./data/credits.csv n=$(n)
	make sample file=./data/movies_metadata.csv n=$(n)
	make sample file=./data/ratings.csv n=$(n)

sample:
	(head -n 1 $(file) && tail -n +2 $(file) | shuf -n $(n)) > $(file)-sample

compose: 
	python dockerize/dockerize.py --config dockerize/config.yml --output compose.yml

kill-unwinder:
	make kill-service service=unwindcredits

kill-top_appearances_0:
	make kill-service service=top_appearances_0

kill-service:
	make reboot
	sleep 4
	docker compose kill ${service}
	sleep 10
	docker compose run --rm ${service}

kill-killer:
	make reboot 
	python killer/killer.py --compose compose.yml --times 10 --seed 123

.PHONY: docker-image docker-compose-up docker-compose-logs docker-compose-down download-dataset sample
