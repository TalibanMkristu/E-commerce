#!/bin/bash

# Colors for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Django project setup...${NC}"

# Step 1: Detect python3
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo -e "${RED}Python is not installed. Exiting.${NC}"
    exit 1
fi

# Step 2: Create virtual environment
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    $PYTHON -m venv venv
else
    echo -e "${YELLOW}Virtual environment already exists. Skipping creation.${NC}"
fi

# Step 3: Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Step 4: Upgrade pip, setuptools, and wheel
echo -e "${GREEN}Upgrading pip, setuptools, and wheel...${NC}"
pip install --upgrade pip setuptools wheel

# Step 5: Install dependencies
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}Installing Python dependencies from requirements.txt...${NC}"
    pip install -r requirements.txt
else
    echo -e "${YELLOW}No requirements.txt found. Skipping package install.${NC}"
fi

# Step 6 (optional): Load .env if exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}Loading environment variables from .env...${NC}"
    export $(grep -v '^#' .env | xargs)
fi

# Step 7: Check if Django project is present and run migrations
if [ -f "manage.py" ]; then
    echo -e "${GREEN}Django project detected. Running migrations...${NC}"
    $PYTHON manage.py migrate
else
    echo -e "${YELLOW}manage.py not found. Skipping Django migration step.${NC}"
fi

echo -e "${GREEN}✅ Setup complete. Activate the virtual environment with:${NC}"
echo -e "${YELLOW}source venv/bin/activate${NC}"
