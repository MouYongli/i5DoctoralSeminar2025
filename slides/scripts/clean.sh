#!/bin/bash
# Clean LaTeX auxiliary files

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Cleaning LaTeX auxiliary files...${NC}"

# Clean build directory contents (keep directory and .gitkeep)
if [ -d "build" ]; then
    # Remove all files in build except .gitkeep
    find build -type f ! -name '.gitkeep' -delete
    # Remove all empty subdirectories in build
    find build -type d -empty -delete
    echo -e "${GREEN}✓ Cleaned build directory (kept .gitkeep)${NC}"
else
    echo -e "${YELLOW}No build directory found${NC}"
fi

# Remove common LaTeX auxiliary files in project root and subdirectories (excluding build)
find . -type f \( \
    -name "*.aux" -o \
    -name "*.log" -o \
    -name "*.out" -o \
    -name "*.toc" -o \
    -name "*.nav" -o \
    -name "*.snm" -o \
    -name "*.bbl" -o \
    -name "*.blg" -o \
    -name "*.bcf" -o \
    -name "*.run.xml" -o \
    -name "*.fls" -o \
    -name "*.fdb_latexmk" -o \
    -name "*.synctex.gz" \
\) ! -path "./build/*" -delete

echo -e "${GREEN}✓ Cleaned all auxiliary files${NC}"
