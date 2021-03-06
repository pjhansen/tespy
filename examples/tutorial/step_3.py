from tespy import cmp, con, nwk, hlp

# %% network

nw = nwk.network(fluids=['water', 'NH3'],
                 T_unit='C', p_unit='bar', h_unit='kJ / kg', m_unit='kg / s',
                 p_range=[0.1, 100], T_range=[1, 500], h_range=[15, 5000])

# %% components

# sources & sinks

c_in = cmp.source('coolant in')
cb = cmp.source('consumer back flow')
cf = cmp.sink('consumer feed flow')
amb_in = cmp.source('source ambient')
amb_out = cmp.sink('sink ambient')
ic_in = cmp.source('source intercool')
ic_out = cmp.sink('sink intercool')

c_out = cmp.sink('coolant out')

# consumer system

cd = cmp.condenser('condenser')
rp = cmp.pump('recirculation pump')
cons = cmp.heat_exchanger_simple('consumer')

# evaporator system

ves = cmp.vessel('vessel')
dr = cmp.drum('drum')
ev = cmp.heat_exchanger('evaporator')
su = cmp.heat_exchanger('superheater')
pu = cmp.pump('pump evaporator')

# compressor-system

cp1 = cmp.compressor('compressor 1')
cp2 = cmp.compressor('compressor 2')
he = cmp.heat_exchanger('heat_exchanger')

# %% connections

# consumer system

c_in_cd = con.connection(c_in, 'out1', cd, 'in1')

cb_rp = con.connection(cb, 'out1', rp, 'in1')
rp_cd = con.connection(rp, 'out1', cd, 'in2')
cd_cons = con.connection(cd, 'out2', cons, 'in1')
cons_cf = con.connection(cons, 'out1', cf, 'in1')

nw.add_conns(c_in_cd, cb_rp, rp_cd, cd_cons, cons_cf)

# connection condenser - evaporator system

cd_ves = con.connection(cd, 'out1', ves, 'in1')

nw.add_conns(cd_ves)

# evaporator system

ves_dr = con.connection(ves, 'out1', dr, 'in1')
dr_pu = con.connection(dr, 'out1', pu, 'in1')
pu_ev = con.connection(pu, 'out1', ev, 'in2')
ev_dr = con.connection(ev, 'out2', dr, 'in2')
dr_su = con.connection(dr, 'out2', su, 'in2')

nw.add_conns(ves_dr, dr_pu, pu_ev, ev_dr, dr_su)

amb_in_su = con.connection(amb_in, 'out1', su, 'in1')
su_ev = con.connection(su, 'out1', ev, 'in1')
ev_amb_out = con.connection(ev, 'out1', amb_out, 'in1')

nw.add_conns(amb_in_su, su_ev, ev_amb_out)

# connection evaporator system - compressor system

su_cp1 = con.connection(su, 'out2', cp1, 'in1')

nw.add_conns(su_cp1)

# compressor-system

cp1_he = con.connection(cp1, 'out1', he, 'in1')
he_cp2 = con.connection(he, 'out1', cp2, 'in1')
cp2_c_out = con.connection(cp2, 'out1', c_out, 'in1')

ic_in_he = con.connection(ic_in, 'out1', he, 'in2')
he_ic_out = con.connection(he, 'out2', ic_out, 'in1')

nw.add_conns(cp1_he, he_cp2, ic_in_he, he_ic_out, cp2_c_out)

# %% component parametrization

# condenser system

cd.set_attr(pr1=0.99, pr2=0.99, ttd_u=5)
rp.set_attr(eta_s=0.8)
cons.set_attr(pr=0.99, offdesign=['zeta'])

# evaporator system

ves.set_attr(mode='man')
ev.set_attr(pr1=0.99, pr2=0.99, ttd_l=5,
            kA_char1='EVA_HOT', kA_char2='EVA_COLD',
            design=['pr1', 'ttd_l'], offdesign=['zeta1', 'kA'])
su.set_attr(pr1=0.99, pr2=0.99, ttd_u=2)
pu.set_attr(eta_s=0.8)

# compressor system

cp1.set_attr(eta_s=0.8, mode='man')
cp2.set_attr(eta_s=0.8, pr=5, mode='man')

he.set_attr(pr1=0.98, pr2=0.98)

# %% connection parametrization

# condenser system

c_in_cd.set_attr(fluid={'water': 0, 'NH3': 1})
cb_rp.set_attr(T=60, p=10, fluid={'water': 1, 'NH3': 0})
cd_cons.set_attr(T=90)
cons_cf.set_attr(h=con.ref(cb_rp, 1, 0), p=con.ref(cb_rp, 1, 0))

# evaporator system cold side

pu_ev.set_attr(m=con.ref(ves_dr, 4, 0), p0=5)
su_cp1.set_attr(p0=5, h0=1700)

# evaporator system hot side

amb_in_su.set_attr(T=12, p=5, fluid={'water': 1, 'NH3': 0})
ev_amb_out.set_attr(T=9)

# compressor-system

he_cp2.set_attr(T=40, p0=10)
ic_in_he.set_attr(p=5, T=20, fluid={'water': 1, 'NH3': 0})
he_ic_out.set_attr(T=30, design=['T'])
cp2_c_out.set_attr(p=con.ref(c_in_cd, 1, 0), h=con.ref(c_in_cd, 1, 0))

# %% key paramter

cons.set_attr(Q=-230e3)

# %% Calculation

nw.solve('design')
# alternatively use:
nw.solve('design', init_file='condenser_eva_results.csv')
nw.print_results()
nw.save('heat_pump')

cons.set_attr(Q=-200e3)

nw.solve('offdesign', init_file='heat_pump/results.csv',
         design_file='heat_pump/results.csv')
nw.print_results()
