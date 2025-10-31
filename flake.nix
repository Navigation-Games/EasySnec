{
  # Which package repository will we point to?
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-25.05";
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

            # Use this version of the python package for GUI support (the alternative is Qt Hell)
            packages = with pkgs; [
              python314Full
              python314Packages.tkinter
            ];

            # Auto-source the venv (nice!)
            shellHook = ''
              source .venv/bin/activate
            '';

            # Add these libraries to the linker, for numpy to use
            nativeBuildInputs = [
              pkgs.pkg-config
              pkgs.hdf5
              pkgs.stdenv.cc.cc.lib
              pkgs.zlib
            ];

            LD_LIBRARY_PATH = "$LD_LIBRARY_PATH:${pkgs.lib.makeLibraryPath nativeBuildInputs}";
        }
      );
    };
}