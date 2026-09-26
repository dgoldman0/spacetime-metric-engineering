import sympy as sp
s,z,r,ph=sp.symbols('sigma z r phi',real=True)
X=[s,z,r,ph]
al=sp.Function('alpha',positive=True)(s,z,r)
be=sp.Function('beta')(s,z,r)
g=sp.zeros(4)
g[0,0]=-al**2+be**2; g[0,1]=g[1,0]=be; g[1,1]=1; g[2,2]=1; g[3,3]=r**2
gi=sp.simplify(g.inv())
def Gamma(a,b,c):
    return sum(gi[a,d]*(sp.diff(g[d,b],X[c])+sp.diff(g[d,c],X[b])-sp.diff(g[b,c],X[d])) for d in range(4))/2
Gam=[[[sp.simplify(Gamma(a,b,c)) for c in range(4)] for b in range(4)] for a in range(4)]
def Ric(b,c):
    e=0
    for a in range(4):
        e+=sp.diff(Gam[a][b][c],X[a])-sp.diff(Gam[a][b][a],X[c])
        for d in range(4):
            e+=Gam[a][a][d]*Gam[d][b][c]-Gam[a][c][d]*Gam[d][b][a]
    return e
R=sp.zeros(4)
for b in range(4):
    for c in range(b,4):
        R[b,c]=R[c,b]=sp.simplify(Ric(b,c))
Rs=sp.simplify(sum(gi[a,b]*R[a,b] for a in range(4) for b in range(4)))
G=R-Rs*g/2
# orthonormal frame vectors (contravariant)
n=sp.Matrix([1/al,-be/al,0,0]); ez=sp.Matrix([0,1,0,0]); er=sp.Matrix([0,0,1,0]); ep=sp.Matrix([0,0,0,1/r])
E=[n,ez,er,ep]
T=sp.zeros(4)
for i in range(4):
    for j in range(i,4):
        T[i,j]=T[j,i]=sp.simplify((E[i].T*G*E[j])[0]/(8*sp.pi))
names=['n','z','r','phi']
for i in range(4):
    for j in range(i,4):
        print(f"8pi T_{names[i]}{names[j]} =", sp.simplify(8*sp.pi*T[i,j]))
