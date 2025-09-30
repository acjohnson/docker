FULLTAG=registry.thejohnsons.site/debianbased:spamassassin-4.0.2
DOCKERFILE=Dockerfile
all: build

build:
	docker build -t $(FULLTAG) -f $(DOCKERFILE) .

rebuild:
	docker build --no-cache -t $(FULLTAG) -f $(DOCKERFILE) .

push: build
	docker push $(FULLTAG)
