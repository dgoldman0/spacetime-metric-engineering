/* Continuum radial shooting for a covariant conformal-scalar PV comparison.
 * Native minus infinite product-cylinder stress, with the same local R and A.
 * Long-double arithmetic protects the regulator and reference cancellations.
 * No material self energy or boundary counterterm is supplied by this kernel.
 */
#include <math.h>
#include <stddef.h>

typedef struct {
    const double *c;
    int cells;
    long double lower, spacing, radius, s, rp_over_r, ap, curvature, einstein[3];
    long double omega2, angular, mass2;
} Problem;

static long double quantity(const Problem *p, long double x, int field) {
    int i = (int)floorl((x-p->lower)/p->spacing);
    if (i < 0) i=0;
    if (i >= p->cells) i=p->cells-1;
    long double dx=x-(p->lower+i*p->spacing);
    const double *c=p->c+(field*p->cells+i)*4;
    return ((c[0]*dx+c[1])*dx+c[2])*dx+c[3];
}

static long double potential(const Problem *p, long double x) {
    return p->omega2*quantity(p,x,0)+p->angular*quantity(p,x,1)
        +quantity(p,x,2)+p->mass2;
}

static long double logarithmic_derivative(const Problem *p, long double end,
        long double probe, long double phase_step, long double attenuation) {
    long double direction=(probe>end ? 1.L : -1.L);
    long double k=sqrtl(fabsl(potential(p,probe)));
    long double cut=attenuation/fmaxl(k,1.e-8L);
    long double x=end;
    if (fabsl(probe-end)>cut) x=probe-direction*cut;
    long double u=0.L, v=direction;
    if (x != end) {
        long double q=potential(p,x);
        if (q<=0.L) x=end;
        else {
            long double h=fminl(.001L,cut/1000.L);
            long double dq=(potential(p,x+h)-potential(p,x-h))/(2*h);
            u=1.L;
            v=direction*sqrtl(q)-dq/(4*q);
        }
    }
    int count=0;
    while (direction*(probe-x)>1.e-18L) {
        long double q=potential(p,x);
        long double h=direction*fminl(fabsl(probe-x),
            fminl(.04L,phase_step/fmaxl(sqrtl(fabsl(q)),.01L)));
        long double qm=potential(p,x+h/2), qe=potential(p,x+h);
        long double ku1=v, kv1=q*u;
        long double ku2=v+h*kv1/2, kv2=qm*(u+h*ku1/2);
        long double ku3=v+h*kv2/2, kv3=qm*(u+h*ku2/2);
        long double ku4=v+h*kv3, kv4=qe*(u+h*ku3);
        u += h*(ku1+2*ku2+2*ku3+ku4)/6;
        v += h*(kv1+2*kv2+2*kv3+kv4)/6;
        long double scale=fabsl(u)+fabsl(v);
        if (scale==0 || !isfinite(scale) || ++count>4000000) return NAN;
        u/=scale; v/=scale; x+=h;
    }
    return v/u;
}

static int difference(Problem *p, long double lo, long double hi, long double probe,
        long double phase_step, long double attenuation, long double *out) {
    long double pl=logarithmic_derivative(p,lo,probe,phase_step,attenuation);
    long double pr=logarithmic_derivative(p,hi,probe,phase_step,attenuation);
    if (!isfinite(pl) || !isfinite(pr) || pl<=pr) return 1;
    long double r2=p->radius*p->radius;
    long double f=1/(r2*(pl-pr));
    long double first=(pl+pr-2*p->s)*f;
    long double mixed=(pl-p->s)*(pr-p->s)*f;
    long double second=2*(p->omega2+p->angular/r2+p->mass2+p->curvature/6)*f
        +2*mixed-(p->ap+2*p->rp_over_r)*first;
    long double time=-p->omega2*f, angular=p->angular*f/(2*r2), mass=p->mass2*f;
    long double native[3]={
        (time+mixed+2*angular+mass)/2
            +(p->einstein[0]*f-second-2*p->rp_over_r*first)/6,
        (time+mixed-2*angular-mass)/2
            +(p->einstein[1]*f+(p->ap+2*p->rp_over_r)*first)/6,
        (time-mixed-mass)/2
            +(p->einstein[2]*f+second+(p->ap+p->rp_over_r)*first)/6
    };
    long double kc=sqrtl(p->omega2+(p->angular+1.L/3.L)/r2+p->mass2);
    long double gc=1/(2*r2*kc);
    long double cylinder[3]={-p->omega2*gc,-kc*kc*gc,(p->angular+1.L/3.L)*gc/(2*r2)};
    for(int k=0;k<3;k++) out[k]=native[k]-cylinder[k];
    return 0;
}

int c1_pv_difference(const double *coefficients, int cells, double lower,
        double spacing, const double *geometry, double lo, double hi, double probe,
        int count, const double *frequency, const int *harmonic, double pv_scale,
        double phase_step, double attenuation, double *output) {
    Problem p={.c=coefficients,.cells=cells,.lower=lower,.spacing=spacing,
        .radius=geometry[0],.s=geometry[1],.rp_over_r=geometry[2],
        .ap=geometry[3],.curvature=geometry[4],
        .einstein={geometry[5],geometry[6],geometry[7]}};
    const int weights[4]={1,-3,3,-1};
    for(int mode=0;mode<count;mode++) {
        p.omega2=(long double)frequency[mode]*frequency[mode];
        p.angular=(long double)harmonic[mode]*(harmonic[mode]+1);
        long double sum[3]={0,0,0};
        for(int mass=0;mass<4;mass++) {
            p.mass2=(long double)mass*pv_scale*pv_scale;
            long double value[3];
            if(difference(&p,lo,hi,probe,phase_step,attenuation,value)) return mode+1;
            for(int k=0;k<3;k++) sum[k]+=weights[mass]*value[k];
        }
        for(int k=0;k<3;k++) output[3*mode+k]=(double)sum[k];
    }
    return 0;
}

int c1_mass_difference(const double *coefficients, int cells, double lower,
        double spacing, const double *geometry, double lo, double hi, double probe,
        int count, const double *frequency, const int *harmonic, double mass,
        double phase_step, double attenuation, double *output) {
    Problem p={.c=coefficients,.cells=cells,.lower=lower,.spacing=spacing,
        .radius=geometry[0],.s=geometry[1],.rp_over_r=geometry[2],
        .ap=geometry[3],.curvature=geometry[4],
        .einstein={geometry[5],geometry[6],geometry[7]},.mass2=(long double)mass*mass};
    for(int mode=0;mode<count;mode++) {
        p.omega2=(long double)frequency[mode]*frequency[mode];
        p.angular=(long double)harmonic[mode]*(harmonic[mode]+1);
        long double value[3];
        if(difference(&p,lo,hi,probe,phase_step,attenuation,value)) return mode+1;
        for(int k=0;k<3;k++) output[3*mode+k]=(double)value[k];
    }
    return 0;
}
