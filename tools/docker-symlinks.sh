#!/usr/bin/env bash
# Symlink build tools from the Nix devshell into /usr/local/bin
# so that buck2 remote actions find them on the default PATH.
set -euo pipefail

mkdir -p /usr/local/bin

# Capture the Nix devshell compiler/linker flags so that remote actions
# invoked outside of `nix develop` still see the correct include/library paths.
# The gcc wrapper expects the suffixed variables and they must be exported so
# the real Nix wrapper process inherits them.
cat > /etc/noctalia-rbe-env.sh <<EOF
export NIX_CC_WRAPPER_TARGET_HOST_x86_64_unknown_linux_gnu=1
export NIX_BINTOOLS_WRAPPER_TARGET_HOST_x86_64_unknown_linux_gnu=1
export NIX_CFLAGS_COMPILE_x86_64_unknown_linux_gnu='${NIX_CFLAGS_COMPILE:-}'
export NIX_CFLAGS_LINK_x86_64_unknown_linux_gnu='${NIX_CFLAGS_LINK:-}'
export NIX_LDFLAGS_x86_64_unknown_linux_gnu='${NIX_LDFLAGS:-}'
export NIX_LDFLAGS_BEFORE_x86_64_unknown_linux_gnu='${NIX_LDFLAGS_BEFORE:-}'
EOF

tools=(
  ar ld ld.lld
  wayland-scanner pkg-config
  meson ninja python3
  clang-format git
  sed awk grep coreutils
)

for tool in "${tools[@]}"; do
  path=$(command -v "$tool" 2>/dev/null) || true
  if [ -n "${path:-}" ] && [ -x "$path" ]; then
    ln -sf "$path" "/usr/local/bin/$tool"
  fi
done

# gcc/g++ wrappers: ensure NIX_CFLAGS_COMPILE / NIX_LDFLAGS are set so that
# system headers/libraries from the devshell are discovered by bare RBE actions.
wrap_compiler() {
  local name=$1
  # Resolve the real binary before we overwrite /usr/local/bin/{gcc,g++}.
  local real
  real=$(readlink -f "$(command -v "$name" 2>/dev/null)") || return 0
  [ -x "$real" ] || return 0
  cat > "/usr/local/bin/$name" <<EOF
#!/usr/bin/env bash
set -e
source /etc/noctalia-rbe-env.sh
exec "$real" "\$@"
EOF
  chmod +x "/usr/local/bin/$name"
}

wrap_compiler gcc
wrap_compiler g++

# clang/clang++ aliases for rules that probe for them
ln -sf "$(command -v g++)" /usr/local/bin/clang++ 2>/dev/null || true
ln -sf "$(command -v gcc)" /usr/local/bin/clang   2>/dev/null || true

# Verify essentials
echo "=== RBE image tools ==="
for t in g++ wayland-scanner pkg-config sed; do
  printf "  %-20s -> %s\n" "$t" "$(which "$t" 2>/dev/null || echo MISSING)"
done
