let
  mach-nix = import (builtins.fetchGit {
    url = "https://github.com/DavHau/mach-nix";
    rev = "bdc97ba6b2ecd045a467b008cff4ae337b6a7a6b";
  }) {
    pkgs = import <nixpkgs> { };
    python = "python39";
    pypiDataRev = "aa41bbda98d5f4333f24fd7090cc8efd3aa5825c";
    pypiDataSha256 = "1iv08mhqdp5vq5g1fkig5wy3mvcxbd9ka6xsblsbjs4wdcbwflip";
  };

  pyEnv = mach-nix.mkPython rec {
    requirements = ''
      cython
      aiohttp
      aiohttp_cors
      psycopg2
      toml
      tqdm
      websockets>=9.1,<10
    ''; # todo: support ipfshttpclient==0.8.0a2
    packagesExtra = [ ./web3.py ];

    providers = { _default = "nixpkgs,sdist,wheel"; };
    ignoreCollisions = true;
  };
in mach-nix.nixpkgs.mkShell { buildInputs = [ pyEnv ]; }
