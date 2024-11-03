# Makefile

# Define the directories containing the Dockerfiles
DOCKER_WEB_BROWSER_DIR := langrocks/docker/web_browser
DOCKER_CODE_INTERPRETER_DIR := langrocks/docker/code_interpreter

# Define the image names
WEB_BROWSER_IMAGE_NAME := langrocks-web-browser
CODE_INTERPRETER_IMAGE_NAME := langrocks-code-interpreter


# Define the build targets
.PHONY: all generate-stubs web-browser-image code-interpreter-image

all: generate-stubs web-browser-image code-interpreter-image

web-browser-image:
	@echo "Building browser image..."	
	docker build -t $(WEB_BROWSER_IMAGE_NAME) -f $(DOCKER_WEB_BROWSER_DIR)/Dockerfile .

code-interpreter-image:
	@echo "Building code interpreter image..."
	docker build -t $(CODE_INTERPRETER_IMAGE_NAME) -f $(DOCKER_CODE_INTERPRETER_DIR)/Dockerfile .

generate-stubs:
	@echo "Generating stubs..."
	python -m grpc_tools.protoc -I./langrocks/common/models --python_out=./langrocks/common/models --grpc_python_out=./langrocks/common/models ./langrocks/common/models/tools.proto

run-web-browser-container:
	@echo "Running web browser container..."
	docker run -it --rm --cap-add=SYS_ADMIN --name $(WEB_BROWSER_IMAGE_NAME) -p 50051-50053:50051-50053 -v ./langrocks/:/code/langrocks $(WEB_BROWSER_IMAGE_NAME) /bin/bash