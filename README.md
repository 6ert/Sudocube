# Sudocube version 0.99 
3D Sudoku by Gert Weber
Game to play in Blender

####### Sudocube.py #######

The game 'Sudocube' is a Sudoku in the simplest 3D variant.
The possible viewer positions (Front, Back, Left, Right, Top, Bottom) result in different viewing levels,
in each of which the numbers 1 - 9 should be contained once completely.
However, no overlaps of the same numbers should occur, no matter from which position they are viewed. 

The program is implemented as a Python script 'Sudocube.py'. 
It uses the Blender Python API and is in the present version only executable in Blender.
The script is called within a Blender instance (Blender version 3.3 or higher).

After Blender has been started, the script 'Sudocube.py' should be referenced in the workspace 'Scripting' (Open - Text).
If there is a red exclamation mark next to it - click on it - 'make Text internal' or 'reopen file' - reload.

The script expects the nine numbers and a 'space' as Blender textures in .png image format.
They are located in the 'images' folder, which should be on the same level in the file system as the script.

Then execute the script via 'Run'.
Now in the '3D Viewport' within the 'Tools' (activate with shortcut 'N') a panel 'Sudocube' should be available.
Start a new 3D Sudoku with 'New Game'.
Game elements should be self-explanatory otherwise - see below.

####### SudocubeAddon.py #######

The module 'SudocubeAddon' can be installed as Blender Add-on with identical functions to the above.

Blender - Edit - Preferences - Add-ons - install - SudocubeAddon.py

The add-on is then in the list under 'Object: Sudocube Addon'.
You have to activate it by marking it.
Because Blender stores the installed add-ons in a special path in the file system, 
the folder 'images' with the textures must be made known.
Enter the path under 'Object: Sudocube Addon' - Preferences (expand add-on left over the arrow)
e.g.: C:\Users\root\Documents\images\
if there are the files '0.png' - '9.png'.
Then in 'Blender - Workspace - Layout' activate the 'Tools' (shortcut 'N').

'New Game' will start by random level.
See hidden Cubes by clicking 'explode Sudocube'
Solve by activating an empty Cube and 'assign' numbers.
To navigate in the viewport use shortcuts on 'Numpad'
e.g.: CTRL+(Numpad 6) to move display.
(shortcuts see: https://docs.blender.org/manual/en/latest/interface/keymap/introduction.html)


Have Fun
