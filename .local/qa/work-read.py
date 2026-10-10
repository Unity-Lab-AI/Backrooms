"""Read the Work tab grid: prints a value per cell (1-4, 0 blank). Classify digit colour:
green=1, bright yellow=2, tan=3, white/grey=4. Usage: python .local/qa/work-read.py [png]"""
import sys, glob, os
from PIL import Image
COLS=[273,305,336,367,398,429,459,490,521,552,583,614,644,675,706,737,768,798,829,860,890,921,952,983,1014,1045,1076,1106,1137,1168,1199,1230,1261,1292,1323]
import os as _os
N=int(_os.environ.get('WORK_ROWS','6'))
ROWS=[764-25*(N-1-i) for i in range(N)]   # last row sits at 764; rows are 25 apart
def read(path):
    im=Image.open(path).convert('RGB'); grid=[]
    for y in ROWS:
        row=[]
        for x in COLS:
            px=[p for p in im.crop((x-4,y-8,x+3,y+7)).getdata() if max(p)>120]
            if len(px)<6: row.append(0); continue
            r=sum(p[0] for p in px)/len(px); g=sum(p[1] for p in px)/len(px); b=sum(p[2] for p in px)/len(px)
            if g>r+30: row.append(1)
            elif r-b>35: row.append(2 if g>163 else 3)   # yellow 2 ~(193,175,103), tan 3 ~(170,150,109)
            else: row.append(4)
        grid.append(row)
    return grid
if __name__=='__main__':
    p=sys.argv[1] if len(sys.argv)>1 else max(glob.glob('.local/qa/evidence/eyes/RRQA-eyes-*.png'),key=os.path.getmtime)
    for y,row in zip(ROWS,read(p)): print(y,' '.join(str(v) for v in row))
