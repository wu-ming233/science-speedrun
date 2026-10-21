/* Fixed arithmetic for a shared flux/virtual-circuit controller.
 * No model training, allocation, I/O or external state. Generic x86-64 C99.
 */
#include <math.h>
#define NR 33
#define NF 86
#define NB 38
#define NS 512
static inline double clip(double x,double lo,double hi){return fmax(lo,fmin(hi,x));}
void control_step(const float*obs,const float*wt,const float*bias,const float*cache,
                  const double*K,const double*geom,const double*machine,
                  double*state,double*out){
    const double *R=machine,*L=R+11,*lo=L+121,*hi=lo+11,*vlow=hi+11,*vhigh=vlow+12,*p=vhigh+12;
    const double dt=p[0],ip=obs[512],norm=p[13]/fmax(ip,10000.);
    double f[NR],v[NF],dr[3],dz[3],stationary[3],b[NB],x[11],next[11],rate[11];
    for(int j=0;j<NR;j++){
        double sum=0.;const float*w=wt+j*NS;
        for(int i=0;i<NS;i++)sum+=(double)w[i]*obs[i];
        f[j]=sum*norm+bias[j];
    }
    for(int i=0;i<NF;i++){
        const float*c=cache+i*NR;double sum=c[0];
        for(int j=0;j<NR-1;j++)sum+=(double)c[j+1]*f[j];
        v[i]=sum;
    }
    for(int i=0;i<3;i++){
        const double*c=v+64+6*i;double det=c[3]*c[5]-c[4]*c[4];
        if(fabs(det)<=1e-10)det=det<0?-1e-10:1e-10;
        dr[i]=clip((c[5]*c[1]-c[4]*c[2])/det,-.15,.15);
        dz[i]=clip((c[3]*c[2]-c[4]*c[1])/det,-.15,.15);
        stationary[i]=c[0]-.5*(dr[i]*c[1]+dz[i]*c[2]);
    }
    double boundary=stationary[2]>(stationary[0]+stationary[1])*.5?fmax(stationary[0],stationary[1]):fmin(stationary[0],stationary[1]);
    double target=.995*boundary+.005*stationary[2];
    for(int i=0;i<32;i++){
        double den=v[32+i]<0?-fmax(fabs(v[32+i]),.02):fmax(fabs(v[32+i]),.02);
        b[i]=clip((v[i]-target)/den,-p[8],p[8]);
    }
    int gate0=(geom[1]>=1&&fabs(dr[0])<p[9]&&fabs(dz[0])<p[9]);
    int gate1=(geom[1]>=2&&fabs(dr[1])<p[9]&&fabs(dz[1])<p[9]);
    b[32]=gate0?dr[0]:0.;b[33]=gate0?dz[0]:0.;b[34]=gate1?dr[1]:0.;b[35]=gate1?dz[1]:0.;
    for(int i=0;i<2;i++){
        double grad=v[83+2*i];double den=grad<0?-fmax(fabs(grad),.02):fmax(fabs(grad),.02);
        b[36+i]=clip((v[82+2*i]-boundary)/den,-p[8],p[8]);
    }
    const double*op=K+(gate0+2*gate1)*11*NB;
    for(int i=0;i<11;i++){double sum=0.;for(int j=0;j<NB;j++)sum+=op[i*NB+j]*b[j];x[i]=sum;}
    double ramp=fmin(1.,(state[15]+1.)/p[1]);
    double zt=state[12]+p[3]*ramp*geom[0]*x[10]*dt;
    double ipramp=fmin(1.,(state[15]+1.)/fmax(1.,p[14]));
    double iperr=obs[583]-ip,ipint=state[11]+iperr*dt*ipramp;
    for(int i=0;i<11;i++){
        double dI=i==0?ipramp*(p[4]*iperr+p[5]*ipint):p[2]*ramp*x[i-1];
        next[i]=clip(state[i]+dI*dt,lo[i],hi[i]);
        next[i]=clip(next[i],obs[500+i]-p[7],obs[500+i]+p[7]);
        rate[i]=(next[i]-state[i])/dt+(next[i]-obs[500+i])/p[6];
    }
    for(int i=0;i<11;i++){
        double sum=R[i]*obs[500+i];for(int j=0;j<11;j++)sum+=L[i*11+j]*rate[j];out[i]=sum;
    }
    double z=f[NR-1],velocity=state[15]>0?(z-state[13])/dt*ip:0.;
    double zerr=(zt-z)*ip,zint=state[14]+zerr*dt;
    out[11]=p[10]*zerr+p[11]*velocity+p[12]*zint;
    for(int i=0;i<12;i++)out[i]=clip(isfinite(out[i])?out[i]:0.,vlow[i],vhigh[i]);
    for(int i=0;i<11;i++)state[i]=next[i];
    state[11]=ipint;state[12]=zt;state[13]=z;state[14]=zint;state[15]+=1.;
}
