# Variables
CONDA := conda
ENV_NAME := yt-summarizer
CONDA_ACTIVATE := source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate $(ENV_NAME)

# Default target
.PHONY: all
all: setup post-setup run

# Create conda environment and install dependencies
.PHONY: setup
setup:
	@echo "Creating conda environment..."
	@$(CONDA) env create -f environment.yml

# Post-setup steps
.PHONY: post-setup
post-setup:
	@echo "Running post-setup steps..."
	@$(CONDA_ACTIVATE) && pip install --upgrade --force-reinstall pytube
	@echo "Setup complete!"

# Run the application
.PHONY: run
run:
	@echo "Running YouTube Summarizer..."
	@$(CONDA_ACTIVATE) && python main.py

# Clean up generated files and environment
.PHONY: clean
clean:
	@echo "Cleaning up..."
	@$(CONDA) env remove -n $(ENV_NAME) -y
	@rm -rf summaries
	@rm -rf models
	@rm -f temp_audio.mp3
	@echo "Cleanup complete!"

# Update existing environment
.PHONY: update
update:
	@echo "Updating conda environment..."
	@$(CONDA) env update -f environment.yml
	@$(MAKE) post-setup
	@echo "Update complete!"

# Run the Gradio server
.PHONY: serve
serve:
	@echo "Starting Gradio server..."
	@$(CONDA_ACTIVATE) && python app.py

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  make setup      - Create conda environment and install dependencies"
	@echo "  make post-setup - Run post-setup configuration steps"
	@echo "  make run        - Run the YouTube Summarizer CLI"
	@echo "  make serve      - Start the Gradio web interface"
	@echo "  make clean      - Remove environment and generated files"
	@echo "  make update     - Update existing environment"
	@echo "  make all        - Setup, configure and run the application"
	@echo "  make help       - Show this help message" 