#!/bin/bash
# LaTeX Environment Setup Script for Beamer Presentations
# Author: Yongli Mou (RWTH DBIS)
# Description: Install and configure LaTeX compilation environment

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  LaTeX Environment Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    else
        echo -e "${RED}Cannot detect OS. Please install manually.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Detected OS: $OS $VER${NC}"
}

# Install LaTeX on Ubuntu/Debian
install_ubuntu() {
    echo -e "${YELLOW}Installing LaTeX packages for Ubuntu/Debian...${NC}"
    sudo apt-get update
    sudo apt-get install -y \
        texlive-latex-base \
        texlive-latex-extra \
        texlive-fonts-recommended \
        texlive-fonts-extra \
        texlive-bibtex-extra \
        texlive-xetex \
        texlive-luatex \
        biber \
        latexmk \
        cm-super \
        dvipng
    echo -e "${GREEN}✓ LaTeX packages installed${NC}"
}

# Install LaTeX on Fedora/RHEL/CentOS
install_fedora() {
    echo -e "${YELLOW}Installing LaTeX packages for Fedora/RHEL...${NC}"
    sudo dnf install -y \
        texlive \
        texlive-latex \
        texlive-xetex \
        texlive-collection-fontsrecommended \
        texlive-collection-latexextra \
        latexmk \
        biber
    echo -e "${GREEN}✓ LaTeX packages installed${NC}"
}

# Install LaTeX on Arch Linux
install_arch() {
    echo -e "${YELLOW}Installing LaTeX packages for Arch Linux...${NC}"
    sudo pacman -S --noconfirm \
        texlive-core \
        texlive-latexextra \
        texlive-fontsextra \
        texlive-bibtexextra \
        biber
    echo -e "${GREEN}✓ LaTeX packages installed${NC}"
}

# Check if LaTeX is already installed
check_latex() {
    echo -e "${YELLOW}Checking for existing LaTeX installation...${NC}"
    if command -v pdflatex &> /dev/null && command -v xelatex &> /dev/null; then
        echo -e "${GREEN}✓ LaTeX is already installed${NC}"
        pdflatex --version | head -n 1
        return 0
    else
        echo -e "${YELLOW}LaTeX not found, proceeding with installation...${NC}"
        return 1
    fi
}

# Install based on OS
install_latex() {
    case $OS in
        ubuntu|debian|linuxmint|pop)
            install_ubuntu
            ;;
        fedora|rhel|centos|rocky|almalinux)
            install_fedora
            ;;
        arch|manjaro)
            install_arch
            ;;
        *)
            echo -e "${RED}Unsupported OS: $OS${NC}"
            echo -e "${YELLOW}Please install LaTeX manually:${NC}"
            echo "  - TeX Live: https://www.tug.org/texlive/"
            echo "  - MiKTeX: https://miktex.org/"
            exit 1
            ;;
    esac
}

# Verify installation
verify_installation() {
    echo ""
    echo -e "${YELLOW}Verifying installation...${NC}"

    local all_installed=true

    # Check required commands
    commands=("pdflatex" "xelatex" "lualatex" "biber" "latexmk")
    for cmd in "${commands[@]}"; do
        if command -v $cmd &> /dev/null; then
            echo -e "${GREEN}✓ $cmd installed${NC}"
        else
            echo -e "${RED}✗ $cmd not found${NC}"
            all_installed=false
        fi
    done

    if [ "$all_installed" = true ]; then
        echo -e "${GREEN}✓ All required tools installed successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ Some tools are missing${NC}"
        return 1
    fi
}

# Create compile script
create_compile_script() {
    echo -e "${YELLOW}Creating compilation script...${NC}"

    cat > "$(dirname "$0")/compile.sh" << 'EOF'
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
EOF

    chmod +x "$(dirname "$0")/compile.sh"
    echo -e "${GREEN}✓ Compilation script created at $(dirname "$0")/compile.sh${NC}"
}

# Create clean script
create_clean_script() {
    echo -e "${YELLOW}Creating clean script...${NC}"

    cat > "$(dirname "$0")/clean.sh" << 'EOF'
#!/bin/bash
# Clean LaTeX auxiliary files

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Cleaning LaTeX auxiliary files...${NC}"

# Remove build directory
if [ -d "build" ]; then
    rm -rf build
    echo -e "${GREEN}✓ Removed build directory${NC}"
fi

# Remove common LaTeX auxiliary files
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
\) -delete

echo -e "${GREEN}✓ Cleaned auxiliary files${NC}"
EOF

    chmod +x "$(dirname "$0")/clean.sh"
    echo -e "${GREEN}✓ Clean script created at $(dirname "$0")/clean.sh${NC}"
}

# Main installation flow
main() {
    detect_os

    echo ""
    if ! check_latex; then
        echo -e "${YELLOW}Proceed with installation? (y/n)${NC}"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            install_latex
        else
            echo -e "${YELLOW}Installation cancelled${NC}"
            exit 0
        fi
    fi

    verify_installation

    echo ""
    create_compile_script
    create_clean_script

    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}Setup completed successfully!${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  Compile presentation: ./scripts/compile.sh [file.tex]"
    echo "  Clean aux files:      ./scripts/clean.sh"
    echo ""
    echo -e "${YELLOW}To compile with other engines:${NC}"
    echo "  XeLaTeX:  xelatex main.tex"
    echo "  LuaLaTeX: lualatex main.tex"
    echo ""
}

# Run main function
main
