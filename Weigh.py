#!/usr/bin/python
# Weigh.py
"""
    Copyright (C) 2011  Peter Hewitt

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

"""
import g,pygame,utils,sys,load_save,buttons,slider
try:
    import gtk
except:
    pass
import wt

class Weigh:

    def __init__(self):
        self.journal=True # set to False if we come in via main()
        self.canvas=None # set to the pygame canvas if we come in via activity.py

    def display(self):
        g.screen.fill((255,255,192))
        buttons.draw()
        self.slider.draw()
        self.wt.draw()

    def do_click(self):
        self.wt.click()

    def do_button(self,bu):
        if bu=='yellow': self.wt.weigh()
        elif bu=='cyan': self.wt.setup()

    def do_key(self,key):
        if key==pygame.K_v: g.version_display=not g.version_display; return
        if key in g.SQUARE: self.do_button('cyan'); return
        if key in g.CIRCLE: self.do_button('yellow'); return
        if key in g.TICK: self.change_level(); return

    def change_level(self):
        g.level+=1
        if g.level>self.slider.steps: g.level=1
        self.wt.setup()

    def buttons_setup(self):
        buttons.Button('yellow',(g.sx(16.2),g.sy(18)))
        buttons.Button('cyan',(g.sx(24.5),g.sy(14)))

    def flush_queue(self):
        flushing=True
        while flushing:
            flushing=False
            if self.journal:
                while gtk.events_pending(): gtk.main_iteration()
            for event in pygame.event.get(): flushing=True

    def run(self):
        g.init()
        if not self.journal: utils.load()
        self.wt=wt.Wt()
        load_save.retrieve()
        self.wt.setup()
        self.buttons_setup()
        self.slider=slider.Slider(g.sx(16),g.sy(20.5),4,utils.GREEN)
        if self.canvas<>None: self.canvas.grab_focus()
        ctrl=False
        pygame.key.set_repeat(600,120); key_ms=pygame.time.get_ticks()
        going=True
        while going:
            if self.journal:
                # Pump GTK messages.
                while gtk.events_pending(): gtk.main_iteration()

            # Pump PyGame messages.
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    if not self.journal: utils.save()
                    going=False
                elif event.type == pygame.MOUSEMOTION:
                    g.pos=event.pos
                    g.redraw=True
                    if self.canvas<>None: self.canvas.grab_focus()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.redraw=True
                    if event.button==1:
                        if self.do_click():
                            pass
                        elif self.slider.mouse():
                            self.wt.setup() # level changed
                        else:
                            bu=buttons.check()
                            if bu!='': self.do_button(bu); self.flush_queue()
                    elif event.button==3:
                        self.wt.right_click()
                elif event.type == pygame.KEYDOWN:
                    # throttle keyboard repeat
                    if pygame.time.get_ticks()-key_ms>110:
                        key_ms=pygame.time.get_ticks()
                        if ctrl:
                            if event.key==pygame.K_q:
                                if not self.journal: utils.save()
                                going=False; break
                            else:
                                ctrl=False
                        if event.key in (pygame.K_LCTRL,pygame.K_RCTRL):
                            ctrl=True; break
                        self.do_key(event.key); g.redraw=True
                        self.flush_queue()
                elif event.type == pygame.KEYUP:
                    ctrl=False
            if not going: break
            self.wt.update()
            if g.redraw:
                self.display()
                if g.version_display: utils.version_display()
                g.screen.blit(g.pointer,g.pos)
                pygame.display.flip()
                g.redraw=False
            g.clock.tick(40)

if __name__=="__main__":
    pygame.init()
    pygame.display.set_mode((1024,768),pygame.FULLSCREEN)
    game=Weigh()
    game.journal=False
    game.run()
    pygame.display.quit()
    pygame.quit()
    sys.exit(0)
