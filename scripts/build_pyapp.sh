VERSION=$(uvx hatch version)

uv build

PYAPP_DISTRIBUTION_EMBED=true \
PYAPP_PROJECT_PATH="$(pwd)/dist/easysnec-${VERSION}.tar.gz" \
PYAPP_UV_ENABLED=true \
PYAPP_PYTHON_VERSION="3.11" \
uvx hatch build -t binary