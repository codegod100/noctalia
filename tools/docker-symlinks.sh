#!/usr/bin/env bash
# Symlink build tools from the Nix devshell into /usr/local/bin
# so that buck2 remote actions find them on the default PATH.
set -euo pipefail

mkdir -p /usr/local/bin

tools=(
  g++ gcc ar ld ld.lld
  wayland-scanner pkg-config
  meson ninja python3
  clang-format git
)

for tool in "${tools[@]}"; do
  path=$(command -v "$tool" 2>/dev/null) || true
  if [ -n "${path:-}" ] && [ -x "$path" ]; then
    ln -sf "$path" "/usr/local/bin/$tool"
  fi
done

# g++ doubles as the C++ linker; create clang++/clang aliases
ln -sf "$(command -v g++)" /usr/local/bin/clang++ 2>/dev/null || true
ln -sf "$(command -v gcc)" /usr/local/bin/clang   2>/dev/null || true

# Verify essentials
echo "=== RBE image tools ==="
for t in g++ wayland-scanner pkg-config; do
  printf "  %-20s -> %s\n" "$t" "$(which "$t" 2>/dev/null || echo MISSING)"
done
