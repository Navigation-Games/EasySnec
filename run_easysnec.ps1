$env:PATH += "$env:USERPROFILE\.local\bin"

if (Get-Command uv -errorAction SilentlyContinue) {
    echo "uv already installed"    
} else {
    echo "uv not installed. fetching now..."
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
}

uv run --offline --frozen --no-sync --no-dev --no-build easysnec
