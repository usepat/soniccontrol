@defgroup VsCode
@ingroup ProjectSetup
@addtogroup VsCode
@{

# VsCode {#VsCode}

[Vscode](https://code.visualstudio.com/) is an Text editor / IDE for programming.
Here we briefly describe some important features useful for this project. 
Also checkout their extensive [documentation](https://code.visualstudio.com/docs) for more details over their features.

## Source Control

By using [Git](https://git-scm.com/) we can make versions of the software and track the progress. Also it is essential for collaboration.  
The *Source Control Tab* discovers automatically the repository and lets you view the changes that you made. You can make there directly commits.
If there are merge conflicts you can view them directly in vscode in a [Two Way Merge View](https://blog.git-init.com/the-magic-of-3-way-merge/) and resolve them there.

For getting an overview over the different branches the [GitGraph](https://marketplace.visualstudio.com/items?itemName=mhutchie.git-graph) extension is very useful

## Debugging

In the *Debugging Tab* you can run and debug your applications.
For that you need to provide a configuration in your *.vscode/launch.json* file. 
It tells Vscode on what debugger to use, with what arguments.
When starting debugging you can use the *Debug Console* for interacting with the program and you can set different [Breakpoints](https://code.visualstudio.com/docs/python/python-tutorial#_configure-and-run-the-debugger) to stop execution and inspect the program state. You can also have conditional Breakpoints and watch variables and expressions.

## Tests

Tests are discovered automatically by vscode (Sometimes you need an extension tho). In the *Testing Tab* you have an overview over all tests and tests stuites and run them individually. The results will then be shown in the *Test Console*.

## Command Palette

You can open the *Command Palette* with `Ctrl+P`.  
You can use to go to lines, search for files and words, execute tasks provided by yourself and the installed extensions.
For example: `>Python: Select Interpreter`

## Tasks

You can define tasks in *.vscode/tasks.json* and then execute them via the *Command Palette* `task: MySuperAwesomeTask`.  
They are very handy for automating stuff, like [building an exe](@ref Deployment).

## Extensions

Extensions are used for adding functionality to Vscode.
There are dozens of extensions for different stuff and different languages. 
There are also themes that let you personalize your ide.

The important thing is that all extensions valuable to this project should be declared inside *.vscode/extensions.json*. Like this we ensure that we have all necessary tools available for this project. Like we have a *requirements.txt* file to ensure that all necessary libraries are available and listed. Dependencies have to be listed somewhere and easily installable.  

By opening the *Command Palette* you can install all recommended extensions via `Extensions: Install Workspace Recommended Extensions`.

### Serial Monitor Extension

Important extension to use a `Serial Monitor Console` directly. Needed to communicate with the device. Needed for debugging.

## Settings

In *.vscode/settings.json* you can specify configuration and settings for your extensions.

@}