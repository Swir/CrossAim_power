import sys, os, json, math, colorsys, ctypes
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QRect, Signal, QSize
from PySide6.QtGui import QColor, QPainter, QPen, QIcon
from PySide6.QtWidgets import (QApplication,QWidget,QMainWindow,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QPushButton,QComboBox,QSlider,QSpinBox,QCheckBox,QGroupBox)

try:
    import mss
except ImportError:
    mss = None

APP_NAME = "CrossAim Power"
APP_VERSION = "1.0.0"
user32 = ctypes.windll.user32
GWL_EXSTYLE=-20; WS_EX_LAYERED=0x80000; WS_EX_TRANSPARENT=0x20; WS_EX_TOOLWINDOW=0x80; WS_EX_NOACTIVATE=0x08000000
VK_RBUTTON=0x02; VK_F8=0x77; WDA_EXCLUDEFROMCAPTURE=0x11

def key_down(vk): return bool(user32.GetAsyncKeyState(vk) & 0x8000)
def appdir():
    p=Path(os.getenv("APPDATA",Path.home()))/"CrossAim_Power"; p.mkdir(parents=True,exist_ok=True); return p

def blank(): return [[0]*32 for _ in range(32)]
def shape(name):
    m=blank(); c=15.5
    if name=="Dot":
        for y in range(14,18):
            for x in range(14,18):
                if (x-c)**2+(y-c)**2<=3.3: m[y][x]=255
    elif name in ("Cross","Cross + Dot"):
        for i in range(8,24):
            if i not in (14,15,16,17): m[15][i]=m[16][i]=m[i][15]=m[i][16]=255
        if name.endswith("Dot"): m[15][15]=m[15][16]=m[16][15]=m[16][16]=255
    elif name in ("Circle","Circle + Dot"):
        for y in range(32):
            for x in range(32):
                if abs(math.hypot(x-c,y-c)-7.5)<.85: m[y][x]=255
        if name.endswith("Dot"): m[15][15]=m[15][16]=m[16][15]=m[16][16]=255
    elif name=="Tiny Ring":
        for y in range(32):
            for x in range(32):
                if abs(math.hypot(x-c,y-c)-4.5)<.8: m[y][x]=255
    return m

class PixelEditor(QWidget):
    changed=Signal()
    def __init__(self):
        super().__init__(); self.setMinimumSize(350,350); self.matrix=shape("Cross + Dot"); self.painting=False; self.erase=False
    def sizeHint(self): return QSize(400,400)
    def set_matrix(self,m): self.matrix=[r[:] for r in m]; self.update(); self.changed.emit()
    def cell(self,pos):
        side=min(self.width(),self.height()); ox=(self.width()-side)/2; oy=(self.height()-side)/2; cs=side/32
        x=int((pos.x()-ox)/cs); y=int((pos.y()-oy)/cs)
        return (x,y) if 0<=x<32 and 0<=y<32 else None
    def apply(self,pos):
        c=self.cell(pos)
        if c:
            x,y=c; self.matrix[y][x]=0 if self.erase else 255; self.update(); self.changed.emit()
    def mousePressEvent(self,e):
        if e.button() in (Qt.LeftButton,Qt.RightButton): self.painting=True; self.erase=e.button()==Qt.RightButton; self.apply(e.position())
    def mouseMoveEvent(self,e):
        if self.painting: self.apply(e.position())
    def mouseReleaseEvent(self,e): self.painting=False
    def paintEvent(self,e):
        p=QPainter(self); side=min(self.width(),self.height()); ox=(self.width()-side)/2; oy=(self.height()-side)/2; cs=side/32
        p.fillRect(self.rect(),QColor("#111722"))
        for y in range(32):
            for x in range(32):
                if self.matrix[y][x]: p.fillRect(QRect(int(ox+x*cs),int(oy+y*cs),max(1,int(cs+1)),max(1,int(cs+1))),QColor("#58d6ff"))
        p.setPen(QPen(QColor("#2d3b52"),1))
        for i in range(33):
            a=int(ox+i*cs); b=int(oy+i*cs); p.drawLine(a,int(oy),a,int(oy+side)); p.drawLine(int(ox),b,int(ox+side),b)

class Overlay(QWidget):
    def __init__(self):
        super().__init__(None); self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool|Qt.WindowTransparentForInput|Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TranslucentBackground,True); self.setAttribute(Qt.WA_ShowWithoutActivating,True); self.resize(320,320)
        self.matrix=shape("Cross + Dot"); self.pixel=2; self.alpha=100; self.color=QColor("white"); self.outline=True; self.offset_x=0; self.offset_y=0
    def showEvent(self,e):
        super().showEvent(e)
        try:
            h=int(self.winId()); ex=user32.GetWindowLongW(h,GWL_EXSTYLE); user32.SetWindowLongW(h,GWL_EXSTYLE,ex|WS_EX_LAYERED|WS_EX_TRANSPARENT|WS_EX_TOOLWINDOW|WS_EX_NOACTIVATE); user32.SetWindowDisplayAffinity(h,WDA_EXCLUDEFROMCAPTURE)
        except: pass
    def center(self): return self.x()+self.width()//2,self.y()+self.height()//2
    def reposition(self):
        g=QApplication.primaryScreen().geometry(); self.move(g.x()+g.width()//2+self.offset_x-self.width()//2,g.y()+g.height()//2+self.offset_y-self.height()//2)
    def paintEvent(self,e):
        p=QPainter(self); ps=self.pixel; total=32*ps; sx=(self.width()-total)//2; sy=(self.height()-total)//2; occupied={(x,y) for y in range(32) for x in range(32) if self.matrix[y][x]}
        if self.outline:
            border=set()
            for x,y in occupied:
                for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
                    q=(x+dx,y+dy)
                    if 0<=q[0]<32 and 0<=q[1]<32 and q not in occupied: border.add(q)
            oc=QColor("#000" if self.color.lightness()>128 else "#fff"); oc.setAlpha(int(230*self.alpha/100)); p.setPen(Qt.NoPen); p.setBrush(oc)
            for x,y in border: p.drawRect(sx+x*ps,sy+y*ps,ps,ps)
        p.setPen(Qt.NoPen)
        for y in range(32):
            for x in range(32):
                a=self.matrix[y][x]
                if a:
                    c=QColor(self.color); c.setAlpha(int(a*self.alpha/100)); p.setBrush(c); p.drawRect(sx+x*ps,sy+y*ps,ps,ps)

class Main(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle(f"{APP_NAME} {APP_VERSION}"); self.resize(930,700)
        icon=Path(__file__).with_name("crossaim_power.png")
        if icon.exists(): self.setWindowIcon(QIcon(str(icon)))
        self.ov=Overlay(); self.enabled=True; self.hidden_rmb=False; self.prev_f8=False; self.last_color=None; self.sct=mss.mss() if mss else None
        self.settings=appdir()/"settings.json"; self.build_ui(); self.load(); self.ov.reposition(); self.ov.show()
        self.keys=QTimer(self); self.keys.timeout.connect(self.tick_keys); self.keys.start(16)
        self.adapt=QTimer(self); self.adapt.timeout.connect(self.tick_color); self.adapt.start(35)
    def build_ui(self):
        root=QWidget(); self.setCentralWidget(root); lay=QHBoxLayout(root); left=QVBoxLayout(); right=QVBoxLayout(); lay.addLayout(left,0); lay.addLayout(right,1)
        t=QLabel("CROSSAIM POWER"); t.setObjectName("title"); left.addWidget(t); left.addWidget(QLabel("Adaptive multi-zone gaming reticle"))
        g=QGroupBox("Reticle"); q=QGridLayout(g); self.shapes=QComboBox(); self.shapes.addItems(["Dot","Cross","Cross + Dot","Circle","Circle + Dot","Tiny Ring","Custom"]); self.shapes.setCurrentText("Cross + Dot"); self.shapes.currentTextChanged.connect(self.pick_shape)
        self.scale=QSpinBox(); self.scale.setRange(1,7); self.scale.setValue(2); self.opacity=QSlider(Qt.Horizontal); self.opacity.setRange(20,100); self.opacity.setValue(100); self.outline=QCheckBox("Auto contrast outline"); self.outline.setChecked(True)
        self.scale.valueChanged.connect(self.sync); self.opacity.valueChanged.connect(self.sync); self.outline.toggled.connect(self.sync)
        q.addWidget(QLabel("Shape"),0,0); q.addWidget(self.shapes,0,1); q.addWidget(QLabel("Scale"),1,0); q.addWidget(self.scale,1,1); q.addWidget(QLabel("Opacity"),2,0); q.addWidget(self.opacity,2,1); q.addWidget(self.outline,3,0,1,2); left.addWidget(g)
        c=QGroupBox("Adaptive color"); cg=QGridLayout(c); self.mode=QComboBox(); self.mode.addItems(["Power Smart Contrast","Adaptive Complement","Adaptive B/W","Fixed White","Fixed Green","Fixed Magenta"]); self.sample=QSpinBox(); self.sample.setRange(9,61); self.sample.setSingleStep(2); self.sample.setValue(21); self.smooth=QSlider(Qt.Horizontal); self.smooth.setRange(0,90); self.smooth.setValue(50); self.status=QLabel("Waiting for pixels…")
        cg.addWidget(QLabel("Mode"),0,0); cg.addWidget(self.mode,0,1); cg.addWidget(QLabel("Sample area"),1,0); cg.addWidget(self.sample,1,1); cg.addWidget(QLabel("Anti-flicker"),2,0); cg.addWidget(self.smooth,2,1); cg.addWidget(self.status,3,0,1,2); left.addWidget(c)
        h=QGroupBox("Controls"); hg=QVBoxLayout(h); self.rmb=QCheckBox("Hide while RMB is held"); self.rmb.setChecked(True); hg.addWidget(self.rmb); hg.addWidget(QLabel("F8 = show/hide overlay")); left.addWidget(h); left.addStretch()
        right.addWidget(QLabel("32 × 32 RETICLE EDITOR")); self.editor=PixelEditor(); self.editor.changed.connect(self.editor_changed); right.addWidget(self.editor,1); row=QHBoxLayout(); clear=QPushButton("Clear"); clear.clicked.connect(lambda:self.editor.set_matrix(blank())); save=QPushButton("Save settings"); save.clicked.connect(self.save); toggle=QPushButton("Show / Hide [F8]"); toggle.clicked.connect(self.toggle); row.addWidget(clear); row.addWidget(save); row.addWidget(toggle); right.addLayout(row)
        self.setStyleSheet('QMainWindow,QWidget{background:#090e17;color:#e7eef8;font-family:Segoe UI;font-size:10pt} QLabel#title{font-size:20pt;font-weight:800;color:#62dcff} QGroupBox{border:1px solid #27344a;border-radius:9px;margin-top:12px;padding-top:12px;color:#9ce8ff;font-weight:700} QPushButton,QComboBox,QSpinBox{background:#121c2c;border:1px solid #334660;border-radius:6px;padding:6px} QPushButton:hover{border-color:#5bd8ff} QSlider::groove:horizontal{height:5px;background:#253149} QSlider::handle:horizontal{background:#5bd8ff;width:14px;margin:-5px 0;border-radius:7px}')
    def pick_shape(self,n):
        if n!="Custom": self.editor.set_matrix(shape(n))
    def editor_changed(self):
        self.shapes.blockSignals(True); self.shapes.setCurrentText("Custom"); self.shapes.blockSignals(False); self.sync()
    def sync(self): self.ov.matrix=[r[:] for r in self.editor.matrix]; self.ov.pixel=self.scale.value(); self.ov.alpha=self.opacity.value(); self.ov.outline=self.outline.isChecked(); self.ov.update()
    def toggle(self):
        self.enabled=not self.enabled
        if self.enabled: self.ov.show(); self.ov.reposition()
        else: self.ov.hide()
    def tick_keys(self):
        f8=key_down(VK_F8)
        if f8 and not self.prev_f8: self.toggle()
        self.prev_f8=f8
        if self.enabled and self.rmb.isChecked():
            down=key_down(VK_RBUTTON)
            if down and not self.hidden_rmb: self.ov.hide(); self.hidden_rmb=True
            elif not down and self.hidden_rmb: self.ov.show(); self.ov.reposition(); self.hidden_rmb=False
    @staticmethod
    def lum(rgb):
        def f(v): v=v/255; return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
        r,g,b=rgb; return .2126*f(r)+.7152*f(g)+.0722*f(b)
    @classmethod
    def ratio(cls,a,b):
        x,y=cls.lum(a),cls.lum(b); return (max(x,y)+.05)/(min(x,y)+.05)
    def zones(self,raw,n):
        cx=n//2; skip=max(2,n//8); z=[[],[],[],[],[]]; i=0
        for y in range(n):
            for x in range(n):
                b,g,r,_=raw[i:i+4]; i+=4
                if abs(x-cx)<=skip and abs(y-cx)<=skip: continue
                p=(r,g,b); z[4].append(p); z[(0 if y<cx else 2)+(0 if x<cx else 1)].append(p)
        out=[]
        for a in z:
            if a:
                rs=sorted(p[0] for p in a); gs=sorted(p[1] for p in a); bs=sorted(p[2] for p in a); k=len(a)//2; out.append((rs[k],gs[k],bs[k]))
        return out
    def complement(self,bg):
        r,g,b=(v/255 for v in bg); h,s,v=colorsys.rgb_to_hsv(r,g,b)
        if s<.12: return (255,255,255) if self.lum(bg)<.3 else (0,0,0)
        r,g,b=colorsys.hsv_to_rgb((h+.5)%1,max(.92,s),1); return (int(r*255),int(g*255),int(b*255))
    def smart(self,z,bg):
        cand=[(255,255,255),(0,0,0),self.complement(bg),(0,255,255),(255,0,255),(255,255,0),(0,255,96),(255,96,0),(0,160,255)]
        def score(c):
            rs=[self.ratio(c,x) for x in z]; return min(rs)*.72+(sum(rs)/len(rs))*.28
        ranked=sorted(((score(c),c) for c in cand),reverse=True); bests,best=ranked[0]
        if self.last_color:
            old=score(self.last_color); h=.08+self.smooth.value()/100*.18
            if old>=bests*(1-h): best=self.last_color
        self.last_color=best; return best
    def tick_color(self):
        if not self.enabled or self.hidden_rmb or not self.sct: return
        mode=self.mode.currentText()
        if mode.startswith("Fixed"):
            self.ov.color=QColor({"Fixed White":"white","Fixed Green":"#00ff80","Fixed Magenta":"#ff00ff"}[mode]); self.ov.update(); return
        try:
            n=self.sample.value()|1; x,y=self.ov.center(); shot=self.sct.grab({"left":x-n//2,"top":y-n//2,"width":n,"height":n}); z=self.zones(shot.raw,n)
            if not z: return
            bg=z[-1]
            if mode=="Power Smart Contrast": out=self.smart(z,bg)
            elif mode=="Adaptive Complement": out=self.complement(bg)
            else: out=(255,255,255) if self.lum(bg)<.3 else (0,0,0)
            self.ov.color=QColor(*out); self.ov.update(); worst=min(self.ratio(out,a) for a in z); self.status.setText(f"BG #{bg[0]:02X}{bg[1]:02X}{bg[2]:02X} → AIM {self.ov.color.name().upper()} • {worst:.1f}:1")
        except Exception as e: self.status.setText(f"Pixel sample error: {e}")
    def save(self):
        data={"matrix":self.editor.matrix,"scale":self.scale.value(),"opacity":self.opacity.value(),"outline":self.outline.isChecked(),"mode":self.mode.currentText(),"sample":self.sample.value(),"smooth":self.smooth.value(),"rmb":self.rmb.isChecked()}; self.settings.write_text(json.dumps(data),encoding="utf-8")
    def load(self):
        try:
            d=json.loads(self.settings.read_text(encoding="utf-8")); self.editor.matrix=d.get("matrix",self.editor.matrix); self.scale.setValue(d.get("scale",2)); self.opacity.setValue(d.get("opacity",100)); self.outline.setChecked(d.get("outline",True)); self.mode.setCurrentText(d.get("mode","Power Smart Contrast")); self.sample.setValue(d.get("sample",21)); self.smooth.setValue(d.get("smooth",50)); self.rmb.setChecked(d.get("rmb",True)); self.sync()
        except: self.sync()
    def closeEvent(self,e):
        self.save(); self.ov.close()
        if self.sct: self.sct.close()
        e.accept()

def main():
    if sys.platform!="win32": print("CrossAim Power requires Windows 10/11."); return 1
    try: ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except: pass
    app=QApplication(sys.argv); app.setApplicationName(APP_NAME); icon=Path(__file__).with_name("crossaim_power.png")
    if icon.exists(): app.setWindowIcon(QIcon(str(icon)))
    w=Main(); w.show(); return app.exec()

if __name__=="__main__": raise SystemExit(main())
