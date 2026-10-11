#!/usr/bin/env python3
"""Патчи raylib 5.5 для запуска на iOS через SDL2.
Запускается из корня проекта: python3 ios/patch_raylib.py"""
import re, sys, pathlib

RS = pathlib.Path("app/src/main/cpp/raylib/src")

# --- 1. rlgl.h: на iOS «экранный» framebuffer у SDL не равен 0 ---------------
p = RS / "rlgl.h"
s = p.read_text(encoding="utf-8")
if "rlDefaultFBO" not in s:
    n = s.count("glBindFramebuffer(GL_FRAMEBUFFER, 0)")
    s = s.replace("glBindFramebuffer(GL_FRAMEBUFFER, 0)", "glBindFramebuffer(GL_FRAMEBUFFER, rlDefaultFBO)")
    print(f"[patch] rlgl.h: заменено glBindFramebuffer(..., 0): {n}")
    # объявление переменной сразу после начала секции реализации
    m = re.search(r"^#if defined\(RLGL_IMPLEMENTATION\)\s*$", s, re.M)
    if not m:
        sys.exit("[patch] ОШИБКА: не найден '#if defined(RLGL_IMPLEMENTATION)' в rlgl.h")
    s = s[:m.end()] + "\nstatic unsigned int rlDefaultFBO = 0;   // iOS/SDL: запоминаем экранный FBO\n" + s[m.end():]
    # запоминаем FBO при инициализации (контекст уже создан)
    m = re.search(r"^void rlglInit\(int width, int height\)\s*\n\{", s, re.M)
    if not m:
        sys.exit("[patch] ОШИБКА: не найдена функция rlglInit в rlgl.h")
    s = s[:m.end()] + "\n    { GLint fb0 = 0; glGetIntegerv(GL_FRAMEBUFFER_BINDING, &fb0); rlDefaultFBO = (unsigned int)fb0; }\n" + s[m.end():]
    p.write_text(s, encoding="utf-8")
    print("[patch] rlgl.h: ок")
else:
    print("[patch] rlgl.h уже пропатчен")

# --- 2. диагностика SDL-бэкенда (в лог сборки, чтобы проще чинить) ----------
b = RS / "rcore_desktop_sdl.c"
t = b.read_text(encoding="utf-8")
print("[diag] rcore_desktop_sdl.c: SDL_FINGERDOWN:", "SDL_FINGERDOWN" in t,
      "| SDL_WINDOW_ALLOW_HIGHDPI:", "SDL_WINDOW_ALLOW_HIGHDPI" in t,
      "| SDL_GL_CONTEXT_PROFILE_ES:", "SDL_GL_CONTEXT_PROFILE_ES" in t)
if "SDL_FINGERDOWN" not in t:
    print("[diag] ВНИМАНИЕ: в SDL-бэкенде raylib нет обработки касаний - управление работать не будет")
