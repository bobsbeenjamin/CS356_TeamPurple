CS356_TeamPurple
================
Note: These instructions assume that you have downloaded all files and directories in this repo to a linux machine. This project may work on Windows, but that is not guaranteed. 

Directions to run hybridfuzzer on your own code
-----------------------------------------------
 GUI Option:
  1. Type arguments into the fields. You must enter a package name. 
    a) See "Package Naming Instructions" below for more details. 
  2. Press the [Run] button. 
 
 Command Line Option:
  1. Type "python hybridfuzzer.py"
    a) Pass the package name as the first argument. If you do not, then you will be prompted for it. 
    b) (Optional) Pass the build file name as the second argument. See "Build File Instructions" below for more details. 
    c) (Optional) If your testing source code needs args to test correctly, then pass them in as args 3-x. 
  2. Press Enter. 

Additional Instructions
-----------------------
Package Naming Instructions:
 1. Be sure to use standard java conventions when creating your source code. In particular, all package names must be dot-separated, and must represent the directory/file tree of your source code files. 
 2. Place your source code in the 'src' directory. 
 3. Pass the name of your root-level entry file for your source code. Treat 'src' as the root directory, but do not include it in the name. 
 4. Example: Your root file is in 'src/building/room' and is called 'Chair.java'. Pass 'building.room.Chair'. 

Build File Instructions:
 1. If you have your own ant build file, then simply add it to the level of the Python script. 
   a) If your file is named 'build.xml', then you do not need to pass the name. 
   b) Otherwise, be sure to pass the name of your ant file. 
   c) Feel free to overwrite the 'build.xml' file that comes with this package. 
 2. If you want your code compiled with your system's standard java compiler, then pass the command 'javac' as this argument. 
 3. If your code is already compiled, then add that code to the 'classes' directory, and pass the command 'do_not_compile' as this argument. This may be convenient if you run this tool multiple times and do not want to recompile your code each time.
