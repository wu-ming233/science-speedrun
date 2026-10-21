/* Fixed B-spline interpolation of the learned field, generic C99. */
#include <math.h>
static int bound(int n,int lo,int hi){return n<lo?lo:(n>hi?hi:n);}
static void weights(double t,double h,int order,double*w){
 if(order==0){w[0]=(1-t)*(1-t)*(1-t)/6;w[1]=(3*t*t*t-6*t*t+4)/6;w[2]=(-3*t*t*t+3*t*t+3*t+1)/6;w[3]=t*t*t/6;}
 else if(order==1){w[0]=-.5*(1-t)*(1-t)/h;w[1]=(1.5*t*t-2*t)/h;w[2]=(-1.5*t*t+t+.5)/h;w[3]=.5*t*t/h;}
 else{w[0]=(1-t)/(h*h);w[1]=(3*t-2)/(h*h);w[2]=(-3*t+1)/(h*h);w[3]=t/(h*h);}
}
static void cubic(int nr,const double*spline,double r,double z,int dr,int dz,float*out){
 const double hr=1.9/64,hz=4.4/64;double qr=(r-.1)/hr,qz=(z+2.2)/hz;
 int ir=bound((int)floor(qr),2,61),iz=bound((int)floor(qz),2,61);double wr[4],wz[4];weights(qr-ir,hr,dr,wr);weights(qz-iz,hz,dz,wz);
 for(int k=0;k<nr;k++){const double*c=spline+k*4225;double sum=0;for(int i=0;i<4;i++)for(int j=0;j<4;j++)sum+=wr[i]*wz[j]*c[(ir+i-1)*65+iz+j-1];out[k]=(float)sum;}
}
void geometry_cache(int nr,const double*grid,const double*spline,const double*points,const double*critical,float*out){
 for(int i=0;i<32;i++){
  double r=points[2*i],z=points[2*i+1],qr=(r-.1)/(1.9/64),qz=(z+2.2)/(4.4/64);int ir=bound((int)floor(qr),0,63),iz=bound((int)floor(qz),0,63);double u=qr-ir,v=qz-iz;
  for(int k=0;k<nr;k++){const double*g=grid+k*4225;out[i*nr+k]=(float)((1-u)*(1-v)*g[ir*65+iz]+u*(1-v)*g[(ir+1)*65+iz]+(1-u)*v*g[ir*65+iz+1]+u*v*g[(ir+1)*65+iz+1]);}
  cubic(nr,spline,r,z,1,0,out+(32+i)*nr);cubic(nr,spline,r,z,0,1,out+(64+i)*nr);
 }
 const int orders[6][2]={{0,0},{1,0},{0,1},{2,0},{1,1},{0,2}};
 for(int i=0;i<3;i++)for(int j=0;j<6;j++)cubic(nr,spline,critical[2*i],critical[2*i+1],orders[j][0],orders[j][1],out+(96+6*i+j)*nr);
}

void gap_cache(int nr,const double*spline,const double*points,float*out){
 for(int i=0;i<2;i++){
  cubic(nr,spline,points[2*i],points[2*i+1],0,0,out+(2*i)*nr);
  cubic(nr,spline,points[2*i],points[2*i+1],1,0,out+(2*i+1)*nr);
 }
}
