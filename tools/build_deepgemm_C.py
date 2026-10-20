# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
"""Build DeepGEMM's TORCH_LIBRARY extension and copy vendored artifacts.

DeepGEMM now registers ops via TORCH_LIBRARY into ``deep_gemm._C_extension``
(abi3) and exposes the legacy API through ``deep_gemm/_C.py``. This driver
delegates to DeepGEMM's ``setup.py build_ext --inplace`` and copies the shim
plus extension into the cmake output directory.

Usage: python build_deepgemm_C.py <DEEPGEMM_SRC_DIR> <OUTPUT_DIR>
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

if len(sys.argv) != 3:
    sys.exit(f"usage: {sys.argv[0]} <SRC> <OUT>")

src = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
_pkg = src / "deep_gemm"
out.mkdir(parents=True, exist_ok=True)

if not (_pkg / "_C.py").is_file():
    sys.exit(
        f"DeepGEMM source at {src} is missing deep_gemm/_C.py; "
        "expected TORCH_LIBRARY migration layout"
    )

# Avoid DeepGEMM's clean-git assertion when vendoring a local dirty tree.
env = os.environ.copy()
env.pop("DG_SKIP_CUDA_BUILD", None)

print(f"[build_deepgemm_C] building in {src} with {sys.executable}", flush=True)
subprocess.check_call(
    [sys.executable, "setup.py", "build_ext", "--inplace"],
    cwd=src,
    env=env,
)

shim = _pkg / "_C.py"
shutil.copy2(shim, out / shim.name)

# The stable-ABI extension is built as _C_extension.abi3.so on POSIX and
# _C_extension.abi3.PYD on Windows; without the abi3 suffix the build
# falls back to plain _C_extension.so / _C_extension.pyd.
for pattern in ("_C_extension.abi3.*", "_C_extension.*"):
    candidates = [
        c for c in _pkg.glob(pattern)
        if c.suffix.lower() in (".so", ".pyd")
    ]
    if candidates:
        break
if not candidates:
    sys.exit(f"DeepGEMM build did not produce _C_extension.* in {_pkg}")
so = candidates[0]
for stale in out.glob("_C_extension*"):
    stale.unlink()
shutil.copy2(so, out / so.name)
print(f"[build_deepgemm_C] installed {so.name} -> {out}", flush=True)
