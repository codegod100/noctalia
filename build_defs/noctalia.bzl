"""Noctalia-specific buck2 helpers."""

def system_cxx_library(name, pkg_config, exported_preprocessor_flags = [], exported_linker_flags = [], visibility = ["PUBLIC"]):
    """Wrap a system library discovered via pkg-config.

    Uses cxx_library (not prebuilt_cxx_library) so that exported_linker_flags
    are propagated to the final link. No source files are compiled.
    """
    native.cxx_library(
        name = name,
        exported_preprocessor_flags = exported_preprocessor_flags,
        exported_linker_flags = exported_linker_flags,
        visibility = visibility,
        within_view = visibility,
    )

def wayland_protocol_library(name, xml, visibility = ["PUBLIC"]):
    """Generate and compile a Wayland protocol binding pair.

    Produces <name>-client-protocol.h and <name>-client-protocol.c from the
    given XML using wayland-scanner, then compiles the C source into a
    small static library. Dependents should add this target to `deps` and
    include the generated header directly (e.g. #include "xdg-shell.h").
    """
    header_out = name + "-client-protocol.h"
    source_out = name + "-client-protocol.c"
    # System XMLs are absolute paths; local ones are export_file target labels.
    is_target = xml.startswith(":")
    is_absolute = xml.startswith("/")
    if is_target:
        src_ref = "$(location " + xml + ")"
        srcs = [xml]
    elif is_absolute:
        src_ref = xml
        srcs = []
    else:
        fail("wayland_protocol_library xml must be an absolute path or a target label starting with ':'")

    native.genrule(
        name = name + "_header",
        srcs = srcs,
        out = header_out,
        cmd = "wayland-scanner client-header " + src_ref + " $OUT",
    )

    native.genrule(
        name = name + "_source",
        srcs = srcs,
        out = source_out,
        cmd = "wayland-scanner private-code " + src_ref + " $OUT",
    )
    native.cxx_library(
        name = name,
        srcs = [":" + name + "_source"],
        exported_headers = [":" + name + "_header"],
        header_namespace = "",
        preferred_linkage = "static",
        link_whole = True,
        visibility = visibility,
        within_view = visibility,
    )

