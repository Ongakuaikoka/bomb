 
from distutils.core import setup
 
import py2exe, glob
 
opts = { 
 "py2exe": { 
   # if you import .py files from subfolders of your project, then those are
   # submodules.  You'll want to declare those in the "includes"
   'includes':['os',
               'random',
               'eztext',
		'operator'
              ],
 } 
} 
 
setup(
 
  #this is the file that is run when you start the game from the command line.  
  windows=['defuse_bomb.py'],
 
  #options as defined above
  options=opts,
 
  #data files - these are the non-python files, like images and sounds
  #the glob module comes in handy here.
  data_files = [
    ("data", glob.glob("data\\white-oak.jpg"))
  ],
 
  #this will pack up a zipfile instead of having a glut of files sitting
  #in a folder.
  zipfile="lib/shared.zip"
)