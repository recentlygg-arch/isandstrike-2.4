/* Точка входа iOS. SDL.h переименовывает main -> SDL_main, а настоящий main
   (SDL_uikit_main.c) запускает UIKit и потом вызывает этот SDL_main. */
#include <SDL.h>

extern int game_main(int sw, int sh);   /* в main.cpp */

int main(int argc, char *argv[])
{
    int w = 1280, h = 720;
    (void)argc; (void)argv;
    if (SDL_Init(SDL_INIT_VIDEO) == 0) {
        SDL_Rect r;
        if (SDL_GetDisplayBounds(0, &r) == 0 && r.w > 0 && r.h > 0) {
            w = r.w > r.h ? r.w : r.h;      /* всегда альбомная ориентация */
            h = r.w > r.h ? r.h : r.w;
        }
    }
    return game_main(w, h);
}
