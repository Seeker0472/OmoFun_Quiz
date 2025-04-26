{
  description = "Omo_workbench";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
    android = {
      url = "github:tadfisher/android-nixpkgs";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils ,android }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config = { allowUnfree = true; };
        };
          android-sdk = android.sdk.${system} (sdkPkgs: with sdkPkgs; [
            platform-tools
            cmdline-tools-latest
          ]);

      in {
        devShells.default = pkgs.mkShell {
          name = "android-project";
          motd = ''
            Entered the Android app development environment.
          '';
          env = {
            ANDROID_HOME = "${android-sdk}/share/android-sdk";
            ANDROID_SDK_ROOT = "${android-sdk}/share/android-sdk";
          };
          buildInputs = with pkgs; [
            man
            git
            vim
            python3
            appium-inspector
            nodejs_23
            sqlite
            android-sdk
          ];
        };
      });
}
