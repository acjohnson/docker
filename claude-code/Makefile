FULLTAG=claude-code-node-22-trixie:latest
DOCKERFILE=Dockerfile
all: build

build:
	docker build -t $(FULLTAG) -f $(DOCKERFILE) .

build-clean:
	docker build --no-cache -t $(FULLTAG) -f $(DOCKERFILE) .
