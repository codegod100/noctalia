#!/usr/bin/env python3
"""Generate the root BUCK file for the main noctalia executable."""

import re
import subprocess
import sys
from pathlib import Path

PKG_LIBS = [
    "sdbus-c++", "wayland-client", "wayland-egl", "freetype2", "fontconfig",
    "cairo", "pango", "pangocairo", "pangoft2", "harfbuzz", "librsvg-2.0",
    "xkbcommon", "glib-2.0", "gobject-2.0", "gio-2.0",
    "polkit-agent-1", "polkit-gobject-1", "libpipewire-0.3", "wireplumber-0.5",
    "libcurl", "libqalculate", "libxml-2.0", "md4c", "libwebp", "pam",
    "egl", "glesv2",
]


def extract_sources(meson_path: Path) -> list[str]:
    text = meson_path.read_text()
    m = re.search(r"_noctalia_sources\s*=\s*files\((.*?)\)", text, re.DOTALL)
    if not m:
        raise RuntimeError("Could not find _noctalia_sources in meson.build")
    return re.findall(r"'([^']+\.cpp)'", m.group(1))


def git_revision() -> str:
    try:
        return subprocess.check_output(
            ["git", "describe", "--tags", "--always", "--dirty=-dirty", "--abbrev=12"],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def pkg_libs() -> str:
    libs = set()
    for pc in PKG_LIBS:
        try:
            out = subprocess.check_output(
                ["pkg-config", "--libs-only-l", pc], text=True, stderr=subprocess.DEVNULL
            )
            for lib in out.strip().split():
                if lib.startswith("-l"):
                    libs.add(lib)
        except subprocess.CalledProcessError:
            pass
    return ",\n        ".join(f'"{l}"' for l in sorted(libs))


def define(name: str, value: str) -> str:
    return f'        "-D{name}=\\"{value}\\""'


def vendored_libs() -> str:
    return """
# Vendored libraries defined at the repo root so include_directories resolve to
# repo-relative paths. This is required for Remote Build Execution: when the
# library is defined inside a sub-package, buck2 resolves include_directories
# relative to the package for local builds but the remote worker receives an
# unusable path. Defining them at the root keeps the include path identical on
# both local and remote workers. raw_headers ensures all headers are uploaded as
# action inputs for RBE.

cxx_library(
    name = "dr_wav",
    srcs = ["third_party/dr_wav/dr_wav.c"],
    raw_headers = glob(["third_party/dr_wav/*.h"]),
    include_directories = ["third_party/dr_wav"],
    public_include_directories = ["third_party/dr_wav"],
    link_whole = True,
    visibility = ["PUBLIC"],
    within_view = ["PUBLIC"],
)

cxx_library(
    name = "fzy",
    srcs = ["third_party/fzy/src/match.c"],
    raw_headers = glob(["third_party/fzy/src/*.h", "third_party/fzy/*.h"]),
    include_directories = ["third_party/fzy/src"],
    public_include_directories = ["third_party/fzy/src"],
    compiler_flags = [
        "-Wno-pedantic",
        "-Wno-conversion",
    ],
    link_whole = True,
    visibility = ["PUBLIC"],
    within_view = ["PUBLIC"],
)

cxx_library(
    name = "material_color_utilities",
    srcs = [
        "third_party/material_color_utilities/cpp/blend/blend.cc",
        "third_party/material_color_utilities/cpp/cam/cam.cc",
        "third_party/material_color_utilities/cpp/cam/hct.cc",
        "third_party/material_color_utilities/cpp/cam/hct_solver.cc",
        "third_party/material_color_utilities/cpp/cam/viewing_conditions.cc",
        "third_party/material_color_utilities/cpp/contrast/contrast.cc",
        "third_party/material_color_utilities/cpp/dislike/dislike.cc",
        "third_party/material_color_utilities/cpp/dynamiccolor/dynamic_color.cc",
        "third_party/material_color_utilities/cpp/dynamiccolor/dynamic_scheme.cc",
        "third_party/material_color_utilities/cpp/dynamiccolor/material_dynamic_colors.cc",
        "third_party/material_color_utilities/cpp/palettes/tones.cc",
        "third_party/material_color_utilities/cpp/quantize/celebi.cc",
        "third_party/material_color_utilities/cpp/quantize/lab.cc",
        "third_party/material_color_utilities/cpp/quantize/wsmeans.cc",
        "third_party/material_color_utilities/cpp/quantize/wu.cc",
        "third_party/material_color_utilities/cpp/scheme/scheme_content.cc",
        "third_party/material_color_utilities/cpp/scheme/scheme_expressive.cc",
        "third_party/material_color_utilities/cpp/scheme/scheme_fidelity.cc",
        "third_party/material_color_utilities/cpp/scheme/scheme_fruit_salad.cc",
        "third_party/material_color_utilities/cpp/scheme/scheme_monochrome.cc",
        "third_party/material_color_utilities/cpp/scheme/scheme_neutral.cc",
        "third_party/material_color_utilities/cpp/scheme/scheme_rainbow.cc",
        "third_party/material_color_utilities/cpp/scheme/scheme_tonal_spot.cc",
        "third_party/material_color_utilities/cpp/scheme/scheme_vibrant.cc",
        "third_party/material_color_utilities/cpp/score/score.cc",
        "third_party/material_color_utilities/cpp/temperature/temperature_cache.cc",
        "third_party/material_color_utilities/cpp/utils/utils.cc",
    ],
    raw_headers = glob(["third_party/material_color_utilities/cpp/**/*.h"]),
    include_directories = ["third_party/material_color_utilities"],
    public_include_directories = ["third_party/material_color_utilities"],
    compiler_flags = [
        "-Wno-pedantic",
        "-Wno-conversion",
        "-Wno-shadow",
        "-Wno-unused-parameter",
    ],
    link_whole = True,
    visibility = ["PUBLIC"],
    within_view = ["PUBLIC"],
)

cxx_library(
    name = "luau",
    srcs = [
        "third_party/luau/Common/src/BytecodeWire.cpp",
        "third_party/luau/Common/src/StringUtils.cpp",
        "third_party/luau/Common/src/TimeTrace.cpp",
        "third_party/luau/Ast/src/Allocator.cpp",
        "third_party/luau/Ast/src/Ast.cpp",
        "third_party/luau/Ast/src/Confusables.cpp",
        "third_party/luau/Ast/src/Cst.cpp",
        "third_party/luau/Ast/src/Lexer.cpp",
        "third_party/luau/Ast/src/Location.cpp",
        "third_party/luau/Ast/src/Parser.cpp",
        "third_party/luau/Ast/src/PrettyPrinter.cpp",
        "third_party/luau/Bytecode/src/BytecodeBuilder.cpp",
        "third_party/luau/Bytecode/src/BytecodeGraph.cpp",
        "third_party/luau/Compiler/src/BuiltinFolding.cpp",
        "third_party/luau/Compiler/src/Builtins.cpp",
        "third_party/luau/Compiler/src/Compiler.cpp",
        "third_party/luau/Compiler/src/ConstantFolding.cpp",
        "third_party/luau/Compiler/src/CostModel.cpp",
        "third_party/luau/Compiler/src/lcode.cpp",
        "third_party/luau/Compiler/src/TableShape.cpp",
        "third_party/luau/Compiler/src/Types.cpp",
        "third_party/luau/Compiler/src/ValueTracking.cpp",
        "third_party/luau/VM/src/lapi.cpp",
        "third_party/luau/VM/src/laux.cpp",
        "third_party/luau/VM/src/lbaselib.cpp",
        "third_party/luau/VM/src/lbitlib.cpp",
        "third_party/luau/VM/src/lbuffer.cpp",
        "third_party/luau/VM/src/lbuflib.cpp",
        "third_party/luau/VM/src/lbuiltins.cpp",
        "third_party/luau/VM/src/lcorolib.cpp",
        "third_party/luau/VM/src/ldblib.cpp",
        "third_party/luau/VM/src/ldebug.cpp",
        "third_party/luau/VM/src/ldo.cpp",
        "third_party/luau/VM/src/lfunc.cpp",
        "third_party/luau/VM/src/lgc.cpp",
        "third_party/luau/VM/src/lgcdebug.cpp",
        "third_party/luau/VM/src/linit.cpp",
        "third_party/luau/VM/src/lintlib.cpp",
        "third_party/luau/VM/src/lclass.cpp",
        "third_party/luau/VM/src/lclasslib.cpp",
        "third_party/luau/VM/src/lmathlib.cpp",
        "third_party/luau/VM/src/lmem.cpp",
        "third_party/luau/VM/src/lnumprint.cpp",
        "third_party/luau/VM/src/lobject.cpp",
        "third_party/luau/VM/src/loslib.cpp",
        "third_party/luau/VM/src/lperf.cpp",
        "third_party/luau/VM/src/lstate.cpp",
        "third_party/luau/VM/src/lstring.cpp",
        "third_party/luau/VM/src/lstrlib.cpp",
        "third_party/luau/VM/src/ltable.cpp",
        "third_party/luau/VM/src/ltablib.cpp",
        "third_party/luau/VM/src/ltm.cpp",
        "third_party/luau/VM/src/ludata.cpp",
        "third_party/luau/VM/src/lutf8lib.cpp",
        "third_party/luau/VM/src/lveclib.cpp",
        "third_party/luau/VM/src/lvmexecute.cpp",
        "third_party/luau/VM/src/lvmload.cpp",
        "third_party/luau/VM/src/lvmutils.cpp",
    ],
    raw_headers = glob(["third_party/luau/**/*.h"]),
    include_directories = [
        "third_party/luau/Common/include",
        "third_party/luau/Ast/include",
        "third_party/luau/Bytecode/include",
        "third_party/luau/Compiler/include",
        "third_party/luau/VM/include",
        "third_party/luau/VM/src",
    ],
    public_include_directories = [
        "third_party/luau/Common/include",
        "third_party/luau/Ast/include",
        "third_party/luau/Bytecode/include",
        "third_party/luau/Compiler/include",
        "third_party/luau/VM/include",
        "third_party/luau/VM/src",
    ],
    compiler_flags = ["-w"],
    link_whole = True,
    visibility = ["PUBLIC"],
    within_view = ["PUBLIC"],
)
"""


def generate() -> str:
    sources = extract_sources(Path("meson.build"))
    revision = git_revision()
    linker_flags = pkg_libs()

    lines = [
        "# Generated by tools/generate_buck2_noctalia.py",
        "# Do not edit by hand; rerun the generator after source changes.",
        "",
        "export_file(",
        '    name = "git_revision_h_in",',
        '    src = "src/core/git_revision.h.in",',
        '    visibility = ["PUBLIC"],',
        ")",
        "",
        "genrule(",
        '    name = "git_revision_header",',
        '    srcs = [":git_revision_h_in"],',
        '    out = "noctalia_git_revision.h",',
        f'    cmd = "sed -e \\"s/@VCS_TAG@/{revision}/g\\" $(location :git_revision_h_in) > $OUT",',
        ")",
        vendored_libs(),
        "",
        "cxx_binary(",
        '    name = "noctalia",',
        "    srcs = [",
    ]
    for s in sources:
        lines.append(f'        "{s}",')
    lines += [
        "    ],",
        '    headers = [":git_revision_header"],',
        '    raw_headers = glob(["src/**/*.h", "third_party/wuffs/**/*"]),',
        "    include_directories = [",
        '        "src",',
        '        "third_party/wuffs",',
        '        ".",',
        "    ],",
        "    compiler_flags = [",
        '        "-Ithird_party/wuffs",',
        '        "-Isrc",',
        '        "-I.",',
        define("NOCTALIA_SOURCE_ASSETS_DIR", "assets") + ",",
        define("NOCTALIA_INSTALL_PREFIX", "/usr/local") + ",",
        define("NOCTALIA_INSTALL_DATADIR", "share") + ",",
        define("NOCTALIA_VERSION", "5.0.0") + ",",
        "    ],",
        "    linker_flags = [",
        f"        {linker_flags},",
        "    ],",
        "    deps = [",
        '        ":dr_wav",',
        '        ":fzy",',
        '        ":luau",',
        '        ":material_color_utilities",',
        '        "//third_party/system:sdbus_cpp",',
        '        "//third_party/system:wayland_client",',
        '        "//third_party/system:wayland_egl",',
        '        "//third_party/system:freetype2",',
        '        "//third_party/system:fontconfig",',
        '        "//third_party/system:cairo",',
        '        "//third_party/system:cairo_ft",',
        '        "//third_party/system:pango",',
        '        "//third_party/system:pangocairo",',
        '        "//third_party/system:pangoft2",',
        '        "//third_party/system:harfbuzz",',
        '        "//third_party/system:librsvg",',
        '        "//third_party/system:xkbcommon",',
        '        "//third_party/system:glib",',
        '        "//third_party/system:gobject",',
        '        "//third_party/system:gio",',
        '        "//third_party/system:polkit_agent",',
        '        "//third_party/system:polkit_gobject",',
        '        "//third_party/system:pipewire",',
        '        "//third_party/system:wireplumber",',
        '        "//third_party/system:curl",',
        '        "//third_party/system:libqalculate",',
        '        "//third_party/system:libxml2",',
        '        "//third_party/system:md4c",',
        '        "//third_party/system:nlohmann_json",',
        '        "//third_party/system:tomlplusplus",',
        '        "//third_party/system:libwebp",',
        '        "//third_party/system:egl",',
        '        "//third_party/system:gles2",',
        '        "//third_party/system:pam",',
        '        "//protocols:xdg-output-unstable-v1",',
        '        "//protocols:xdg-shell",',
        '        "//protocols:ext-workspace-v1",',
        '        "//protocols:ext-foreign-toplevel-list-v1",',
        '        "//protocols:ext-data-control-v1",',
        '        "//protocols:xdg-activation-v1",',
        '        "//protocols:ext-session-lock-v1",',
        '        "//protocols:ext-idle-notify-v1",',
        '        "//protocols:ext-background-effect-v1",',
        '        "//protocols:fractional-scale-v1",',
        '        "//protocols:viewporter",',
        '        "//protocols:idle-inhibit-unstable-v1",',
        '        "//protocols:text-input-unstable-v3",',
        '        "//protocols:virtual-keyboard-unstable-v1",',
        '        "//protocols:dwl-ipc-unstable-v2",',
        '        "//protocols:org-kde-plasma-virtual-desktop",',
        '        "//protocols:cursor-shape-v1",',
        '        "//protocols:wlr-foreign-toplevel-management-unstable-v1",',
        '        "//protocols:wlr-data-control-unstable-v1",',
        '        "//protocols:hyprland-focus-grab-v1",',
        '        "//protocols:hyprland-toplevel-mapping-v1",',
        '        "//protocols:wlr-gamma-control-unstable-v1",',
        '        "//protocols:wlr-screencopy-unstable-v1",',
        '        "//protocols:wlr-layer-shell-unstable-v1",',
        "    ],",
        '    visibility = ["PUBLIC"],',
        ")",
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    out = Path("BUCK")
    out.write_text(generate())
    print(f"Generated {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
