if (Get-Command uv -errorAction SilentlyContinue) {
    uv run easysnec
} else {
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    uv run easysnec
}