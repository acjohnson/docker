FULLTAG=registry.thejohnsons.site/debianbased:spamassassin
DOCKERFILE=Dockerfile
all: build

build:
	docker build -t $(FULLTAG) -f $(DOCKERFILE) .

rebuild:
	docker build --no-cache -t $(FULLTAG) -f $(DOCKERFILE) .

push: build
	docker push $(FULLTAG)
