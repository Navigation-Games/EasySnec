$env:PATH += "$env:USERPROFILE\.local\bin"

if (Get-Command uv -errorAction SilentlyContinue) {
    echo "uv already installed"
} else {
    echo "uv not installed. fetching now..."
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
}

uv sync --no-dev --check --offline
if ($?) {
    echo "project already initalized"
} else {
    echo "project uninitialized!"
    uv sync --exact --no-dev
}
uv run --offline --frozen --no-sync --no-dev --no-build easysnec
# uv run --offline --frozen --no-sync --no-dev --no-build easysnec
