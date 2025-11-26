#!/bin/bash
# Compile Beamer Presentation

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

MAIN_FILE="${1:-main.tex}"
OUTPUT_DIR="build"

echo -e "${YELLOW}Compiling $MAIN_FILE...${NC}"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Compile with latexmk (handles multiple passes automatically)
latexmk -pdf \
    -pdflatex="pdflatex -interaction=nonstopmode -shell-escape" \
    -outdir="$OUTPUT_DIR" \
    -auxdir="$OUTPUT_DIR" \
    "$MAIN_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Compilation successful!${NC}"
    echo -e "${GREEN}Output: $OUTPUT_DIR/$(basename ${MAIN_FILE%.tex}.pdf)${NC}"
else
    echo -e "${RED}✗ Compilation failed${NC}"
    exit 1
fi
