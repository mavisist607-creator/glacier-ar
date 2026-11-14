import os, json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from matplotlib.patches import Rectangle, Circle, Arc, FancyArrowPatch, FancyBboxPatch
import trimesh
from PIL import Image
from matplotlib import colors

OUT=os.path.dirname(__file__)
NX,NY=221,125
xs=np.linspace(0,1,NX)
ys=np.linspace(-.5,.5,NY)
X,Y=np.meshgrid(xs,ys)

def gaussian(cx,cy,sx,sy,amp): return amp*np.exp(-.5*((X-cx)/sx)**2-.5*((Y-cy)/sy)**2)

def ridge(cx1,cy1,cx2,cy2,amp,width):
  dx,dy=cx2-cx1,cy2-cy1
  t=((X-cx1)*dx+(Y-cy1)*dy)/(dx*dx+dy*dy)
  tc=np.clip(t,0,1)
  d=np.hypot(X-(cx1+dx*tc),Y-(cy1+dy*tc))
  return amp*np.exp(-.5*(d/width)**2)*np.exp(-.5*((t-.5)/.56)**6)

# 山區高程東向遞減，從冰蝕區接續到冰磧、融冰水與風積區
Z=100+1520*np.clip(1-X/.72,0,1)**2.35
Z+=gaussian(.18,-.38,.17,.14,350)+gaussian(.14,.39,.20,.14,450)
Z+=gaussian(.28,-.36,.15,.12,245)+gaussian(.28,.35,.16,.13,320)
# 高山稜脊與角峰
Z+=ridge(.11,.06,.23,.44,330,.021)
Z+=ridge(.11,.06,.23,-.40,270,.019)
Z+=ridge(.11,.06,.01,-.25,170,.022)
Z+=gaussian(.105,.06,.031,.053,530)
# 冰斗的凹地與後壁凹弧
for cx,cy in ((.205,-.265),(.195,.275)):
  r=np.sqrt(((X-cx)/.085)**2+((Y-cy)/.125)**2)
  Z-=320*np.exp(-.5*(r/.83)**4)
  Z+=105*np.exp(-.5*((r-1.17)/.18)**2)
# U型谷：中段寬平谷底與陡峭谷壁，並保留端磧區
cy0=.014+.038*np.sin(11*X)
transition=(1/(1+np.exp(np.clip((np.abs(Y-cy0)-.115)/.016,-65,65))))
xweight=(1/(1+np.exp(np.clip((X-.45)/.035,-65,65))))*(1/(1+np.exp(np.clip((.13-X)/.035,-65,65))))
valleyFloor=95+920*np.clip(1-X/.72,0,1)**2.1-100
Z=Z*(1-transition*xweight)+(valleyFloor)*(transition*xweight)
# 羊背石：谷地基岩丘，迎冰面較緩而背冰面陡，教學地形示意
Z+=gaussian(.36,.055,.050,.026,52)
# 冰河堆積：鼓丘（長軸與冰流方向平行）
for cx,cy,sx,sy,amp in [(.435,.23,.044,.018,80),(.476,-.255,.049,.023,66),(.485,.34,.040,.022,60)]:
  Z+=gaussian(cx,cy,sx,sy,amp)
# 側磧：冰河谷兩側狹長堆積脊
for sign in [-1,1]:
  pY=sign*(.145+.015*np.sin(17*X))
  Z+=45*np.exp(-.5*((Y-pY)/.013)**2)*np.exp(-.5*((X-.405)/.094)**6)
# 端磧：冰舌末端的弧形脊，較寬以供等高線辨認
arcX=.515+.045*(1-(Y/.40)**2)
Z+=106*np.exp(-.5*((X-arcX)/.016)**2)*np.exp(-.5*(Y/.335)**8)
# 蛇丘：冰內/冰底融水所堆積狹長曲線狀地形，位於冰緣附近
eskerY=.20+.056*np.sin((X-.47)*27)
Z+=65*np.exp(-.5*((Y-eskerY)/.011)**2)*np.exp(-.5*((X-.565)/.095)**6)
# 冰水沖積平原：辮狀河道形成淺槽，周圍低起伏
for offset,amp in [(-.15,28),(-.065,19),(.035,16)]:
  cy=offset+.048*np.sin((X-.57)*29+offset*13)
  lengthweight=np.exp(-.5*((X-.705)/.105)**6)
  Z-=amp*np.exp(-.5*((Y-cy)/.012)**2)*lengthweight
# 橫向下風處的風積沙丘（示意）
for cx,cy in [(0.865,-.23),(.910,.11),(.964,-.07),(.92,.34)]:
  Z+=gaussian(cx,cy,.018,.085,82)
# 細微地表起伏
Z+=5*np.sin(11*Y+2*X)*np.sin(19*X-4*Y)
Z=gaussian_filter(Z,.7)
Z=np.maximum(Z,25)
print('height range',float(Z.min()),float(Z.max()))

PAGE_W=297;PAGE_H=210
MAP_X=13;MAP_Y=40;MAP_W=271;MAP_H=139
# map domain x0..1 y[-.5,.5], render reversed physical y
T=lambda xx,yy:(MAP_X+xx*MAP_W, MAP_Y+(.5-yy)*MAP_H)

# Feature anchors, model coordinates derived from the same DEM; a few are interpreted not diagnostic from topo alone
features=[
 dict(id=1,name='角峰',process='冰蝕',x=.105,y=.06,color='#ad464b'),
 dict(id=2,name='刃嶺',process='冰蝕',x=.166,y=.238,color='#ad464b'),
 dict(id=3,name='冰斗',process='冰蝕',x=.202,y=-.255,color='#ad464b'),
 dict(id=4,name='冰槽（U形谷）',process='冰蝕',x=.33,y=.01,color='#ad464b'),
 dict(id=5,name='鼓丘',process='冰磧',x=.435,y=.23,color='#497e60'),
 dict(id=10,name='羊背石',process='冰蝕（基岩丘）',x=.36,y=.055,color='#ad464b'),
 dict(id=6,name='端磧',process='冰磧',x=.56,y=-.02,color='#497e60'),
 dict(id=7,name='蛇丘',process='冰水沉積（冰下／冰內）',x=.59,y=.20,color='#277ba5'),
 dict(id=8,name='冰水沖積平原',process='冰水沉積',x=.72,y=-.31,color='#277ba5'),
 dict(id=9,name='風積沙丘',process='風積',x=.91,y=.12,color='#b27c37'),
]

features.sort(key=lambda f: f['id'])

def interp(x,y):
  i=int(round(x*(NX-1)));j=int(round((y+.5)*(NY-1)))
  return float(Z[np.clip(j,0,NY-1),np.clip(i,0,NX-1)])
minz=float(np.min(Z));maxz=float(np.max(Z));
for f in features:
  px,py=T(f['x'],f['y']); f['page_x_mm']=round(px,3);f['page_y_mm']=round(py,3)
  f['ar_x']=round((px-PAGE_W/2)/PAGE_W,6); f['ar_y']=round((PAGE_H/2-py)/PAGE_W,6)
  f['ar_z']=round(0.007+0.20*(interp(f['x'],f['y'])-minz)/(maxz-minz)+.011,6)

# contour vector paths based on same grid used for 3D mesh
xmm=MAP_X+X*MAP_W
y_mm=MAP_Y+(.5-Y)*MAP_H
levels=np.arange(0,2300,40)
from matplotlib.figure import Figure
fig0=Figure()
ax0=fig0.add_subplot(111)
cont=ax0.contour(xmm,y_mm,Z,levels=levels)
segments=[]
for level,slist in zip(cont.levels, cont.allsegs):
 for path in slist:
  if len(path)>=3:
   segments.append((int(level),path))
plt.close(fig0)

# font fallback: Noto CJK fonts installed?
plt.rcParams['font.sans-serif']=['Noto Sans CJK JP','DejaVu Sans']
plt.rcParams['axes.unicode_minus']=False

def mmfig():
  fig=plt.figure(figsize=(PAGE_W/25.4,PAGE_H/25.4),dpi=220,facecolor='white')
  ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,PAGE_W);ax.set_ylim(PAGE_H,0);ax.set_aspect('equal');ax.axis('off')
  return fig,ax

def draw_base(teacher=False):
 fig,ax=mmfig()
 ax.add_patch(Rectangle((0,0),PAGE_W,PAGE_H,facecolor='#fffefb',edgecolor='none'))
 # upper heading
 ax.text(13,15,'冰河地景探究｜等高線與 AR',size=17.5,weight='bold',color='#193748',va='center')
 ax.text(13,25.5,'從高山冰蝕 → 冰緣堆積 → 融冰水搬運 → 下風處風積',size=8.8,color='#42606a',va='center')
 ax.text(283,15,'LANDSCAPE   01',size=8.1,ha='right',weight='bold',color='#344f5d')
 ax.text(283,25.5,'A4  橫式｜教學示意｜等高距 40 m',size=7.8,ha='right',color='#42606a')
 # top four-zone process strip outside the map
 zone_edges=[0,.39,.59,.82,1]
 for i,(a,b,lab,col) in enumerate(zip(zone_edges[:-1],zone_edges[1:], ['A  冰蝕作用','B  冰河堆積','C  冰水作用','D  風積作用'],['#dce9ee','#d9e8dd','#dfecf0','#f0e7cf'])):
  px=MAP_X+a*MAP_W; pw=(b-a)*MAP_W
  ax.add_patch(Rectangle((px,32.5),pw,5,facecolor=col,edgecolor='#fdfbf4',linewidth=.5))
  ax.text(px+pw/2,35.2,lab,fontsize=7.2,ha='center',va='center',color='#304c57',weight='medium')
 # main map and contours
 ax.add_patch(Rectangle((MAP_X,MAP_Y),MAP_W,MAP_H,facecolor='#fdfcf8',edgecolor='#536977',lw=.7))
 for lvl,path in segments:
  isIndex=(lvl%200==0)
  ax.plot(path[:,0],path[:,1],color=('#55656c' if not isIndex else '#253d4b'),lw=(.24 if not isIndex else .48),alpha=.9,solid_joinstyle='round')
 # small non-constant corner mark patterns for feature tracking, outside central map interior
 for i,(ix,iy) in enumerate([(15,42),(270,42),(15,169),(270,169)]):
  ax.add_patch(Rectangle((ix,iy),11,8,facecolor='#fffef8',edgecolor='#173f53',linewidth=0.85))
  for j in range(3+i):
   ax.plot([ix+1.5+(j*2.1)%8,ix+1.5+(j*2.1)%8],[iy+1,iy+2.5+((j+i)%3)*1.1],color='#173f53',lw=.75)
  ax.text(ix+8.5,iy+6.7,'X'+str(i+1),ha='right',fontsize=4.3,color='#173f53')
 # guide arrows in the margins
 ax.annotate('冰流方向',xy=(MAP_X+.46*MAP_W,MAP_Y+.53*MAP_H),xytext=(MAP_X+.38*MAP_W,MAP_Y+.53*MAP_H),fontsize=7.3,color='#175c88',ha='right',va='center',arrowprops=dict(arrowstyle='->',color='#175c88',lw=1.1))
 ax.annotate('融冰水',xy=(MAP_X+.75*MAP_W,MAP_Y+.82*MAP_H),xytext=(MAP_X+.66*MAP_W,MAP_Y+.82*MAP_H),fontsize=6.8,color='#2377a5',ha='right',va='center',arrowprops=dict(arrowstyle='->',color='#2377a5',lw=1))
 ax.annotate('盛行風',xy=(MAP_X+.925*MAP_W,MAP_Y+.16*MAP_H),xytext=(MAP_X+.83*MAP_W,MAP_Y+.16*MAP_H),fontsize=6.8,color='#8a6d38',ha='right',va='center',arrowprops=dict(arrowstyle='->',color='#8a6d38',lw=1))
 # footer strips
 ax.text(13,189,'學生任務',fontsize=9,weight='bold',color='#274a5a')
 ax.text(13,197,'① 先從等高線圈選地形  ② AR 立體驗證  ③ 解釋地形形成作用',fontsize=7.7,color='#314d5d')
 ax.text(283,190,'地形高程為合成資料；非真實地圖',fontsize=7.6,color='#56717a',ha='right')
 ax.text(283,198,'等高線與 3D 模型共用同一數值地形',fontsize=7.6,color='#56717a',ha='right')
 if teacher:
  for f in features:
   px,py=f['page_x_mm'],f['page_y_mm']
   ax.add_patch(Circle((px,py),radius=2.1,facecolor=f['color'],edgecolor='white',lw=.7,zorder=30))
   ax.text(px,py-.1,str(f['id']),fontsize=6.5,color='white',weight='bold',ha='center',va='center',zorder=31)
  ax.text(14,207,'教師參考：編號與名稱請對照 teacher-key.txt；不是學生版 AR 辨識圖片',fontsize=6.2,color='#9c5139')
 else:
  ax.text(14,207,'作答：紅色＝冰蝕｜綠色＝冰磧｜藍色＝冰水｜橘色＝風積（請避開四角定位記號）',fontsize=7,color='#4b5f67')
 return fig,ax

for teacher in [False,True]:
 f,ax=draw_base(teacher)
 fname='sheet-teacher.png' if teacher else 'sheet-student.png'
 f.savefig(os.path.join(OUT,fname),dpi=240,facecolor='white',pad_inches=0)
 plt.close(f)
 print(fname)

# vertex positions: MindAR full-image target is normalized to physical A4 page width = 1
xyz=[];rgb=[]
for j in range(NY):
 for i in range(NX):
  xpage=MAP_X+xs[i]*MAP_W;ypage=MAP_Y+(.5-ys[j])*MAP_H
  z=float(Z[j,i]); base=(z-minz)/(maxz-minz)
  # AR image is landscape target, x horizontal and y vertical with center at 0,0
  xyz.append([(xpage-PAGE_W/2)/PAGE_W,(PAGE_H/2-ypage)/PAGE_W,.007+.20*base])
  # subtle zone differentiation and elevation shading
  if xs[i]<.39: c=np.array([117,137,146.])
  elif xs[i]<.59: c=np.array([147,164,134.])
  elif xs[i]<.82: c=np.array([154,172,158.])
  else: c=np.array([198,176,131.])
  c=c*.88+np.array([230,232,228])*base*.12
  rgb.append([*np.uint8(np.clip(c,0,255)),255])
faces=[]
for j in range(NY-1):
 for i in range(NX-1):
  p=j*NX+i; q=p+NX
  # compare directions: in index j+1 increases y scene coordinate, so right x up y gives +z
  faces.append([p,p+1,q]);faces.append([p+1,q+1,q])
mesh=trimesh.Trimesh(vertices=np.array(xyz),faces=np.array(faces),process=False)
mesh.visual.vertex_colors=np.array(rgb,dtype=np.uint8)
mesh.export(os.path.join(OUT,'terrain.glb'))
print('GLB',os.stat(os.path.join(OUT,'terrain.glb')).st_size)
with open(os.path.join(OUT,'features.json'),'w',encoding='utf-8') as ff:json.dump(features,ff,ensure_ascii=False,indent=2)
with open(os.path.join(OUT,'teacher-key.txt'),'w',encoding='utf-8') as f:
 f.write('冰河地景｜教師參考答案\n\n')
 for p in features:f.write(f"{p['id']:>2}  {p['name']} [{p['process']}]  地圖座標 x={p['x']:.3f}, y={p['y']:.3f}\n")
 f.write('\n注意：本圖為自製合成示意高程；不能由等高線單獨證明沉積物成因。\n蛇丘由冰體內或冰底融冰水沉積形成，不應一概置於冰河末端下游。\n風積區位於下風處，不等於河川下游。\n')

# create preview of student and teacher with smaller images
for fn in ['sheet-student.png','sheet-teacher.png']:
 img=Image.open(os.path.join(OUT,fn));img.thumbnail((1350,980));img.save(os.path.join(OUT,fn.replace('.png','-preview.png')))
