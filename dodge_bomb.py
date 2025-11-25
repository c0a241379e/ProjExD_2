import os
import sys
import random
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, 5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (5, 0),
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple:
    """Rectが画面内なら (True, True) を返す。
    戻り値 (in_x, in_y) は横方向・縦方向が画面内かを示す。
    """
    in_x = 0 <= rct.left and rct.right <= WIDTH
    in_y = 0 <= rct.top and rct.bottom <= HEIGHT
    return in_x, in_y

def show_game_over(screen: pg.Surface, kk_img: pg.Surface, kk_rct: pg.Rect) -> None:
    """ゲームオーバー画面を表示する。"""
    # 背景を真っ暗にする
    screen.fill((0, 0, 0))

    # こうかトンの画像を切り替えて中央に配
    kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1.5)   
    kk_rct = kk_img.get_rect()
    kk_rct.center = (WIDTH // 2, HEIGHT // 2 + 100)

    # GameOver テキスト
    font = pg.font.Font(None, 100)
    txt_surf = font.render("GameOver", True, (255, 0, 0))
    txt_rct = txt_surf.get_rect()
    txt_rct.center = (WIDTH // 2, HEIGHT // 2)

    # 描画
    screen.blit(kk_img, kk_rct)
    screen.blit(txt_surf, txt_rct)
    pg.display.update()
    # 表示を見せるために短く待機
    pg.time.wait(2000)


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    # 爆弾Surfaceを作成（半径10、赤）、黒を透明にする
    bb_img = pg.Surface((20, 20))
    bb_img.fill((0, 0, 0))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(10, WIDTH - 10), random.randint(10, HEIGHT - 10)
    vx, vy = 5, 5

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:   # クリックされたら
                return
        screen.blit(bg_img, [0, 0])

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for k, mv in DELTA.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        # こうかとんを移動させ，画面外になったら移動前の位置に戻す
        prev_center = kk_rct.center
        kk_rct.move_ip(sum_mv)
        in_x, in_y = check_bound(kk_rct)
        if not (in_x and in_y):
            kk_rct.center = prev_center

        # 爆弾の次フレーム位置を確認し，画面外に出る方向の速度を反転して移動
        next_bb = bb_rct.move(vx, vy)
        in_x_bb, in_y_bb = check_bound(next_bb)
        if not in_x_bb:
            vx *= -1
        if not in_y_bb:
            vy *= -1
        bb_rct.move_ip(vx, vy)

        # 衝突判定: こうかとんが爆弾と衝突したらGameOver画面を表示して終了
        if kk_rct.colliderect(bb_rct):
            show_game_over(screen, kk_img, kk_rct)
            return

        # 描画
        screen.blit(bg_img, [0, 0])
        screen.blit(bb_img, bb_rct)
        screen.blit(kk_img, kk_rct)

        pg.display.update()
        tmr += 1
        clock.tick(50)

#  commitの調整1

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
