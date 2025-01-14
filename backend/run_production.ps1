# Activate virtual environment if you're using one
# Uncomment these lines if you're using a virtual environment
# $env:VIRTUAL_ENV = "path\to\your\venv"
# $env:PATH = "$env:VIRTUAL_ENV\Scripts;$env:PATH"

# Set environment variables
$env:ENVIRONMENT = "production"

# Start the server
Write-Host "Starting production server..."
python production.py 