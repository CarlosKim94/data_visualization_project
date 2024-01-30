.DEFAULT := help
.PHONY := help all


all: launch ## Execute downloader


# deps-install: ## Install dependencies
# 	pip install -r requirements.txt

# deps-uninstall: ## Uninstall dependencies
# 	pip uninstall -y -r requirements.txt

launch:
	streamlit run main.py
