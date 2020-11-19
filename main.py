import pyxel
import math
import time
import copy
import random
import time
from enum import Enum,auto
from threading import Thread

"""
MIT License

Copyright (c) 2018 Takashi Kitao

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

#
#TODO
#

#
#命名ルール
#
#1.グローバル変数は全て大文字
#2.クラス名は1文字目のみ大文字
#3.ローカル関数、ローカル変数は全て小文字

#グローバル変数の説明
#プレイヤー辞書のキーバリューは{ステージ番号：[開始時X座標、開始時Y座標]}
#ボックス辞書のキーバリューは{ステージ番号：[X,Y,移動フラグ,ゴールフラグ,X座標欄外フラグ,Y座標欄外フラグ]}
#タイルマップ辞書のキーバリューは{ステージ番号：[pyxel.bltmの引数仕様に習う]}。１ステージ２画面構成を考慮して辞書にした。

SCENE_NEXT = 0
SCENE_PLAY = 1
SCENE_CLEAR = 2
PLAYER={0:[16,48],1:[16,16],2:[16,16],3:[16,16],4:[16,16],5:[32,16],\
        6:[48,16],7:[32,16],8:[16,16],9:[48,16],10:[16,32],\
        11:[16,16],12:[16,16],13:[16,96],14:[16,16],15:[16,16],\
        16:[16,16],17:[16,16],18:[80,48],19:[16,16],20:[16,16],}

BOX={0:[[32,48,0,0,0,0]],1:[[80,32,0,0,0,0]],2:[[64,32,0,0,0,0]],3:[[32,48,0,0,0,0]],4:[[32,64,0,0,0,0]],5:[[48,32,0,0,0,0]],\
        6:[[48,48,0,0,0,0]],7:[[32,48,0,0,0,0]],8:[[48,16,0,0,0,0],[48,96,0,0,0,0]],9:[[32,64,0,0,0,0],[80,64,0,0,0,0]],10:[[48,32,0,0,0,0]],\
        11:[[32,48,0,0,0,0]],12:[[32,32,0,0,0,0]],13:[[32,80,0,0,0,0]],14:[[80,32,0,0,0,0]],15:[[64,32,0,0,0,0]],\
        16:[[64,32,0,0,0,0],[176,80,0,0,0,0]],17:[[64,32,0,0,0,0],[176,64,0,0,0,0]],18:[[48,48,0,0,0,0]],19:[[160,96,0,0,0,0]],20:[[48,16,0,0,0,0],[32,64,0,0,0,0]],}

TILEMAP={0:[0,0,0,0,0,16,16,0],1:[0,0,0,16,0,16,16,0],2:[0,0,0,32,0,16,16,0],3:[0,0,0,48,0,16,16,0],4:[0,0,0,64,0,16,16,0],5:[0,0,0,80,0,16,16,0],\
        6:[0,0,0,96,0,16,16,0],7:[0,0,0,112,0,16,16,0],8:[0,0,0,128,0,16,16,0],9:[0,0,0,144,0,16,16,0],10:[0,0,0,160,0,16,16,0],\
        11:[0,0,0,176,0,16,16,0],12:[0,0,0,192,0,16,16,0],13:[0,0,0,208,0,16,16,0],14:[0,0,0,224,0,16,16,0],15:[0,0,0,240,0,16,16,0],\
        16:[0,0,0,0,16,16,16,0],17:[0,0,0,32,16,16,16,0],18:[0,0,0,80,16,16,16,0],19:[0,0,0,96,16,16,16,0],20:[0,0,0,128,16,16,16,0],}
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
        self.stage_count=-1
        self.player_img = 0
        self.clear=SCENE_PLAY

        #時間系
        self.clear_pause_time = 4
        self.title_frame_count=0
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
            if pyxel.tilemap(0).get(math.floor(self.player_x/8)+self.move_x*2+self.stage_pogition_x, math.floor(self.player_y/8)+self.move_y*2+self.stage_pogition_y) in [ 64,65 ]:
                self.move_count=0
            #ステージクリア後はキャラが動けないようにする。
            if self.clear_count >= len(self.box_list):
                self.move_count=0

            #画面スクロール系
            #スクロール後、プレイヤーと箱の座標をどう処理するか決める。
            #
            if (math.floor(self.player_x/8)+self.move_x*2+self.stage_pogition_x) >= self.stage_pogition_x+16:
                self.tilemap_list[3] += 16
                self.stage_pogition_x += 16
                self.player_x = -16
                for i in self.box_list:
                    if i[0] == 128 and i[4] == 1:
                        i[0]=0
                        i[4]=0
                    elif i[4] == 0 and i[0] < 128:
                        i[0] += 128
                    elif i[4] == 0 and i[0] >= 128:
                        i[0] -= 128
            elif (math.floor(self.player_y/8)+self.move_y*2+self.stage_pogition_y) >= self.stage_pogition_y+16:
                self.tilemap_list[4] += 16
                self.stage_pogition_y += 16
                self.player_y = -16
                for i in self.box_list:
                    if i[1] == 128 and i[5] == 1:
                        i[1]=0
                        i[5]=0
                    elif i[5] == 0 and i[1] < 128:
                        i[1] += 128
                    elif i[5] == 0 and i[1] >= 128:
                        i[1] -= 128
            elif (math.floor(self.player_x/8)+self.move_x*2+self.stage_pogition_x) < self.stage_pogition_x:
                self.tilemap_list[3] -= 16
                self.stage_pogition_x -= 16
                self.player_x = +128
                for i in self.box_list:
                    if i[0] == -16 and i[4] == 1:
                        i[0]=112
                        i[4]=0
                    elif i[4] == 0 and i[0] < 128:
                        i[0] += 128
                    elif i[4] == 0 and i[0] >= 128:
                        i[0] -= 128
            elif (math.floor(self.player_y/8)+self.move_y*2+self.stage_pogition_y) < self.stage_pogition_y:
                self.tilemap_list[4] -= 16
                self.stage_pogition_y -= 16
                self.player_y = +128
                for i in self.box_list:
                    if i[1] == -16 and i[5] == 1:
                        i[1]=112
                        i[5]=0
                    elif i[5] == 0 and i[1] < 128:
                        i[1] += 128
                    elif i[5] == 0 and i[1] >= 128:
                        i[1] -= 128

            for i in self.box_list:
                #進行方向に箱があればクラス変数moveをTrueにする
                if (self.player_x+self.move_x*16 == i[0]) and (self.player_y+self.move_y*16 == i[1]):
                    i[2] = 1
                    for m in self.box_list:
                        #プレイヤーが押そうとした箱の移動方向に箱がある、もしくはプレイヤーが押そうとした箱の移動方向に壁がある(タイルマップからデータを取得して判断)なら箱もプレイヤーも移動しない
                        if (i[0]+self.move_x*16 == m[0]) and (i[1]+self.move_y*16 == m[1]) or (pyxel.tilemap(0).get(math.floor(i[0]/8)+self.move_x*2+self.stage_pogition_x, math.floor(i[1]/8)+self.move_y*2+self.stage_pogition_y) in  [ 64,65 ]):
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
        elif self.scene == GAMEMODE.End:
            self.update_end()
    
    def update_title(self):
        if pyxel.btnp(pyxel.KEY_ENTER):
            self.scene = GAMEMODE.Skit

    def update_skit(self):
        #変数の初期化をここで行う。
        #各種変数のセット
        self.stage_count+=1
        self.box_list = copy.deepcopy(BOX[self.stage_count])
        self.tilemap_list = copy.deepcopy(TILEMAP[self.stage_count])
        self.stage_pogition_x = copy.copy(self.tilemap_list[3])
        self.stage_pogition_y = copy.copy(self.tilemap_list[4])
        #移動系変数
        self.move_count=0
        self.move_x=0
        self.move_y=0
        #プレイヤー変数
        self.player_x = list(PLAYER[self.stage_count])[0]
        self.player_y = list(PLAYER[self.stage_count])[1]
        #クリア判定関連変数
        self.time_count = []
        self.clear_count=0
        self.start_time = int(time.time())

        time.sleep(2)
        pyxel.playm(0, loop=True)
        self.scene = GAMEMODE.Main
    
    def update_end(self):
        if pyxel.btnp(pyxel.KEY_ENTER):
            self.scene = GAMEMODE.Title

    def update_main(self):
        #ゲーム終了
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if self.clear_count < len(self.box_list):
            #リスタート
            if pyxel.btn(pyxel.KEY_SPACE):
                self.stage_count-=1
                pyxel.stop()
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
        if self.clear_pause_time == len(self.time_count):
            self.clear=SCENE_PLAY
            pyxel.stop()
            if self.stage_count+1 == len(BOX):
                self.stage_count=-1
                self.title_frame_count=0
                self.scene = GAMEMODE.End
            else:
                self.scene = GAMEMODE.Skit

    #
    #画面描画系関数
    #
    def draw(self):
        pyxel.cls(0)
        if self.scene == GAMEMODE.Title:
            self.draw_title()
        elif self.scene == GAMEMODE.Skit:
            self.draw_skit()
        elif self.scene == GAMEMODE.Main:
            self.draw_main()
        elif self.scene == GAMEMODE.End:
            self.draw_end()
    
    #時間差計算変数
    #花火の爆発スピードをあげる：lの数字を１より高くする。
    def time_diff(self,detonation_velocity, start_time, coefficient):
        diff = (int(time.time()* detonation_velocity )-start_time * coefficient)
        return diff

    #花火変数

    #剰余を1から3で出力して花火を3段階で描画する。

    #打ち上げ花火
    def lanchset(self, x, y, explosion_cycle, delay):
        temp = int(self.time_diff(5,self.start_time,5))% explosion_cycle
        if temp > explosion_cycle / 2:
            self.pset(x, y-explosion_cycle, explosion_cycle/2, delay)
        elif temp < explosion_cycle/2 :
            pyxel.pset( x+int(random.random()*2.4), y-( temp + delay )*3, (int(random.random()*10)*pyxel.frame_count) % 16)

    #花火の火の輪
    def pset(self, x, y, explosion_cycle, delay):
        temp = ((int(self.time_diff(5,self.start_time,5))% explosion_cycle )+ delay )*3
        if temp >= 0:
            for m in range(1,9):
                r = ( 40*m/360 ) * (math.pi*2)
                s = math.sin(r)
                c = math.cos(r)
                pyxel.pset(x+(temp*c), y+(temp*s), (int(random.random()*10)*pyxel.frame_count) % 16)

    def draw_title(self):
        pyxel.text(49, 36, "SOUKOBAN", pyxel.frame_count % 16)
        pyxel.text(45, 60, "PUSH ENTER", pyxel.frame_count % 16)
        #フレームカウントを利用してアニメーションさせることにした。
        if self.title_frame_count <= 160:
            self.title_frame_count += 1 if (pyxel.frame_count//30)%2 == 0 else 1
            pyxel.blt(self.title_frame_count,96,0,80,0 if (pyxel.frame_count//30)%2 == 0 else 16,16,16,0)
            pyxel.blt(self.title_frame_count-16,96,0,96,0 if (pyxel.frame_count//30)%2 == 0 else 16,16,16,0)
            pyxel.blt(self.title_frame_count-32,96,0,112,0 if (pyxel.frame_count//30)%2 == 0 else 16,16,16,0)
        else:
            self.title_frame_count=0

    def draw_skit(self):
        pyxel.text(50, 48, "STAGE:"+str(self.stage_count+2), 7)

    def draw_end(self):
        self.pset(55,80,5,-1)
        self.lanchset(50,90,16,0)
        self.pset(70,85,5,-1)
        self.lanchset(85,90,16,0)
        pyxel.text(44, 30, "ALL CLEAR!!", 7)
        pyxel.text(36, 48, "KIMI HA SUGOI !!", 7)
        pyxel.blt(60, 96,0,64,0 if (pyxel.frame_count//30)%2 == 0 else 16,16,16,0)

    #DRAW_MAIN系
    #クリア判定のロジック

    #darw_main関数での処理
    #＞ボックスがゴールに置かれたら、クリアカウントをアップ。さらに箱のフラグをチェック(箱のリスト４番目の要素)。
    #＞クリアカウントが箱リストの数に達したら、クリアフラグをチェック。
    #＞チェック後処理を行う
    #update_main関数へ処理を移す。
    #＞ステージカウントUP、モードリセットを行う

    def draw_main(self):
        #MAPの読込み
        pyxel.bltm(*self.tilemap_list)
        #クリアフラグチェック後の処理
        if self.clear == SCENE_CLEAR:
            pyxel.text(43,56,"STAGE CLEAR!",pyxel.frame_count % 16)
            if self.time_diff(1,self.start_time,1)%self.clear_pause_time not in self.time_count:
                self.time_count.append(self.time_diff(1,self.start_time,1)%self.clear_pause_time)
        #箱がゴールに辿り着いたときの処理分岐
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
                if i[0] == 128 or i[0] == -16:
                    i[4] = 1
                elif i[1] == 128 or i[1] == -16:
                    i[5] = 1
                else:
                    pyxel.blt(i[0],i[1],0,0,32,16,16,0)
        #十字キーの入力に合わせて描画するプレイヤーイメージを変更
        if self.player_img <= 1:
            pyxel.blt(self.player_x, self.player_y,0,16*self.player_img,0, 16 if (pyxel.frame_count//30)%2 == 0 else -16,16,0)
        else:
            pyxel.blt(self.player_x, self.player_y,0,16*self.player_img,0 if (pyxel.frame_count//30)%2 == 0 else 16,16,16,0)

App()