
$version=$(uvx hatch version)

uv build

pwsh -Command {
    $env:PYAPP_DISTRIBUTION_EMBED="true";
    $env:PYAPP_PROJECT_PATH="$(pwd)/dist/easysnec-$version.tar.gz";
    $env:PYAPP_UV_ENABLED="true";
    $env:PYAPP_PYTHON_VERSION="3.11";
    uvx hatch build -t binary
    # $env:MYVAR="myvalue";
    # .\path\to.exe
}

# you need to install innosetup and find its installation location
C:\Users\qbowers\AppData\Local\Programs\"Inno Setup 6"\ISCC.exe /DVersionNo=$version /O$(pwd)/dist/installers build/windows_installer.iss