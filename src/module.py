import os
import re

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text) ]

# module file
def get_filename_mae():
    for file in os.listdir():
        if file.endswith('.mae') or file.endswith('.maegz'):
            filename = (file)
    return filename
        
def create_msj_file(path, kTemp, asl, g_height, g_width, g_interval): 
        with open(path, 'w') as file_msj:
            file_msj.write('''# Desmond standard NVT relaxation protocol
# All times are in the unit of ps.
# Energy is in the unit of kcal/mol.
task {
task = "desmond:auto"
set_family = {
  desmond = {
     checkpt.write_last_step = no
  }
}
}

simulate {
title       = "Brownian Dynamics NVT, T = 10 K, small timesteps, and restraints on solute heavy atoms, 100ps"
annealing   = off
time        = 100
timestep    = [0.001 0.001 0.003 ]
temperature = 10.0
ensemble = {
  class = "NVT"
  method = "Brownie"
  brownie = {
     delta_max = 0.1
  }
}
restraints.new = [{
  name = posre_harm
  atoms = solute_heavy_atom
  force_constants = 50.0
}]
}


simulate {
title       = "NVT, T = 10 K, small timesteps, and restraints on solute heavy atoms, 12ps"
annealing   = off
time        = 12
timestep    = [0.001 0.001 0.003]
temperature = 10.0
restraints.new = [{
  name = posre_harm
  atoms = solute_heavy_atom
  force_constants = 50.0
}]
ensemble    = {
  class  = NVT
  method = Langevin
  thermostat.tau = 0.1
}

randomize_velocity.interval = 1.0
eneseq.interval             = 0.3
trajectory.center           = solute
}

simulate {
title       = "NVT and no restraints"
time        = 24
effect_if   = [["@*.*.annealing"] 'annealing = off temperature = "@*.*.temperature[0][0]"']
ensemble    = {
  class  = NVT
  method = Langevin
  thermostat.tau = 0.1
}

eneseq.interval   = 0.3
trajectory.center = solute

restraints.new = [{
  name = posre_harm
  atoms = ["mol.num 1"]  
  force_constants = 1.0
}]
}
simulate {
cfg_file = "''' + path.split('/')[1] + '''"
jobname  = "$MAINJOBNAME"
dir      = "."
compress = ""
meta = {
  kTemp = ''' + kTemp + '''
  cv = [{ type = rmsd
        atom = ['''+ asl+''' ]
        width = ''' + g_width + '''
     }
  ]
  cv_name = "$JOBNAME$[_replica$REPLICA$].cvseq"
  first = 0.0
  height = ''' + g_height + '''
  interval = ''' + g_interval + '''
  name = "$JOBNAME$[_replica$REPLICA$].kerseq"
} 
       backend ={
           # set cvseq interval to trajectory output
           force.term.ES.interval = '@*.*.*.*.trajectory.interval'
       }
       checkpt.write_last_step = yes
    
}

analysis {
meta = { }
dir = "."
compress = ""
}''')

def create_cfg_file(path, seed, time, interval):           
        with open(path, 'w') as file_cfg:
            file_cfg.write('''annealing = false
backend = {
}
bigger_rclone = false
box = ?
checkpt = {
   first = 0.0
   interval = 240.06
   name = "$JOBNAME.cpt"
   write_last_step = true
}
cpu = 1
cutoff_radius = 9.0
elapsed_time = 0.0
energy_group = false
eneseq = {
   first = 0.0
   interval = 1.0
   name = "$JOBNAME$[_replica$REPLICA$].ene"
}
ensemble = {
   barostat = {
      tau = 2.0
   }
   class = NVT
   method = NH
   thermostat = {
      tau = 1.0
   }
}
glue = solute
maeff_output = {
   center_atoms = solute
   first = 0.0
   interval = 120.0
   name = "$JOBNAME$[_replica$REPLICA$]-out.cms"
   periodicfix = true
   trjdir = "$JOBNAME$[_replica$REPLICA$]_trj"
}
meta_file = ?
pressure = 1.01325
randomize_velocity = {
   first = 0.0
   interval = inf
   seed =  ''' + str(seed) + '''
   temperature = "@*.temperature"
}
restrain = none
simbox = {
   first = 0.0
   interval = 1.2
   name = "$JOBNAME$[_replica$REPLICA$]_simbox.dat"
}
surface_tension = 0.0
taper = false
temperature = [
   [300.0 0 ]
]
time = ''' + time + '''
timestep = [0.002 0.002 0.006 ]
trajectory = {
   center = []
   first = 0.0
   format = dtr
   frames_per_file = 250
   interval = ''' + interval + '''
   name = "$JOBNAME$[_replica$REPLICA$]_trj"
   periodicfix = true
   write_last_vel = false
   write_velocity = false
}''')
