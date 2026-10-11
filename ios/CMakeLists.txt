cmake_minimum_required(VERSION 3.21)
project(SandstrikeIOS C CXX)

set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(GAME_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../app/src/main/cpp)
set(RS       ${GAME_DIR}/raylib/src)
set(SDL_DIR  ${CMAKE_CURRENT_SOURCE_DIR}/SDL2)

foreach(p ${RS}/raylib.h ${SDL_DIR}/include/SDL.h)
    if(NOT EXISTS ${p})
        message(FATAL_ERROR "Нет файла ${p}. Сначала скачайте raylib и SDL2 (см. .github/workflows/build-ipa.yml)")
    endif()
endforeach()

# ---- SDL2 (статически) ----
set(SDL_SHARED OFF CACHE BOOL "" FORCE)
set(SDL_STATIC ON  CACHE BOOL "" FORCE)
set(SDL_TEST   OFF CACHE BOOL "" FORCE)
set(SDL2_DISABLE_INSTALL ON CACHE BOOL "" FORCE)
add_subdirectory(${SDL_DIR} SDL2 EXCLUDE_FROM_ALL)

# ---- raylib 5.5 на SDL-бэкенде + OpenGL ES 2 ----
add_library(raylib STATIC
    ${RS}/rcore.c ${RS}/rshapes.c ${RS}/rtextures.c ${RS}/rtext.c
    ${RS}/rmodels.c ${RS}/raudio.c ${RS}/utils.c)
target_compile_definitions(raylib PUBLIC PLATFORM_DESKTOP_SDL GRAPHICS_API_OPENGL_ES2)
target_include_directories(raylib PUBLIC ${RS} ${RS}/external ${SDL_DIR}/include)
target_compile_options(raylib PRIVATE -Wno-everything)
target_link_libraries(raylib PUBLIC SDL2-static)

# ---- игра ----
set(ASSETS ${GAME_DIR}/../assets/menu_bg.jpg ${CMAKE_CURRENT_SOURCE_DIR}/Icon.png)
add_executable(sandstrike MACOSX_BUNDLE
    ${GAME_DIR}/main.cpp
    ios_entry.c
    ${SDL_DIR}/src/main/uikit/SDL_uikit_main.c
    ${ASSETS})
target_include_directories(sandstrike PRIVATE ${RS} ${SDL_DIR}/include)
target_compile_options(sandstrike PRIVATE -O2 -Wno-everything)
target_link_libraries(sandstrike PRIVATE raylib
    "-framework UIKit" "-framework Foundation" "-framework OpenGLES" "-framework QuartzCore"
    "-framework CoreGraphics" "-framework CoreMotion" "-framework CoreHaptics" "-framework GameController"
    "-framework AudioToolbox" "-framework AVFoundation" "-framework CoreAudio" "-framework CoreMedia"
    "-framework CoreVideo" "-framework Metal" "-framework ImageIO" "-framework MobileCoreServices"
    "-framework CoreBluetooth")
set_target_properties(sandstrike PROPERTIES
    MACOSX_BUNDLE_INFO_PLIST ${CMAKE_CURRENT_SOURCE_DIR}/Info.plist
    RESOURCE "${ASSETS}"
    XCODE_ATTRIBUTE_PRODUCT_BUNDLE_IDENTIFIER "com.sandstrike.game"
    XCODE_ATTRIBUTE_TARGETED_DEVICE_FAMILY "1,2"
    XCODE_ATTRIBUTE_ENABLE_BITCODE "NO"
    XCODE_ATTRIBUTE_CODE_SIGNING_ALLOWED "NO"
    XCODE_ATTRIBUTE_CODE_SIGNING_REQUIRED "NO")
