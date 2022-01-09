let
  mach-nix = import (builtins.fetchGit {
    url = "https://github.com/DavHau/mach-nix";
    rev = "bdc97ba6b2ecd045a467b008cff4ae337b6a7a6b";
  }) {
    pkgs = import <nixpkgs> { };
    python = "python38";
    pypiDataRev = "aa41bbda98d5f4333f24fd7090cc8efd3aa5825c";
    pypiDataSha256 = "1iv08mhqdp5vq5g1fkig5wy3mvcxbd9ka6xsblsbjs4wdcbwflip";
  };

  pyEnv = mach-nix.mkPython rec {
    requirements = ''
      cython
      aiohttp
      toml
    '';

    providers = { _default = "nixpkgs,wheel,sdist"; };
    ignoreCollisions = true;
  };
in mach-nix.nixpkgs.mkShell { buildInputs = [ pyEnv ]; }
