#!/bin/bash

# =============================================================================
# SALESFORCE ANALYTICS EMBEDDING TEMPLATE - QUICK SETUP SCRIPT
# =============================================================================
#
# This script automates the initial setup of the Salesforce Analytics
# Embedding Template with industry-specific configurations and Veeva CRM
# integration support.
#
# Usage: ./scripts/setup.sh [industry]
#
# Industries: pharma, healthcare, generic
#
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
INDUSTRY="${1:-pharma}"
NODE_MIN_VERSION="18"
PYTHON_MIN_VERSION="3.11"

# Helper functions
print_header() {
    echo ""
    echo -e "${BLUE}=============================================================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}=============================================================================${NC}"
    echo ""
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Version comparison function
version_compare() {
    if [[ $1 == $2 ]]; then
        return 0
    fi
    local IFS=.
    local i ver1=($1) ver2=($2)
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++)); do
        ver1[i]=0
    done
    for ((i=0; i<${#ver1[@]}; i++)); do
        if [[ -z ${ver2[i]} ]]; then
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]})); then
            return 1
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]})); then
            return 2
        fi
    done
    return 0
}

# Main setup function
main() {
    print_header "SALESFORCE ANALYTICS EMBEDDING TEMPLATE SETUP"

    print_info "Industry Template: ${INDUSTRY}"
    echo ""

    # Step 1: Verify system requirements
    print_step "Checking system requirements"
    check_system_requirements

    # Step 2: Install dependencies
    print_step "Installing dependencies"
    install_dependencies

    # Step 3: Setup environment configuration
    print_step "Setting up environment configuration"
    setup_environment

    # Step 4: Configure industry template
    print_step "Configuring industry template"
    configure_industry_template

    # Step 5: Initialize project structure
    print_step "Initializing project structure"
    initialize_project_structure

    # Step 6: Validate installation
    print_step "Validating installation"
    validate_installation

    # Final instructions
    print_completion_instructions
}

check_system_requirements() {
    local requirements_met=true

    # Check Node.js
    if command_exists node; then
        local node_version=$(node -v | sed 's/v//')
        local node_major=$(echo $node_version | cut -d. -f1)

        if [[ $node_major -ge $NODE_MIN_VERSION ]]; then
            print_info "✅ Node.js $node_version (required: $NODE_MIN_VERSION+)"
        else
            print_error "❌ Node.js $node_version is too old (required: $NODE_MIN_VERSION+)"
            requirements_met=false
        fi
    else
        print_error "❌ Node.js not found (required: $NODE_MIN_VERSION+)"
        print_info "Install from: https://nodejs.org/"
        requirements_met=false
    fi

    # Check Python
    local python_cmd="python3"
    if command_exists python3; then
        python_cmd="python3"
    elif command_exists python; then
        python_cmd="python"
    else
        print_error "❌ Python not found (required: $PYTHON_MIN_VERSION+)"
        requirements_met=false
    fi

    if command_exists $python_cmd; then
        local python_version=$($python_cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        version_compare $python_version $PYTHON_MIN_VERSION
        local result=$?

        if [[ $result -eq 1 ]] || [[ $result -eq 0 ]]; then
            print_info "✅ Python $python_version (required: $PYTHON_MIN_VERSION+)"
        else
            print_error "❌ Python $python_version is too old (required: $PYTHON_MIN_VERSION+)"
            requirements_met=false
        fi
    fi

    # Check pip
    if command_exists pip || command_exists pip3; then
        print_info "✅ pip package manager"
    else
        print_error "❌ pip not found"
        requirements_met=false
    fi

    # Check git
    if command_exists git; then
        print_info "✅ Git version control"
    else
        print_warning "⚠️ Git not found (optional but recommended)"
    fi

    if [[ $requirements_met == false ]]; then
        print_error "System requirements not met. Please install missing dependencies."
        exit 1
    fi
}

install_dependencies() {
    print_info "Installing Node.js dependencies..."

    if [[ -f "package.json" ]]; then
        npm install
        print_success "Node.js dependencies installed"
    else
        print_error "package.json not found"
        exit 1
    fi

    print_info "Installing Python dependencies..."

    # Try to use virtual environment if available
    if command_exists python3; then
        python_cmd="python3"
        pip_cmd="pip3"
    else
        python_cmd="python"
        pip_cmd="pip"
    fi

    # Check if we're in a virtual environment
    if [[ -z "$VIRTUAL_ENV" ]]; then
        print_warning "Not in a virtual environment. Consider creating one:"
        print_info "  python3 -m venv venv"
        print_info "  source venv/bin/activate  # Linux/Mac"
        print_info "  venv\\Scripts\\activate     # Windows"
        echo ""
    fi

    if [[ -f "requirements.txt" ]]; then
        $pip_cmd install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

setup_environment() {
    if [[ -f ".env" ]]; then
        print_warning "Environment file (.env) already exists"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Keeping existing .env file"
            return
        fi
    fi

    if [[ -f ".env.example" ]]; then
        cp .env.example .env
        print_success "Environment template copied to .env"

        # Configure industry-specific defaults
        case $INDUSTRY in
            "pharma")
                sed -i.bak 's/INDUSTRY_TEMPLATE=.*/INDUSTRY_TEMPLATE=pharma/' .env
                sed -i.bak 's/VEEVA_INTEGRATION_ENABLED=.*/VEEVA_INTEGRATION_ENABLED=true/' .env
                sed -i.bak 's/PHARMA_COMPLIANCE_MODE=.*/PHARMA_COMPLIANCE_MODE=true/' .env
                print_info "Configured for pharmaceutical industry"
                ;;
            "healthcare")
                sed -i.bak 's/INDUSTRY_TEMPLATE=.*/INDUSTRY_TEMPLATE=healthcare/' .env
                sed -i.bak 's/HEALTHCARE_HIPAA_COMPLIANCE=.*/HEALTHCARE_HIPAA_COMPLIANCE=true/' .env
                print_info "Configured for healthcare industry"
                ;;
            "generic")
                sed -i.bak 's/INDUSTRY_TEMPLATE=.*/INDUSTRY_TEMPLATE=generic/' .env
                print_info "Configured for generic business use"
                ;;
        esac

        # Remove backup file
        rm -f .env.bak

        print_warning "IMPORTANT: You must edit .env with your Salesforce credentials"
        print_info "Required settings:"
        print_info "  - SALESFORCE_ORG_URL"
        print_info "  - SALESFORCE_CLIENT_ID"
        print_info "  - SALESFORCE_CLIENT_SECRET"
        print_info "  - TABLEAU_DASHBOARD_ID"
        print_info "  - AGENTFORCE_AGENT_ID"

    else
        print_error ".env.example not found"
        exit 1
    fi
}

configure_industry_template() {
    local template_file="config/industry-templates/${INDUSTRY}.json"

    if [[ -f "$template_file" ]]; then
        print_success "Industry template found: $template_file"

        # Validate template structure
        if command_exists python3; then
            python3 -c "
import json
import sys
try:
    with open('$template_file', 'r') as f:
        config = json.load(f)
    required_keys = ['template', 'dashboard', 'agentforce', 'dataModel']
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        print('Missing required keys:', missing_keys)
        sys.exit(1)
    print('Template validation passed')
except Exception as e:
    print('Template validation failed:', e)
    sys.exit(1)
"
            if [[ $? -eq 0 ]]; then
                print_success "Industry template validated"
            else
                print_error "Industry template validation failed"
                exit 1
            fi
        else
            print_info "Skipping template validation (Python not available)"
        fi
    else
        print_error "Industry template not found: $template_file"
        print_info "Available templates:"
        ls -1 config/industry-templates/*.json 2>/dev/null | sed 's/.*\///; s/.json//' | sed 's/^/  - /' || echo "  No templates found"
        exit 1
    fi
}

initialize_project_structure() {
    # Create necessary directories
    local dirs=(
        "static/js/industry-adapters"
        "static/css/industry-themes"
        "static/assets"
        "templates/layouts"
        "logs"
    )

    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            print_info "Created directory: $dir"
        fi
    done

    # Copy SDK files
    if [[ -f "node_modules/@salesforce/analytics-embedding-sdk/dist/sdk-bundle.js" ]]; then
        cp "node_modules/@salesforce/analytics-embedding-sdk/dist/sdk-bundle.js" "static/js/analytics-sdk.js"
        print_success "Copied Analytics SDK to static files"
    else
        print_warning "Analytics SDK not found in node_modules"
    fi
}

validate_installation() {
    print_info "Running validation checks..."

    # Check if .env file has required settings
    if [[ -f ".env" ]]; then
        local missing_vars=()

        # Check for required environment variables
        required_vars=(
            "SALESFORCE_ORG_URL"
            "SALESFORCE_CLIENT_ID"
            "TABLEAU_DASHBOARD_ID"
            "APP_URL"
            "SECRET_KEY"
        )

        for var in "${required_vars[@]}"; do
            if ! grep -q "^${var}=" .env || grep -q "^${var}=your_" .env; then
                missing_vars+=($var)
            fi
        done

        if [[ ${#missing_vars[@]} -eq 0 ]]; then
            print_success "Environment configuration appears complete"
        else
            print_warning "The following environment variables need to be configured:"
            for var in "${missing_vars[@]}"; do
                print_info "  - $var"
            done
        fi
    else
        print_error ".env file not found"
    fi

    # Test Python imports
    if command_exists python3; then
        python3 -c "
import flask, requests, dotenv
print('✅ Python dependencies available')
" 2>/dev/null || print_warning "Some Python dependencies may be missing"
    fi

    # Test Node.js imports
    if command_exists node; then
        node -e "
try {
    require('@salesforce/analytics-embedding-sdk');
    console.log('✅ Analytics SDK available');
} catch(e) {
    console.log('⚠️ Analytics SDK not available:', e.message);
}
" 2>/dev/null || print_warning "Analytics SDK may not be properly installed"
    fi

    print_success "Validation completed"
}

print_completion_instructions() {
    print_header "SETUP COMPLETED SUCCESSFULLY"

    echo -e "${GREEN}🎉 Your Salesforce Analytics Template is ready!${NC}"
    echo ""

    print_info "Next Steps:"
    echo ""
    echo -e "${YELLOW}1. Configure your Salesforce credentials:${NC}"
    echo "   Edit .env file with your:"
    echo "   - Salesforce org URL"
    echo "   - Connected App credentials"
    echo "   - Dashboard and Agent IDs"
    echo ""

    echo -e "${YELLOW}2. Test your setup:${NC}"
    echo "   python app.py"
    echo "   # Then visit http://localhost:5000"
    echo ""

    if [[ $INDUSTRY == "pharma" ]]; then
        echo -e "${BLUE}3. For Veeva CRM integration:${NC}"
        echo "   See docs/VEEVA-INTEGRATION.md"
        echo "   Configure Veeva-specific settings in .env"
        echo ""
    fi

    echo -e "${YELLOW}4. Customize for your industry:${NC}"
    echo "   - Edit config/industry-templates/${INDUSTRY}.json"
    echo "   - Customize static/css/industry-themes/"
    echo "   - Add your branding and styling"
    echo ""

    echo -e "${YELLOW}5. Deploy to your preferred platform:${NC}"
    echo "   The application supports any hosting platform"
    echo "   that supports Python/Flask and Node.js"
    echo ""

    echo -e "${CYAN}📚 Documentation:${NC}"
    echo "   - README.md - Overview and quick start"
    echo "   - docs/CONFIGURATION.md - Detailed configuration"
    if [[ $INDUSTRY == "pharma" ]]; then
        echo "   - docs/VEEVA-INTEGRATION.md - Veeva CRM integration"
    fi
    echo "   - docs/TROUBLESHOOTING.md - Common issues and solutions"
    echo ""

    print_success "Happy building! 🚀"
}

# Error handling
trap 'print_error "Setup failed on line $LINENO. Exit code: $?"' ERR

# Check if we're in the right directory
if [[ ! -f "package.json" ]] || [[ ! -f "requirements.txt" ]]; then
    print_error "This script must be run from the project root directory"
    print_info "Current directory: $(pwd)"
    print_info "Expected files: package.json, requirements.txt"
    exit 1
fi

# Run main function
main "$@"