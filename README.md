# Python XCTSK Viewer

A Python-based interactive visualization tool for viewing XCTSK files.

This tool allows paragliding pilots, organizers, and enthusiasts to visualize XCTSK files—used to define competition tasks for XCTrack. Built with Python, the viewer provides an interactive map interface to inspect turnpoints, task types, and routes defined in XCTSK files, making it easier to review or debug tasks for competitions.

## Quick Start

### Installation and Setup

```bash
# Clone and navigate to the project directory
cd xctsk-viewer

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
# Install the package in development mode
pip install -e .
# lock dependency versions for deployment
pip freeze > requirements.txt
```

### Running the Application

```bash
python run.py
```

## Deployment

### Fly.io

This application can be deployed to [Fly.io](https://fly.io/) for production hosting.

#### Setup Requirements

Install the Fly.io CLI:

```bash
curl -L https://fly.io/install.sh | sh
# Add Fly.io to your PATH (add to `.bashrc` or `.zshrc`):
export FLYCTL_INSTALL="/home/$USER$/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"
```

#### Deployment Setup

The project includes a `fly.toml` configuration file for Fly.io deployment. To deploy:

```bash
# Login to Fly.io
fly auth login
# Launch the application (--ha=false ensures single machine deployment)
fly launch --ha=false
# If you already have two machines deployed, scale down to one
fly scale count 1
# Set Flask secret key for security
python3 -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))"
# Copy the output and set it as a secret (replace with actual generated key)
fly secrets set FLASK_SECRET_KEY=your_generated_key_here
# Deploy updates
fly deploy

# For automated deployments via GitHub Actions, create a deploy token:
fly tokens create deploy -x 999999h
```

#### Local Docker Testing

Before deploying to Fly.io, you can test the Docker image locally:

```bash
# Build the Docker image
docker build -t my-fly-app .

# Run the container locally on port 8080
docker run -p 8080:8080 my-fly-app
```

The application will be available at <http://localhost:8080>.
