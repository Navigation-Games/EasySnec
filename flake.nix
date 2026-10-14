{
  # Which package repository will we point to?
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-26.05-small";
  };

  outputs = { self, nixpkgs, ... }@inputs:
    # Handy iterator so we only have to do this once
    let
      forAllSystems = nixpkgs.lib.genAttrs [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

    in {
      devShell = forAllSystems (
        system: let
            pkgs = nixpkgs.legacyPackages.${system};
        in pkgs.mkShell rec {
            name = "Alva Data Processing";

            packages = with pkgs; [
              python314
              uv
            ];

            shellHook = ''
              # Auto-source the venv
              source .venv/bin/activate
            '';

            # Add these libraries to the linker, for numpy to use
            nativeBuildInputs = with pkgs; [
              stdenv.cc.cc.lib
              libGL # posibly superseded by hardware.enable

              # slint deps
              libx11
              udev
              libinput
              libgbm
              freetype
              # glib
              # glibc
              krb5
              libxkbcommon
              dbus
              wayland
              expat
              fontconfig

              # pkg-config

              alsa-lib
              ffmpeg_7
            ];

            LD_LIBRARY_PATH = "/run/opengl-driver/lib/:${pkgs.lib.makeLibraryPath nativeBuildInputs}";
            UV_NO_MANAGED_PYTHON=true;
        }
      );
    };
}