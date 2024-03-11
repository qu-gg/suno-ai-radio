# suno-ai-radio
POC using Selenium on Suno with OBS to host an AI radio station where the next song is generated online while the current one is playing.

#### To run
- Run the main program: <code>python app.py</code>
- Log into your Suno account in the Selenium Chrome instance
- Hit a button in the CMD of the program onced logged in
- Leverage something like OBS to record the browser's audio output

#### How it works
Using Selenium, this program will use a logged-in Chrome instance of Suno and interact with the HTML to both play and generate new songs actively.
It waits the appropriate length of time for the current song to finish before moving onto the next and can be used for a (theoretically) infinite stream given enough credits.

#### Why?
There is no API to hit in Suno yet and it sounded like a fun day project.

#### Limitations
There are a few current limitations that can be addressed:
- Currently only 30-60s clips are used, however a prototype of live-stitching longer songs is added in <code>wip_long_generation.py</code>. This requires some tuning, though.
- Inputs are currently not taken for the song description (short version) or for lyrics and genre (long version). This can be fixed.
