# Windows: allow building vllm-flash-attn with Python 3.14.
# The pinned vllm-flash-attn commit lists Python 3.9-3.13 as supported; newer
# upstream flash-attention commits add "3.14". Run as a FetchContent
# PATCH_COMMAND (working directory = flash-attn source), so it takes effect
# before flash-attn's own configure step. Idempotent.
set(_fa_cmakelists "CMakeLists.txt")
file(READ "${_fa_cmakelists}" _fa_content)
if(NOT _fa_content MATCHES "PYTHON_SUPPORTED_VERSIONS[^)]*\"3\\.14\"")
  string(REPLACE "\"3.12\" \"3.13\")" "\"3.12\" \"3.13\" \"3.14\")" _fa_new "${_fa_content}")
  if(_fa_new STREQUAL _fa_content)
    message(FATAL_ERROR "windows_flash_attn_py314.cmake: Python version list not found in ${_fa_cmakelists}")
  endif()
  file(WRITE "${_fa_cmakelists}" "${_fa_new}")
  message(STATUS "Added Python 3.14 to vllm-flash-attn supported versions")
endif()
