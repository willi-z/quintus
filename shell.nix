{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  nativeBuildInputs = with pkgs; [cmake pkg-config freetype expat fontconfig lldb];
  buildInputs = with pkgs; [ rustup sqlite gcc];
}
