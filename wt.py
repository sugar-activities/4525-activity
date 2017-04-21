# wt.py
import utils,g,pygame,random

class Ball:
    def __init__(self):
        self.c=None # current x,y centre
        self.c0=None # x,y centre when level
        self.pan=1 # 0=left, 1=right
        self.posn=0 # position in pan 0 back, 1 left, 2 right, 3 top
        self.state=1 # 0=light, 1=normal, 2=heavy, 3=neutral
        self.active=False
        self.colour='blue'

class Wt:
    def __init__(self):
        # 0=left down, right up; 1=left up, right down; 2=level
        self.state=None
        self.scales=[]
        self.c=(g.sx(16),g.sy(12))
        for i in range(3):
            img=utils.load_image(str(i)+'.png',True,'scales')
            self.scales.append(img)
        self.balls=[]
        for i in range(12):
            ball=Ball(); self.balls.append(ball)
        self.legend=utils.load_image('legend.png',True)
        self.legend_xy=g.sx(12),g.sy(.9)
        self.smile=utils.load_image('smile.png',True)
        self.frown=utils.load_image('frown.png',True)
        self.tick=utils.load_image('tick.png',True)
        self.smile_l=g.sx(2.5),g.sy(15.2)
        self.smile_r=g.sx(29.5),g.sy(15.2)
        self.blue=utils.load_image('blue.png',True)
        self.red=utils.load_image('red.png',True)
        self.green=utils.load_image('green.png',True)
        self.gold=utils.load_image('gold.png',True)
        self.magenta=utils.load_image('magenta.png',True)
        self.white=utils.load_image('white.png',True)
        self.shadow=utils.load_image('shadow.png',True)
        self.d2=self.blue.get_width()/2
        self.light_img=utils.load_image('light.png',True)
        self.light_xy=(g.sx(.2),g.sy(16.1))
        self.heavy_img=utils.load_image('heavy.png',True)
        w=self.heavy_img.get_width()
        self.heavy_xy=(g.offset+g.sx(32)-w-self.light_xy[0],self.light_xy[1])
        self.nballs=None
        self.dxy=[] # offset of level balls from scales centre
        for x,y in[(5.6,3.6),(6.9,3.4),(4,3.4),(5.5,5.7)]: # b,l,r,t
            self.dxy.append((g.sy(x),g.sy(y)))
        self.dxy_ud=[]
        # left down, right up, left up, right down offsets from ball.c0
        for x,y in [(-.4,1),(.4,-1.46),(-.6,-1.5),(.24,.95)]:
            self.dxy_ud.append((g.sy(x),g.sy(y)))
        self.pan_n=[0,0]
        self.z=[]; self.carry=None
        self.set_pan_posns()

    def set_pan_posns(self):
        self.pan_posns=[[],[]] # left,right
        x0,y0=self.c
        for i in range(4):
            dx,dy=self.dxy[i]
            x=x0-dx; y=y0-dy; self.pan_posns[0].append((x,y))
            x=x0+dx; y=y0-dy; self.pan_posns[1].append((x,y))

    def setup(self):
        group=g.level # 1,2,3 or 4
        self.nballs=group*3 # 3,6,9,12
        x_free=g.sx(3); y_free=g.sy(2.7); dy_free=g.sy(3.2)
        self.free_rect=pygame.Rect(x_free-self.d2,y_free-self.d2,\
                                   2*self.d2,3*dy_free+self.d2)
        i=0; self.z=[]; self.pan_n[0]=0; self.pan_n[1]=0
        for ball in self.balls:
            ball.active=False; ball.colour='blue'
            if i<self.nballs:
                if i<group:
                    x,y=self.pan_posns[0][i]; ball.pan=0
                    self.pan_n[0]+=1; ball.posn=i
                elif i<group*2:
                    x,y=self.pan_posns[1][i-group]; ball.pan=1
                    self.pan_n[1]+=1; ball.posn=i-group
                else:
                    x=x_free; y=y_free; y_free+=dy_free; ball.pan=None
                ball.c0=(x,y); ball.c=(x,y); ball.active=True
                self.z.append(ball)
            i+=1
        self.carry=None
        ind=random.randint(0,self.nballs-1); self.rogue=self.balls[ind]
        self.heavy=random.randint(0,1)
        self.count=0; self.show_rogue=False; self.ms=pygame.time.get_ticks()
        self.flutter_k=None; self.flutter_ind=None; self.state_save=None
        self.state=2 # level
        self.result=None
        self.red_set=False # ensure exactly one red/gold per round

    def draw(self):
        self.draw_legend()
        utils.display_number(self.count,(g.sx(16),g.sy(8)),g.font2)
        img=self.scales[self.state]
        utils.centre_blit(g.screen,img,self.c)
        g.screen.blit(self.light_img,self.light_xy)
        g.screen.blit(self.heavy_img,self.heavy_xy)
        for ball in self.z:
            if ball.active:
                if ball!=self.carry:
                    img=self.ball_img(ball)
                    utils.centre_blit(g.screen,img,ball.c)
        if self.carry!=None:
            ball=self.carry
            img=self.ball_img(ball); x,y=g.pos; x-=self.mdx; y-=self.mdy
            utils.centre_blit(g.screen,self.shadow,(x+g.sy(.35),y+g.sy(1.1)))
            utils.centre_blit(g.screen,img,(x,y))
            if utils.mouse_on_img(self.light_img,self.light_xy):
                self.drop_ball('light')
            if utils.mouse_on_img(self.heavy_img,self.heavy_xy):
                self.drop_ball('heavy')
        if self.result!=None:
            utils.centre_blit(g.screen,self.result[0],self.result[1])

    def drop_ball(self,barrel):
        ball=self.carry
        ball.active=False; self.carry=None; success=False
        aim=3
        if g.level==1: aim=2
        if barrel=='heavy':
            cxy=self.smile_r
            if ball==self.rogue and self.heavy: success=True
        if barrel=='light':
            cxy=self.smile_l
            if ball==self.rogue and not self.heavy: success=True
        if success:
            if self.result==None:
                self.result=(self.smile,cxy)
                if self.count<=aim: g.scores[g.level-1]+=1
                else: self.result=(self.tick,cxy)
        else:
            self.result=(self.frown,cxy)
            self.show_rogue=True
        
    def ball_img(self,ball):
        img=self.blue
        if self.show_rogue and ball==self.rogue:
            if self.heavy: img=self.magenta
            else: img=self.white
        elif ball.colour=='green': img=self.green
        elif ball.colour=='red': img=self.red
        elif ball.colour=='gold': img=self.gold
        return img
    
    def draw_legend(self):
        g.screen.blit(self.legend,self.legend_xy)
        x,y=self.legend_xy
        x+=g.sy(2); y+=g.sy(.05)
        utils.text_blit1(g.screen,'3     6     9    12',\
                         g.font2,(x,y),utils.BLUE,False)
        y+=g.sy(1.25)
        utils.text_blit1(g.screen,'2     3     3     3',\
                         g.font2,(x,y),utils.BLACK,False)
        x=g.sx(14.2); y+=g.sy(1.75); dx=g.sy(1.77)
        for n in g.scores:
            utils.display_number(n,(x,y),g.font2,utils.ORANGE)
            x+=dx

    def click(self):
        if self.count==0: return False # no ball move till after first weigh
        tf=True
        if self.carry!=None:
            ball=self.carry; self.z.remove(ball); self.z.append(ball)
            x,y=g.pos; cx=x-self.mdx; cy=y-self.mdy
            ball.c=(cx,cy); self.into_pan(ball); self.carry=None
        else:
            ball=self.which()
            if ball!=None:
                cx,cy=ball.c; x,y=g.pos; self.mdx=x-cx; self.mdy=y-cy
                self.carry=ball; self.out_of_pan(ball)
            else:
                tf=False
        return tf

    def right_click(self):
        if self.count==0: return False # no ball move till after first weigh
        ball=self.carry
        if ball==None: ball=self.which()
        if ball !=None:
            rect=self.free_rect
            x=random.randint(rect.left,rect.left+rect.w)+g.sy(25.5)
            y=random.randint(rect.top,rect.top+rect.h)
            ball.c=(x,y)
            if ball.pan!=None: self.pan_n[ball.pan]-=1; ball.pan=None
            self.z.remove(ball); self.z.append(ball)
            self.carry=None; self.prev_carry=None
            
    def update(self):
        if self.flutter_k==None: return
        ms=pygame.time.get_ticks()
        if ms-self.ms>40:
            g.redraw=True
            self.flutter_ind+=1
            if self.flutter_ind==4: self.flutter_ind=0
            state=[0,2,1,2][self.flutter_ind]
            self.flutter_k+=1; self.state=state; self.set_state()
            if self.flutter_k>20:
                self.set_colours(self.state_save)
                if state==self.state_save:
                    self.flutter_k=None; return
            self.ms=pygame.time.get_ticks()

    def flutter_start(self):
        self.ms=pygame.time.get_ticks()
        self.flutter_k=0
        self.flutter_ind=0
        self.state_save=self.state
            
    def into_pan(self,ball):
        pan=self.over_pan(ball)
        if pan!=None:
            if self.pan_n[pan]<4:
                # find empty positions
                posn=[]
                for b in self.balls:
                    if b.active:
                        if b.pan==pan: posn.append(b.posn)
                for i in range(4):
                    if i not in posn:
                        ball.posn=i; self.pan_n[pan]+=1; ball.pan=pan
                        ball.c=self.pan_posns[pan][i]; ball.c0=ball.c
                        if i==0: # put to back
                            self.z.remove(ball); self.z=[ball]+self.z
                        if self.state==0: self.left_down()
                        elif self.state==1: self.left_up()
                        break
    
    def out_of_pan(self,ball):
        if ball.pan!=None:
            self.pan_n[ball.pan]-=1; ball.pan=None

    def over_pan(self,ball):
        cx,cy=ball.c
        for pan in range(2):
            x,y=self.pan_posns[pan][0]
            dx,dy=0,0
            if self.state<2:
                ind=self.state*2+pan
                dx,dy=self.dxy_ud[ind]
            rect=pygame.Rect(x+dx-g.sy(4),y+dy-g.sy(3),g.sy(8),g.sy(4.5))
            if rect.collidepoint(cx,cy): return pan
        return None
    
    def which(self):
        ln=len(self.z); b=None
        for ind in range(ln-1,-1,-1):
            ball=self.z[ind]
            if ball.active:
                if utils.mouse_on_img1(self.blue,ball.c):
                    if ball.pan!=None:
                        if self.pan_n[ball.pan]==4:
                            if ball.posn!=3: break # must be top in full pan
                    b=ball; break
        return b

    def set_state(self):
        if self.state==0: self.left_down()
        elif self.state==1: self.left_up()
        elif self.state==2: self.level()
        
    # ld, ru, lu, rd
    def left_down(self):
        self.state=0
        for ball in self.balls:
            if ball.active:
                x0,y0=ball.c0
                if ball.pan!=None:
                    dx,dy=self.dxy_ud[ball.pan]; x=x0+dx; y=y0+dy
                    ball.c=(x,y)
                    
    def left_up(self):
        self.state=1
        for ball in self.balls:
            if ball.active:
                x0,y0=ball.c0
                if ball.pan!=None:
                    dx,dy=self.dxy_ud[ball.pan+2]; x=x0+dx; y=y0+dy
                    ball.c=(x,y)

    def level(self):
        self.state=2
        for ball in self.balls:
            if ball.active:
                if ball.pan!=None: ball.c=ball.c0

    def weigh(self):
        self.count+=1
        l=self.pan_n[0]; r=self.pan_n[1]; done=False
        if l<r: self.left_up(); done=True
        elif l>r: self.left_down(); done=True
        else:
            for ball in self.balls:
                if ball==self.rogue:
                    if ball.pan==0:
                        if self.heavy: self.left_down()
                        else: self.left_up()
                        done=True
                    elif ball.pan==1:
                        if self.heavy: self.left_up()
                        else: self.left_down()
                        done=True
        if not done: self.level()
        self.flutter_start()

    def set_colours(self,state):
        if self.count==1 or not self.red_set:
            if state==0:
                for ball in self.balls:
                    if ball.colour=='blue':
                        if ball.pan==0: ball.colour='red'; self.red_set=True 
                        elif ball.pan==1: ball.colour='gold' 
                        else: ball.colour='green' 
            elif state==1:
                for ball in self.balls:
                    if ball.colour=='blue':
                        if ball.pan==0: ball.colour='gold' 
                        elif ball.pan==1: ball.colour='red'; self.red_set=True 
                        else: ball.colour='green' 
            else:
                for ball in self.balls:
                    if ball.pan!=None: ball.colour='green'


                    
        

