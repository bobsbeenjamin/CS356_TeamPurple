#-----------------------------------------------------------------------------------------
# Name:      TeamPurple_HybridIO
# Purpose:   Gives user an interactive prompt to easily feed a program root file and get 
#               feedback on all steps as they happen.
# Author:    Ben Clifford
# Created:   2014-02-17
# Updated:   2014-03-05
#-----------------------------------------------------------------------------------------

import datetime, multiprocessing, os, sys, shutil, subprocess, time, webbrowser

logStr = "Starting script..." # used by logMe()

##########################################################################################
#################################       MAIN        ######################################
##########################################################################################

def main():
    try:
        welcomeUser()
        package, cmdLineArgs, antBuildName = getScriptArgs()
        if not package:
            return # exit script thru finally block
        # TODO [Optional: Run javaCompile() and transformSourceToMarkup() in parallel]
        javaCompile(package, antBuildName)
        transformSourceToMarkup()
        output = runHybridAntScript(package, cmdLineArgs)
        createFormattedOutput(output, package)
    
    finally:
        logMe("Script is now exiting...")
        createLogFile() # remove this line in production versions
    

##########################################################################################
#################################       OTHER       ######################################
##########################################################################################

def welcomeUser():
    """Print some instruction text for the user."""
    welcomeText = """Instructions on use:
Place your code in the src directory, then run this Python script with the following args:
1) Dot-seperated relative name of root java file (required)
2) The name of your custom ant build script (optional; default is supplied)
3) Any additional arguments your program requires (optional; seperate args w/ whitespace)
Results will be generated as an html file in the same directory as this script. If you 
ran this script with too few args, simply perform a keyboard interrupt and start over."""
    print welcomeText
    

def getScriptArgs():
    """@return package: The package name of the user's Java code
    @return cmdLineArgs: The command line args to pass to the user's program
    @return antBuildName: The user-created ant build file name"""
    # Note: Python sets the 0th argv as the script name
    argv = sys.argv
    if len(argv) > 1:
        package = argv[1]
    else:
    # DONE Make user guide for how to enter package name
        packageInstructions = \
        """The package was not passed as a command line arg, but is required.
Please enter a dot-seperated package name for the root java file that is relative to src:
"""
        package = raw_input(packageInstructions)
    logMe("Package of root java file is " + package)
    if len(argv) > 2:
        antBuildName = argv[2]
        logMe("Custom ant build name is " + antBuildName)
    else:
        antBuildName = ""
    if len(argv) > 3:
        cmdLineArgs = " ".join(argv[3:])
        logMe("Args are " + cmdLineArgs)
    else:
        cmdLineArgs = ""
    return package, cmdLineArgs, antBuildName
    

def javaCompile(package, antBuildName):
    """Modifies an ant script, then runs it to compile the user's java program/suite."""
    # DONE Allow user to either bypass compiling or to use javac instead of ant
    # DONE Compile user's code using an ant script (possibly passed thru antBuildName)
    if not antBuildName:
        antBuildName = "build.xml"
    if antBuildName == "javac":
        args = "javac " + transformPackageToPath(package)
    # Two keywords are supported to allow user to bypass building their code base
    elif antBuildName.lower() in ("donotbuild", "do_not_build"):
        logMe("Java code will not be compiled (per client request)")
        return
    else:
        args = "ant -f " + antBuildName
    logMe("Java code is compiling...")
    os.system(args)
    

def transformPackageToPath(package, extension=".java"):
    """Transforms a string of the form A.B.C into a string of the form A/B/C, using the 
    current OS path seperator, then adds to the end. 
    @return A string as defined above"""
    return package.replace(".", os.sep) + extension
    

def transformSourceToMarkup():
    """Recursively searches the directory tree rooted at path, and copies all files to a 
    'mirrored' html directory. Adds tags to each line in the copied file, and adds the 
    .html extension."""
    dest = "html"
    deleteDir(dest)
    for sourceFile in walkDir("src"):
        # The 'with' keyword opens the file, provides the var after 'as' as a file handle, 
        # and closes the file once the with-block exits
        with open(sourceFile) as source:
            fileData = source.readlines()
        # Create a destination file name by replacing 'src' on the front with 'html'
        destFile = sourceFile.replace("src", "html", 1) + ".html"
        # Grab the directory that destFile will be in, and create it if needed
        localParentDir = destFile.rpartition(os.sep)[0]
        createDir(localParentDir)
        with open(destFile, 'wb') as dest:
            for line_num, line in enumerate(fileData):
                new_line = "<a name=\"line_" + str(line_num) + "\">" \
                          + line.rstrip('\n') + "</a><BR/>\n"
                dest.write(new_line)
    

def runHybridAntScript(fullPackageName, cmdLineArgs):
    """Run the 'trimmed_run.xml' file for HybridFuzzer. Capture the output and return it.
    @return The output from 'run.xml' as a list of strings"""
    origHybridAntFile = "trimmed_run.xml"
    tempHybridAntFile = "trimmed_run_tmp.xml"
    with open(origHybridAntFile) as ant:
        antData = ant.readlines()
    for i, line in enumerate(antData):
        if "MTVectorTest" in line:
            antData[i] = line.replace("benchmarks.dstest.MTVectorTest", fullPackageName)
        # DONE Allow user to pass args
        if '<property  name="javato.app.args"' in line:
            if cmdLineArgs:
                antData[i] = line.replace('value=""', 'value="'+cmdLineArgs+'"')
            else:
                # Delete the line entirely
                antData[i] = ""
    with open(tempHybridAntFile, 'wb') as ant:
        ant.writelines(antData)
    logMe("Code is being analyzed...")
    tempOutputFile = "tempOut.txt"
    args = "ant -f trimmed_run_tmp.xml test_vector > " + tempOutputFile 
    os.system(args)
    with open(tempOutputFile) as tmp:
        output = tmp.readlines()
    logMe("ant script is complete")
    os.remove(tempOutputFile)
    os.remove(tempHybridAntFile)
    return output
    

def createFormattedOutput(output, codeName):
    """Create an html file based on the output produced by hybridfuzzer. Then open it in 
    the system's current default browser."""
    logMe("Output is being formatted...")
    # Start formattedOutput as an array with some strings that will eventually be written
    # to our formatted html output file 
    header = "<head><b><u>Client code name: " +codeName + "</u></b></head>" + endl('html')
    formattedOutput = [header]
    formattedOutput.append("<body>" + endl('html'))
    # DONE Format output as feature-rich xml
    lineToDo = "ignore"
    # Loop over hybridfuzzer output and use it to create our formatted output
    for line in output:
        line = line.strip()
        line = line.partition("[java]")[2]
        # Start transforming to linkable html just after this line
        if "Data race between" in line:
            lineToDo = "transform"
        # Switch to copying at this line (including this line)
        if line.startswith("# of data races"):
            lineToDo = "copy"
        if lineToDo=="transform":
            formattedOutput.append(transformLineToLink(line))
        if lineToDo=="copy":
            if "# of data races" in line:
                line = line.partition(" and ")[0] # Remove 'and lock races 0'
            formattedOutput.append(line + endl('html'))
        # Start ignoring lines again
        if not "Data race between" in line and lineToDo=='transform':
            lineToDo = "ignore"
    formattedOutput.append("</body>")
    outputFileName = "FormattedOutput.html"
    with open(outputFileName, 'wb') as outputFile:
        outputFile.writelines(formattedOutput)
    logMe("Output is ready at " + outputFileName)
    url = "file://" + os.getcwd() + "/FormattedOutput.html"
    webbrowser.open(url)
    

def transformLineToLink(line):
    """Pull in a line, and pass back a transformed line (see the comments below for the 
    logic involved.
    @return A hyperlinked transforamation of line"""
    # Slice off the first 7 characters, then copy until the end of 'between '
    transformmedLine = "Data race betweeen "
    # Create the first part of the first href tag
    transformmedLine += "<a href=./html/" + parseOutputLine(line, 1)
    transformmedLine += ".html#line_" + parseOutputLine(line, 2) + ">"
    # Fill the first tag and close it
    transformmedLine += parseOutputLine(line,1) + parseOutputLine(line,2) + "</a>"
    # Add the first thread number and ' and '
    transformmedLine += parseOutputLine(line, 3)
    # Now it all again for the second part of the race collision 
    transformmedLine += "<a href=./html/" + parseOutputLine(line, 4)
    transformmedLine += ".html#line_" + parseOutputLine(line, 5) + ">"
    transformmedLine += parseOutputLine(line,4) + parseOutputLine(line,5) + "</a>"
    transformmedLine += parseOutputLine(line, 6)
    # Finally we can add this bad boy to formattedOutput!
    return transformmedLine + endl('html')
    

def parseOutputLine(line, case):
    """Scans a line from hybridfuzzer output, and grabs either a relative path, a line 
    number, or a thread number from it. case can be a num between 1-4, and signifies the 
    position of the substring to return.
    @return A string, as described above"""
    # Case: Need first path 
    if case==1:
        # Pull the front off
        line = line.partition(" between ")[2]
        # Pull the line number (and remaining text) off of the end
        line = line.partition("#")[0]
        return line
    # Case: Need first line number 
    elif case==2:
        line = line.partition("#")[2]
        line = line.partition(":")[0]
        return line
    # Case: Need first thread number 
    elif case==3:
        line = line.partition(":")[2]
        line = line.partition(" and ")[0]
        return " at thread #" + line + " and "
    # Case: Need second path 
    elif case==4:
        line = line.partition("and ")[2]
        line = line.partition("#")[0]
        return line
    # Case: Need second line number 
    elif case==5:
        # partition scans left-to-right, while rpartition scans right-to-left 
        line = line.rpartition("#")[2]
        line = line.partition(":")[0]
        return line
    # Case: Need second thread number 
    elif case==6:
        line = line.rpartition(":")[2]
        return " at thread #" + line
    else:
        # My half-hearted error handling
        logMe("Bad call to parseOutputLine()")
        return ""
    

##########################################################################################
##################################     UTILITIES    ######################################
##########################################################################################

def createDir(path):
    """Recursively creates a directory at path, if needed.
    @return The new path if the path is created; None otherwise"""
    path = str(path)
    if not os.path.isdir(path):
        os.makedirs(path)
        logMe("COMPLETE: Directory created: " + path)
        return path
    

def createLogFile(fileName=None, logDir="LOGS"):
    """Creates a log file in logDir containing all console output (this expects user to 
    print output using logMe()). If fileName is not passed, then a default is used."""
    if not fileName:
        fileName = "PythonOutput_" + getDateTime() + ".log"
    if not isString(fileName) or not isString(logDir):
        logMe("ERROR: Bad call to createLogFile")
        return False
    try:
        createDir(logDir)
        path = os.path.join(logDir, fileName)
        with open(path, 'wb') as logFile:
            logFile.write(logStr)
    except Exception, e:
        logMe("ERROR: Log file not successfully created: " + str(e))
        return False
    logMe("COMPLETE: Log file created: " + str(fileName))
    return True
    

def deleteDir(path):
    """Removes a directory at path, and all of its contents. This is silent if path does 
    not exist.
    @return The path if it is deleted; None otherwise"""
    path = str(path)
    if os.path.isdir(path):
        shutil.rmtree(path)
        logMe("COMPLETE: Directory fully deleted: '" + path + "'")
        return path
    

def endl(specialFormat=None):
    """C-inspired convenience function. If specialFormat is set to a string, then this 
    attempts to make sense of it and return its associated newline string. Otherwise, the 
    default is returned. This does not flush the output buffer.
    @return A literal string with the universal newline"""
    if not specialFormat:
        return "\r\n"
    if specialFormat=="html":
        return "<BR>\n"
    elif specialFormat=="linux":
        return "\n"
    else:
        return "\r\n"
    

def getDateTime(dateOrTime = "both", sep="@"):
    """dateOrTime should be 'both', 'date', 'time', or 'milliseconds'. sep should be a 
    string.
    @return A string representing the current date/time in one of the following formats: 
        YYYY-MM-DD<sep>HHMMSS
        YYYY-MM-DD
        HHMMSS
        HHMMSS.mmm"""
    now = datetime.datetime.today()
    if not isString(sep):
        sep = "@"
    dateStr = now.isoformat(sep)
    # Partition at milliseconds
    dateStr, c, milliseconds = dateStr.rpartition(".")
    # ":" is not allowed in directory names
    dateStr = dateStr.replace(":", "")
    dateSplit = dateStr.partition(sep)
    if dateOrTime!="both":
        if dateOrTime=="date":
            return dateSplit[0]
        elif dateOrTime=="time":
            return dateSplit[2]
        elif dateOrTime=="milliseconds":
            return dateSplit[2] + milliseconds
        # Unrecognized param, so warn and return default
        else:
            logMe("WARNING: Bad param passed into getDateTime(); returning default")
    return dateStr
    

def isString(item, *otherItems):
    """@return True if item and all otherItems are strings; False otherwise"""
    if not isinstance(item, basestring):
        return False
    if otherItems:
        for item in otherItems:
            if not isinstance(item, basestring):
                return False
    return True
    

def logMe(strToLog="------------------------------------------------------", \
          quietMode=False):
    """Adds strToLog to the global string logStr (on a new line). If quietMode is omitted 
    or False, then this prints logStr to the console or to Hudson. If nothing is passed, 
    then a line separator is logged and printed."""
    global logStr
    # Ensure that errors don't get thrown when treating strToLog like a string
    strToLog = str(strToLog)
    logStr += endl() + strToLog
    if quietMode:
        # Don't print to the console
        return
    print strToLog
    # Push console output to Hudson
    sys.stdout.flush()
    

def walkDir(path):
    """path should be a directory (either absolute or relative to this script). Starting 
    with path as the root, this searches the directory tree recursively, looking for file  
    names. 
    @return A list of strings, where each string is full path starting at path and ending 
    at each file found during the search"""
    if not os.path.isdir(path):
        logMe("Bad input to walkDir()")
        return[]
    fileArray = []
    for dirpath, dirnames, filenames in os.walk(path):
        if not filenames: # no files exist in this dir
            continue
        for fileName in filenames:
            fileName = os.path.join(dirpath, fileName)
            fileArray.append(fileName)
    return fileArray
    

# Execute MAIN
if __name__ == "__main__":
    main()
