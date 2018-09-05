# lightshow

This code is in a very rough state and a lot of values are still hardcoded. It is mostly provided right now as something educational if you want to see how the audio is being processed. It will be updated in the near future to be more reusable and user friendly. Look at `test.py` to see how it all works.

* Download [aubio](https://aubio.org/) and make sure you can run it with `aubio -h`

* Use aubio to calculate the melbands and offsets of a wav file (mp3's should work but I'm on Linux and didn't want to install some stuff to make them work so I stuck with wav's).

* In test.py, edit the file names for the melbands and offsets.

* Run the program with `python test.py <name of wav file>`

* There will be a pause while the melbands file is read in and some calculations are performed.

* The song will start playing and the values for the various channels will be printed to the terminal.

* There is Arduino code in the `test_sketch` folder. It requires some extra hardware that I will provide details about later.
