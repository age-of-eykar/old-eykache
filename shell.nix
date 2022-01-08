with import <nixpkgs> { };

let
  eykache = python38.withPackages (python-packages:
    with python-packages; [
      cython
      aiohttp
      toml
    ]);
in stdenv.mkDerivation {
  name = "eykache-dev-environment";
  buildInputs = [ eykache ];
}