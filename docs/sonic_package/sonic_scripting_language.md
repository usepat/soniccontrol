@defgroup SonicScriptingLanguage
@ingroup SonicPackage
@addtogroup SonicScriptingLanguage

@{

# Sonic Scripting Language {#SonicScriptingLanguage}

## Brief Description

The Sonic Scripting Language is used to make scripts that control the amp. The language is very basic at the moment and gets executed line for line by an interpreter.

## Commands

Each line is a statement in the language. 
If a statement starts with `!`, `?`, `-` or `=` it is interpreted as a command and the line gets send directly to the device as a command. For example `!freq=100`.

But for a better readability there were also custom commands defined: 
- `on`: sets the signal to on
- `off`: sets the signal to off
- `frequency` `[FREQ]`
- `gain` `[GAIN]`
- `hold` `[TIME s/ms]`: stops execution for amount of time and then continues
- `ramp_freq`: I am too lazy to describe this

## Loops

You can make loops with the following construct:

```
startloop [TIMES]
    [STATEMENTS]
endloop
```

Loops can be nested. A loop gets executed the number of `TIMES` specified.
If `TIMES`  is not given, then the loop runs endless.

@}