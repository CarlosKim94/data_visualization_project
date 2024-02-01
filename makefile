.DEFAULT := help
.PHONY := help all


all: deps-install launch ## Execute downloader


deps-install: ## Install dependencies
	pip3 install -r ./requirements.txt

# deps-uninstall: ## Uninstall dependencies
	# pip uninstall -y -r requirements.txt

launch:
	streamlit run main.py
