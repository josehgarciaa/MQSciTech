import sys
sys.path.append("/content/conda_dir")
import kwant
import qsymm
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from numpy.random import random
welcome="Packages are loaded. ¡Welcome!"


def Rz(phi):
  sp.Matrix([  [ sp.cos(2*phi*sp.pi),-sp.sin(2*phi*sp.pi), 0 ],
               [ sp.sin(2*phi*sp.pi), sp.cos(2*phi*sp.pi), 0 ],
               [ 0            , 0        , 1 ]
            ]);

  
import requests
import IPython.display as Disp
grafeno_real = 'https://i.pinimg.com/564x/27/73/60/277360f8a8265b0a8008d1d03023a7be.jpg'
grafeno_disp = 'https://icn2.cat/images/20190802_spin-communication.jpg'
def ejemplo_grafeno_real():
  return Disp.Image(requests.get(grafeno_real).content);
def ejemplo_dispositivo_grafeno():
  return Disp.Image(requests.get(grafeno_disp).content);

Phi0 =  2.067833758e-6;
energy = -2;
lat_c  = 0.246;
lat_vec= lat_c*np.array(((1, 0), (0.5,0.5*np.sqrt(3))));
Area = np.sqrt(3)*0.5*lat_c*lat_c;
orbs   = lat_c*np.array([(0, 0), (0, 1 / np.sqrt(3))]);
graphene = kwant.lattice.general(lat_vec, orbs);
a, b = graphene.sublattices

def create_system( L, W, sym=None, U=1.0, c=0.0, r0=(0,0), phi=0 ):

  syst = kwant.Builder()
  if sym is not None:
    syst = kwant.Builder(sym);
    phi = 0
    
  def shape(pos):
    x, y = pos;
    a0, a1 = np.linalg.inv(lat_vec).T.dot(pos);
    return ( r0[0]/lat_c <= a0 <= L/lat_c ) and ( r0[1]/lat_c <= a1 <= W/lat_c )

  def anderson(site):
      if random()*100 <= c:
        return U*(random()-0.5);
      return 0.0;
  #incorporate anderson disorder as onsites
  syst[graphene.shape(shape, r0)] = anderson;

  def hopping(site_i, site_j):
    xi, yi = site_i.pos;
    xj, yj = site_j.pos;
    return -2.8*np.exp(-0.5j * phi * (xi - xj) * (yi + yj))
  #incorporate hoppings
  syst[graphene.neighbors()] = hopping;

  return syst;

def crear_cable(L, W, U=1.0, c=0.0, phi=0 ):
  return create_system(L, W, sym=None, U=U, c=c,phi=phi );

def agregar_contactos(syst,L, W):
    tdir=-graphene.vec((1,0));
    sym = kwant.TranslationalSymmetry(tdir);
    lead = create_system(L=L, W=W, sym=sym,r0=2*tdir );
    syst.attach_lead(lead)
    syst.attach_lead(lead.reversed())
    return syst;

def crear_barra_hall(syst,L, W):
    #Contactos laterales
    tdir=-graphene.vec((1,0));
    r0  = 2*tdir;
    sym = kwant.TranslationalSymmetry(tdir);
    lead = create_system(L=L, W=W, sym=sym,r0=r0 );
    syst.attach_lead(lead)
    syst.attach_lead(lead.reversed())
    #Contactos verticales
    tdir=-graphene.vec((0,1));
    r0  = L*graphene.vec((1,0));
    sym = kwant.TranslationalSymmetry(tdir);
    lead = create_system(L=L*2/3, W=W, sym=sym,r0=r0 );
    syst.attach_lead(lead)
    syst.attach_lead(lead.reversed())
    return syst;

def graficar_sistema( syst ):
  kwant.plot(syst, show=False,dpi=100);
  imp_pos = [s.pos for s,v in syst.site_value_pairs() if np.abs(v(s))>1e-5 ]
  if len(imp_pos)>0: 
    ax = plt.gca();
    ax.scatter( *np.transpose(imp_pos), c="k",zorder=3,s=1);
  plt.show();

def calcula_conductancia(fsyst,E0,nreal=1 ):
  C0 = 7.7480e-5;
  return C0*np.mean([ kwant.smatrix(fsyst, E0).transmission(1, 0) for i in range(nreal)]); 

def calcula_matriz_conductancia(fsyst,E0,nreal=1 ):
  C0 = 7.7480e-5;
  C = C0*kwant.smatrix(fsyst,E0 ).conductance_matrix();
  return C[:3,:3]; 

def calcula_matriz_resistencia(fsyst,E0,nreal=1 ):
  return np.linalg.inv(calcula_matriz_conductancia(fsyst,E0,nreal)); 


def calcula_resistencia(fsyst,E0,nreal=1 ):

  return 1/calcula_conductancia(fsyst,E0,nreal ); 




