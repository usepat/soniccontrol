## SonicMeasure

SonicMeasure in the context of SonicControl is a software tool process to collect spectrum data from a SonicAmp and plotting the data contentiously in an animating plot. The concrete data that is being plotted is U_rms [mV], I_rms [mA], Phase [degree] on the y-axis depending on the frequency [Hz] on the x-axis. @SonicSTS could maybe comment some pictures of some older versions of SonicMeasure.

### Requirements 

- [ ] The user can set up the conditions for the SonicAmp behaviour during the SonicMeasure data collection and plotting 
  - [ ] The user can set up a ramping condition for the SonicMeasure
    - [ ] Start frequency, Stop frequency, Step (resolution) frequency
    - [ ] Holding time during that the signal is turned on
    - [ ] Holding time during that the signal is turned off (defaults to 0 ms)
      - [ ] On-Holding as well as Off-Holding should be possible to set up in milliseconds (ms) or in seconds (s).
    - [ ] The gain that is being set for the whole procedure
    - [ ] The number of times this ramp should be repeated
    - Keep in mind, that this format was used but not updated with the new firmware. @DavidWild02 and other SCRUM members should talk about the possibilty of the behaviour changing.
    - Also, although the ramping procedure was moved into the firmware, the old ramping behaviour (being in soniccontrol) should probably be also supported for older legacy amps. This information should be clarified with @TechHeadusePAT.
  - [ ] The user can activate a "scripting mode", that disables the ramping setup when checked and uses the written script in the scripting tab. During the collection and plotting of data, the script is being run parallel to SonicMeasure.
- [ ] After the spectrum was generated, the user can save the graph or/ and copy the dataset (.csv file e.g.) to another location.
- [ ] After the specturm was generated, the user can restart the SonicMeasure or reset everything to set up new values.
- [ ] Traditionally - is the urms resembled in blue, irms in red and phase in green.
- [ ] Regarding the concrete look of the graph, talk with @guessy-git and @TechHeadusePAT and @SonicSTS. One issue talks about that in #67.
- [ ] *Important for crossplatform*: This part is of SonicControl is being recognized as the most troublesome part for running software on MacOS. Due to #56, SonicMeasure should someday be able to run on a mac.
  - Keep in mind, that a written matplotlib logic is extremly tedious to refactor for apple hardware, because of the very in depth problems of macintosh. Therefore, it is recommended to test the plotting behaviour on these computers parallel to the development. 