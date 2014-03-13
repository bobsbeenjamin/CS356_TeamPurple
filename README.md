CS356_TeamPurple
================
Directions on running hybridfuzzer on your own code:

You must first compile hybrid fuzzer using the "ant -f build.xml" command; the output .class files must be in /hybridfuzzer/classes

To get a custom source file to run, you have to place your code inside MTVectorTest.java. Make sure your class name is MTVectorTest, and it must have the statement "package benchmarks.dstest;" before compiling it.

Take the MTVectorTest.class file and place it in the /hybridfuzzer/classes/benchmarks/dstest/ subfolder. Then change directory to /hybridfuzzer and run  "ant -f trimmed_run.xml test_vector" to see your code's output.
