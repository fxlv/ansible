{ pkgs ? import <nixpkgs> {} }:

with pkgs;

mkShell {
  buildInputs = [
  python3Full
  gnupg
  git-crypt
  ];
}