import pyxel
import math
import time
import copy
from enum import Enum,auto
from threading import Thread

#
#TODO
#

#
#命名ルール
#
#1.グローバル変数は全て大文字
#2.クラス名は1文字目のみ大文字
#3.ローカル関数、ローカル変数は全て小文字

#グローバル変数の設定
SCENE_NEXT = 0
SCENE_PLAY = 1
SCENE_CLEAR = 2
PLAYER={0:[16,48],1:[16,16],2:[16,16],3:[16,16],4:[16,16],5:[48,16],6:[32,16],7:[16,16],}
BOX={0:[[32,48,0]],1:[[80,32,0]],2:[[64,32,0]],3:[[80,32,0]],4:[[48,48,0]],5:[[48,48,0]],6:[[32,48,0]],7:[[48,96,0],[48,16,0]],}
BOX={0:[[32,48,0,0]],1:[[80,32,0,0]],2:[[64,32,0,0]],3:[[80,32,0,0]],4:[[48,48,0,0]],5:[[48,48,0,0]],6:[[32,48,0,0]],7:[[48,96,0,0],[48,16,0,0]],}
TILEMAP={0:[0,0,0,0,0,16,16,0],1:[0,0,0,16,0,16,16,0],2:[0,0,0,32,0,16,16,0],3:[0,0,0,48,0,16,16,0],4:[0,0,0,64,0,16,16,0],5:[0,0,0,80,0,16,16,0],6:[0,0,0,96,0,16,16,0],7:[0,0,0,112,0,16,16,0],}
SCREEN_SIZE=255

class GAMEMODE(Enum):
    # 画面のシーンをEnumで定義します
    Title = auto()
    Skit = auto()
    Main = auto()
    End = auto()

class App:
    #
    #初期化関数
    #
    def __init__(self):
        pyxel.init(128,128,caption="Warehouse keeper")
        pyxel.load('warehouse_keeper.pyxres')
        #
        #変数
        #
        #場面変数
        self.scene = GAMEMODE.Title
        
        #ステージカウント
        self.stage_count=5
        #self.stage_count=-1
        self.player_img = 0
        self.clear=SCENE_PLAY

        #起動
        pyxel.run(self.update,self.draw)

    #移動関数
    def move(self,x,y):
        if self.move_count==0:
            self.move_count=16
            self.move_x=x
            self.move_y=y
            
            #現在のタイルマップ上の座標からの移動先の座標は、オブジェクト番号64かどうかを判定する。
            #もしオブジェクト番号64ならばムーブカウントを強制的に0にして移動できなくする。
            if pyxel.tilemap(0).get(math.floor(self.player_x/8)+self.move_x*2+self.stage_pogition_x, math.floor(self.player_y/8)+self.move_y*2)+self.stage_pogition_y == 64:
                self.move_count=0
            
            if self.clear_count >= len(self.box_list):
                self.move_count=0

            for i in self.box_list:
                #進行方向に箱があればクラス変数moveをTrueにする
                if (self.player_x+self.move_x*16 == i[0]) and (self.player_y+self.move_y*16 == i[1]):
                    i[2] = 1
                    for m in self.box_list:
                        #プレイヤーが押そうとした箱の移動方向に箱がある、もしくはプレイヤーが押そうとした箱の移動方向に壁がある(タイルマップからデータを取得して判断)なら箱もプレイヤーも移動しない
                        if (i[0]+self.move_x*16 == m[0]) and (i[1]+self.move_y*16 == m[1]) or (pyxel.tilemap(0).get(math.floor(i[0]/8)+self.move_x*2+self.stage_pogition_x, math.floor(i[1]/8)+self.move_y*2+self.stage_pogition_y) == 64):
                            i[2]=0
                            self.move_count=0
                            break
                    #箱を押していない時
                else:
                    i[2] = 0

    #操作系関数
    def update(self):
        if self.scene == GAMEMODE.Title:
            self.update_title()
        elif self.scene == GAMEMODE.Skit:
            self.update_skit()
        elif self.scene == GAMEMODE.Main:
            self.update_main()
    
    def update_title(self):
        if pyxel.btnp(pyxel.KEY_ENTER):
            self.scene = GAMEMODE.Skit
    
    def update_skit(self):
        #変数の初期化をここで行う。

        #各種変数のセット
        self.stage_count+=1
        self.stage_pogition_x = self.stage_count*16
        self.stage_pogition_y = (self.stage_count//16)*16
        self.box_list = copy.deepcopy(BOX[self.stage_count])
        self.tilemap_list = TILEMAP[self.stage_count]
        #移動系変数
        self.move_count=0
        self.move_x=0
        self.move_y=0
        #プレイヤー変数
        self.player_x = list(PLAYER[self.stage_count])[0]
        self.player_y = list(PLAYER[self.stage_count])[1]
        #クリア判定変数
        self.clear_count=0
        time.sleep(1)
        self.scene = GAMEMODE.Main

    def update_main(self):
        #ゲーム終了
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if self.clear_count < len(self.box_list):
            #リスタート
            if pyxel.btn(pyxel.KEY_SPACE):
                self.stage_count-=1
                self.scene = GAMEMODE.Skit
        #キャラクター操作系
        if self.move_count==0:
            if pyxel.btn(pyxel.KEY_DOWN):
                self.player_img = 0
                self.move(0,1)
            elif pyxel.btn(pyxel.KEY_UP):
                self.player_img = 1
                self.move(0,-1)
            elif pyxel.btn(pyxel.KEY_RIGHT):
                self.player_img = 2
                self.move(1,0)
            elif pyxel.btn(pyxel.KEY_LEFT):
                self.player_img = 3
                self.move(-1,0)

        #箱操作系
        if self.move_count>0:
            self.move_count-=1
            self.player_x+=self.move_x
            self.player_y+=self.move_y
            for n in self.box_list:
                if n[2] == 1:
                    n[0] += self.move_x
                    n[1] += self.move_y

        #次ステージ向かう系
        if self.clear_count >= len(self.box_list)+90:
            self.clear=SCENE_PLAY
            self.scene = GAMEMODE.Skit

    #画面描画系関数
    def draw(self):
        pyxel.cls(0)
        if self.scene == GAMEMODE.Title:
            self.draw_title()
        elif self.scene == GAMEMODE.Skit:
            self.draw_skit()
        elif self.scene == GAMEMODE.Main:
            self.draw_main()

    def draw_title(self):
        pyxel.text(49, 36, "SOUKOBAN", pyxel.frame_count % 16)
        pyxel.text(45, 60, "PUSH ENTER", pyxel.frame_count % 16)

    def draw_skit(self):
        pyxel.text(50, 48, "STAGE:"+str(self.stage_count+2), 7)

    #DRAW_MAIN系

    #クリア判定のロジック    
    #通常時はクリアカウントで制限。
    #クリアカウントが規定数に達するとロックカウントが足され続ける。
    #update_main側でクリアカウントが一定のカウントに達したのを検知して次のステージへ向かう。
    
    #本当はフラグが立ったら一定時間の間クリアテキストを表示して、次ステージに向かうようにしたい。
    #スレッディングとか試みたがうまくいかなかった。。。。

    #ボックスがチェックポイントに置かれたかどうかの判定
    #リストの４番目の要素をフラグにして管理。

    def draw_main(self):
        #MAPの読込み
        pyxel.bltm(*self.tilemap_list)
        if self.clear == SCENE_CLEAR:
            pyxel.text(43,56,"GAME CLEAR!",pyxel.frame_count % 16)
            self.clear_count += 1
        for i in self.box_list:
            if pyxel.tilemap(0).get(round(i[0]/8)+self.stage_pogition_x,round(i[1]/8)+self.stage_pogition_y) == 130:
                if i[3] == 0:
                    pyxel.blt(i[0],i[1],0,32,32,16,16,0)
                    self.clear_count += 1
                    i[3] = 1
                elif i[3] == 1:
                    pyxel.blt(i[0],i[1],0,32,32,16,16,0)
                if self.clear_count == len(self.box_list):
                    self.clear=SCENE_CLEAR
            else:
                pyxel.blt(i[0],i[1],0,0,32,16,16,0)
        if self.player_img <= 1:
            pyxel.blt(self.player_x, self.player_y,0,16*self.player_img,0, 16 if (pyxel.frame_count//30)%2 == 0 else -16,16,0)
        else:
            pyxel.blt(self.player_x, self.player_y,0,16*self.player_img,0 if (pyxel.frame_count//30)%2 == 0 else 16,16,16,0)

App()