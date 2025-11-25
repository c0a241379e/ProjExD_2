import os
import pygame as pg
import random
import sys




WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, 5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (5, 0),
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect, *, prev_center: tuple | None = None, obj_type: str | None = None, vx: float | None = None, vy: float | None = None) -> tuple:
    """Rect が画面内かを判定する。

    基本戻り値は (in_x, in_y) だが、オプションでオブジェクト種別を渡すと副作用を行う：
    - obj_type='player': 画面外なら rct を `prev_center` に戻す（移動前に戻す）。
    - obj_type='bomb'  : 画面外になった軸について vx/vy の符号を反転し、
                         画面外の場合は rct を `prev_center` に戻す（1 フレーム分戻す）。

    引数:
      rct: 判定対象の Rect
      prev_center: 画面外だったときに戻すための直前の中心座標（(x,y)）
      obj_type: 'player' または 'bomb'（もしくは None）
      vx, vy: 爆弾用の速度成分（obj_type='bomb' のときのみ使用）

    戻り値:
      (in_x, in_y, vx, vy)
      - vx, vy は obj_type='bomb' の場合に更新された速度（反転済み）を返す。
      - それ以外の場合は vx, vy に None を返す。
    """
    in_x = 0 <= rct.left and rct.right <= WIDTH
    in_y = 0 <= rct.top and rct.bottom <= HEIGHT

    out_vx, out_vy = None, None
    # プレイヤーならはみ出していたら直前位置に戻す
    if obj_type == 'player':
        if not (in_x and in_y) and prev_center is not None:
            rct.center = prev_center

    # 爆弾ならはみ出した軸の速度を反転し、はみ出していたら直前位置に戻す
    if obj_type == 'bomb':
        if vx is None or vy is None:
            out_vx, out_vy = vx, vy
        else:
            if not in_x:
                out_vx = -vx
            else:
                out_vx = vx
            if not in_y:
                out_vy = -vy
            else:
                out_vy = vy
        if not (in_x and in_y) and prev_center is not None:
            rct.center = prev_center

    return in_x, in_y, out_vx, out_vy

def show_game_over(screen: pg.Surface, kk_img: pg.Surface, kk_rct: pg.Rect) -> None:
    """ゲームオーバー画面を表示する。
    
    引数:
      screen (pg.Surface): 描画対象のスクリーン表面
      kk_img (pg.Surface): こうかとん画像（現在は使用されない）
      kk_rct (pg.Rect): こうかとんの矩形（現在は使用されない）
    
    戻り値:
      なし（None）
    
    動作:
      1. 背景を黒で塗りつぶす
      2. こうかとん（fig/8.png）を 1.5 倍に縮放して中央下に配置
      3. 赤い \"GameOver\" テキストを中央に配置
      4. すべてを描画して画面更新
      5. 2000 ms（2 秒）待機
    """
    # 背景を真っ暗にする
    screen.fill((0, 0, 0))

    # こうかトンの画像を切り替えて中央に配置
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


def show_clear(screen: pg.Surface, score: int) -> None:
    """ゲームクリア画面を表示する。
    
    引数:
      screen (pg.Surface): 描画対象のスクリーン表面
      score (int): 生存フレーム数またはスコア値
    
    戻り値:
      なし（None）
    
    動作:
      1. 背景を黒で塗りつぶす
      2. こうかとん（fig/6.png）を 1.5 倍に縮放して中央下に配置
      3. 緑の \"Clear!\" テキストを中央やや上に配置
      4. 白いスコア表示（\"Score: {score}\"）を中央やや下に配置
      5. すべてを描画して画面更新
      6. 2000 ms（2 秒）待機
    """
    screen.fill((0, 0, 0))

    # こうかとんを少し大きくして中央に表示
    kk_img = pg.transform.rotozoom(pg.image.load("fig/6.png"), 0, 1.5)
    kk_rct = kk_img.get_rect()
    kk_rct.center = (WIDTH // 2, HEIGHT // 2 + 80)

    # Clear テキスト
    font_big = pg.font.Font(None, 100)
    txt_surf = font_big.render("Clear!", True, (0, 255, 0))
    txt_rct = txt_surf.get_rect()
    txt_rct.center = (WIDTH // 2, HEIGHT // 2 - 40)

    # スコア表示
    font_score = pg.font.Font(None, 50)
    score_surf = font_score.render(f"Score: {score}", True, (255, 255, 255))
    score_rct = score_surf.get_rect()
    score_rct.center = (WIDTH // 2, HEIGHT // 2 + 140)

    screen.blit(kk_img, kk_rct)
    screen.blit(txt_surf, txt_rct)
    screen.blit(score_surf, score_rct)
    pg.display.update()
    pg.time.wait(2000)


def prepare_bomb_images() -> tuple[list[pg.Surface], list[float]]:
    """爆弾の段階別画像と加速度リストを生成する。
    
    引数:
      なし
    
    戻り値:
      tuple[list[pg.Surface], list[float]]: (bb_imgs, bb_accs)
        - bb_imgs: サイズ 20x20 から 200x200 まで 10 段階の赤い円形 Surface リスト
        - bb_accs: 加速度倍率 [1.0, 1.1, 1.2, ..., 1.9] のリスト
    
    動作:
      1. r=1 から 10 まで、各段階で次のサイズの画像を作成
         - サイズ: 20*r × 20*r（例: r=1 => 20x20、r=10 => 200x200）
         - 形状: 黒い背景に赤い円（半径 10*r）を描画
      2. 加速度倍率を 1.0 から 1.9 まで 0.1 刻みで生成
    """
    bb_imgs: list[pg.Surface] = []
    for r in range(1, 11):
        size = 20 * r
        surf = pg.Surface((size, size))
        surf.fill((0, 0, 0))
        pg.draw.circle(surf, (255, 0, 0), (size // 2, size // 2), 10 * r)
        surf.set_colorkey((0, 0, 0))
        bb_imgs.append(surf)
    # 加速度リスト（倍率）: 1.0 から 1.9 まで段階的に増加
    bb_accs = [1.0 + 0.1 * a for a in range(10)]
    return bb_imgs, bb_accs


def prepare_kokaton_images() -> dict:
    """こうかとんの方向別画像を辞書で生成する。
    
    引数:
      なし
    
    戻り値:
      dict: キーは移動ベクトル (dx, dy)、値は回転・縮放済みの pygame.Surface
            - (0, 0): 静止画（fig/3.png）
            - (5, 0): 右向き（fig/0.png）
            - (-5, 0): 左向き（fig/2.png）
            - (0, 5): 下向き（fig/1.png）
            - (0, -5): 上向き（fig/3.png）
            - 斜め移動: 横向き画像を優先
    
    動作:
      各画像を 0.9 倍に縮放してロード。指定なき移動ベクトルは
      デフォルト画像で補完される。
    """
    imgs = {}
    imgs[(0, 0)] = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    imgs[(5, 0)] = pg.transform.rotozoom(pg.image.load("fig/0.png"), 0, 0.9)
    imgs[(-5, 0)] = pg.transform.rotozoom(pg.image.load("fig/2.png"), 0, 0.9)
    imgs[(0, 5)] = pg.transform.rotozoom(pg.image.load("fig/1.png"), 0, 0.9)
    imgs[(0, -5)] = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    # 斜め移動は横向き画像を優先（好みで変更可）
    imgs[(5, 5)] = imgs[(5, 0)]
    imgs[(5, -5)] = imgs[(5, 0)]
    imgs[(-5, 5)] = imgs[(-5, 0)]
    imgs[(-5, -5)] = imgs[(-5, 0)]
    return imgs


def chase_vector(org: pg.Rect, dst: pg.Rect, current_vx: float, current_vy: float) -> tuple:
    """爆弾がこうかとん方向に移動する追従ベクトルを計算する。
    
    引数:
      org (pg.Rect): 爆弾の Rect（追従元）
      dst (pg.Rect): こうかとんの Rect（追従先）
      current_vx (float): 現在の x 方向速度（慣性維持用）
      current_vy (float): 現在の y 方向速度（慣性維持用）
    
    戻り値:
      tuple: (vx, vy) 移動ベクトル
    
    動作:
      - 距離が 500 px 未満: 現在の速度 (current_vx, current_vy) をそのまま返す（慣性）
      - 距離が 500 px 以上: dst - org の差ベクトルを √50 に正規化して返す（追従）
    """
    org_x, org_y = org.center
    dst_x, dst_y = dst.center

    dx = dst_x - org_x
    dy = dst_y - org_y
    distance = (dx ** 2 + dy ** 2) ** 0.5

    # 近ければ慣性で移動
    if distance < 300:
        return current_vx, current_vy

    target_norm = 50 ** 0.5  # √50
    if distance > 0:
        vx = (dx / distance) * target_norm
        vy = (dy / distance) * target_norm
    else:
        vx, vy = 0, 0

    return vx, vy



def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """2つのRectの位置関係から相対方向を計算する。
    
    引数:
      org (pg.Rect): 基準となるオブジェクトの Rect
      dst (pg.Rect): 比較対象のオブジェクトの Rect
      current_xy (tuple[float, float]): 未使用（互換性保持のためのみ）
    
    戻り値:
      tuple[float, float]: (orientation_x, orientation_y)
        - x 方向: 1.0（dst が右）/ -1.0（dst が左）/ 0.0（同じ x 座標）
        - y 方向: 1.0（dst が下）/ -1.0（dst が上）/ 0.0（同じ y 座標）
    
    動作:
      org から dst への相対位置を x・y それぞれで判定し、
      方向を -1.0 / 0.0 / 1.0 の 3 値で表現する。
    """
    dir_x = dst.centerx - org.centerx
    dir_y = dst.centery - org.centery

    if dir_x > 0:
        orientation_x = 1.0
    elif dir_x < 0:
        orientation_x = -1.0
    else:
        orientation_x = 0.0

    if dir_y > 0:
        orientation_y = 1.0
    elif dir_y < 0:
        orientation_y = -1.0
    else:
        orientation_y = 0.0

    return (orientation_x, orientation_y)

def main() -> None:
    """ゲームメインループ。
    引数:
      なし
    
    戻り値:
      なし（None）
    
    動作:
      1. Pygame 初期化済みを前提に、ゲームウィンドウ・画像・フォントを準備
      2. ゲームループを 50 FPS で実行
         - プレイヤー（こうかとん）の入力に応じて移動・画像切り替え
         - 爆弾の段階的成長・追従・壁反射を計算
         - スコア（生存フレーム）を毎フレーム加算
         - 衝突判定: プレイヤーが爆弾に触れたら show_game_over()
         - クリア判定: 生存時間が CLEAR_TMR 以上なら show_clear()
      3. 画面上にスコアを左上に表示
      4. ウィンドウを閉じるかゲーム終了時に return
    
    グローバル変数使用:
      - WIDTH, HEIGHT: 画面サイズ（1100x650）
      - DELTA: キー入力対応の移動量辞書
    """
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    # こうかとん画像辞書を準備
    kk_imgs = prepare_kokaton_images()

    # 爆弾Surfaceリストと加速度リストを準備（10段階）
    bb_imgs, bb_accs = prepare_bomb_images()
    idx = 0
    bb_img = bb_imgs[idx]
    bb_rct = bb_img.get_rect()
    # 爆弾の初期位置（中心座標）を画面内のランダムな点に設定
    bb_x = random.randint(bb_img.get_width() // 2, WIDTH - bb_img.get_width() // 2)
    bb_y = random.randint(bb_img.get_height() // 2, HEIGHT - bb_img.get_height() // 2)
    bb_rct.center = (bb_x, bb_y)
    vx, vy = 5, 5
    clock = pg.time.Clock()
    tmr = 0
    score = 0
    # 生存フレーム数でのクリア閾値（例: 30秒 * 50FPS = 1500フレーム）
    CLEAR_TMR = 10
    # スコア表示用フォント
    score_font = pg.font.Font(None, 50)

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


        # 合計移動量タプルに対応する画像を選択
        kk_img = kk_imgs.get((sum_mv[0], sum_mv[1]), kk_img)

        # こうかとんを移動させ，画面外なら check_bound 内で移動前の位置に戻す
        prev_center = kk_rct.center
        kk_rct.move_ip(sum_mv)
        in_x, in_y, _, _ = check_bound(kk_rct, prev_center=prev_center, obj_type='player')
        # 爆弾の段階（サイズ）と加速度を選択
        idx = min(tmr // 300, len(bb_imgs) - 1)
        if bb_img is not bb_imgs[idx]:
            old_center = bb_rct.center
            bb_img = bb_imgs[idx]
            bb_rct = bb_img.get_rect()
            bb_rct.center = old_center
            # Surfaceのサイズが変わった場合、Rectのサイズ属性を更新
            bb_rct.width = bb_img.get_rect().width
            bb_rct.height = bb_img.get_rect().height
        # 追従ベクトルを計算
        vx, vy = chase_vector(bb_rct, kk_rct, vx, vy)

        # 移動量を計算し、実際に移動してから画面内かを判定する
        avx = int(vx * bb_accs[idx])
        avy = int(vy * bb_accs[idx])
        prev_center_bb = bb_rct.center
        bb_rct.move_ip(avx, avy)
        # 実際の移動後のRectで判定（check_boundが位置復元・速度反転を行う）
        in_x_bb, in_y_bb, new_vx, new_vy = check_bound(bb_rct, prev_center=prev_center_bb, obj_type='bomb', vx=vx, vy=vy)
        # 返ってきた速度で更新（check_bound が None を返すことはないはずだが念のため）
        if new_vx is not None:
            vx = new_vx
        if new_vy is not None:
            vy = new_vy

        # スコアを時間経過で増加（フレーム毎に1ポイント）
        score += 1

        # クリア判定: 一定フレーム生存でクリア画面を表示して終了
        if tmr >= CLEAR_TMR:
            show_clear(screen, score)
            return

        # 衝突判定: こうかとんが爆弾と衝突したらGameOver画面を表示して終了
        if kk_rct.colliderect(bb_rct):
            show_game_over(screen, kk_img, kk_rct)
            return

        # 描画
        screen.blit(bg_img, [0, 0])
        screen.blit(bb_img, bb_rct)
        screen.blit(kk_img, kk_rct)

        # スコア描画（画面上に重ねる）
        score_surf = score_font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_surf, (10, 10))

        pg.display.update()
        tmr += 1
        clock.tick(50)

#  commitの調整1

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
