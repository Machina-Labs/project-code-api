.PHONY: deploy local-docker local
CURRENT_DIRECTORY := $(shell pwd)
make_activate_env_SCRIPT := $(CURRENT_DIRECTORY)/make_activate_env.sh

make_activate_env:
	$(make_activate_env_SCRIPT)

local-prod: make_activate_env
	@echo "Make sure to conda activate pcode"
	@echo "Running PROD in local mode"
	# @git checkout main
	@sudo docker build -t project-code-api:latest .
	@sudo docker run -p 8000:8000 project-code-api:latest

local-dev: make_activate_env
	@echo "Make sure to conda activate pcode"
	@echo "Running DEV in local mode"
	# if you dont want to rebuild entirely, you can run sudo docker build -t project-code-api
	# @git checkout dev
	@sudo docker build -t project-code-api:dev . --no-cache
	@sudo docker run -p 8000:8000 project-code-api:dev

deploy-prod: make_activate_env
	@echo "Deploying PROD to Azure"
	# @git checkout main
	# @sudo docker login machinacr.azurecr.us
	@sudo docker build -t project-code-api:latest . --no-cache
	@sudo docker tag project-code-api:latest machinacr.azurecr.us/project-code-api:latest
	@sudo docker push machinacr.azurecr.us/project-code-api:latest

deploy-dev: make_activate_env
	@echo "Deploying DEV to Azure"
	@git checkout dev
	@sudo docker login machinacr.azurecr.us
	@sudo docker build -t project-code-api:dev . --no-cache
	@sudo docker tag project-code-api:dev machinacr.azurecr.us/project-code-api:dev
	@sudo docker push machinacr.azurecr.us/project-code-api:dev

# machinalabs.ioma
poetry-prod:
	@git checkout main
	@poetry run python app.py

poetry-dev:
	@git checkout dev
	@poetry run python app.py