# Makefile for LaTeX Beamer Presentation
# Project: LLM and AI Agent Systems Tutorial

# Variables
MAIN = main
BUILD_DIR = build
LATEX = pdflatex
BIBTEX = biber
VIEWER = open

# LaTeX flags
LATEX_FLAGS = -interaction=nonstopmode -output-directory=$(BUILD_DIR)

# Output PDF
PDF = $(BUILD_DIR)/$(MAIN).pdf

# Default target
.PHONY: all
all: pdf

# Build PDF with full bibliography compilation
.PHONY: pdf
pdf:
	@echo "Building PDF with bibliography..."
	@mkdir -p $(BUILD_DIR)
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	cd $(BUILD_DIR) && BIBINPUTS=..:../bibliography: $(BIBTEX) $(MAIN)
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	@echo "Build complete: $(PDF)"

# Quick build (single pass, no bibliography)
.PHONY: quick
quick:
	@echo "Quick build (single pass)..."
	@mkdir -p $(BUILD_DIR)
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	@echo "Quick build complete: $(PDF)"

# View PDF
.PHONY: view
view: pdf
	@if command -v $(VIEWER) > /dev/null; then \
		$(VIEWER) $(PDF) &; \
	elif command -v xdg-open > /dev/null; then \
		xdg-open $(PDF) &; \
	else \
		echo "No PDF viewer found. Please open $(PDF) manually."; \
	fi

# Watch mode (continuous compilation)
.PHONY: watch
watch:
	@echo "Watch mode not implemented. Use 'make pdf' to rebuild."

# Clean temporary files
.PHONY: clean
clean:
	@echo "Cleaning temporary files..."
	@rm -f $(BUILD_DIR)/*.aux \
	       $(BUILD_DIR)/*.log \
	       $(BUILD_DIR)/*.out \
	       $(BUILD_DIR)/*.toc \
	       $(BUILD_DIR)/*.nav \
	       $(BUILD_DIR)/*.snm \
	       $(BUILD_DIR)/*.bbl \
	       $(BUILD_DIR)/*.blg \
	       $(BUILD_DIR)/*.bcf \
	       $(BUILD_DIR)/*.run.xml \
	       $(BUILD_DIR)/*.vrb \
	       $(BUILD_DIR)/*.synctex.gz \
	       $(BUILD_DIR)/.DS_Store
	@echo "Temporary files cleaned."

# Clean all including PDF
.PHONY: cleanall
cleanall: clean
	@echo "Removing PDF output..."
	@rm -f $(PDF)
	@echo "All build files removed."

# Rebuild from scratch
.PHONY: rebuild
rebuild: cleanall pdf

# Show help
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  make           - Build PDF with bibliography (default)"
	@echo "  make pdf       - Build PDF with bibliography"
	@echo "  make quick     - Quick build (single pass, no bibliography)"
	@echo "  make view      - Build and open PDF in viewer"
	@echo "  make clean     - Remove temporary files"
	@echo "  make cleanall  - Remove all build files including PDF"
	@echo "  make rebuild   - Clean and rebuild from scratch"
	@echo "  make help      - Show this help message"
