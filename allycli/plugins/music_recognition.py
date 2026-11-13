from io import BytesIO
import tempfile
import urllib.error
import urllib.request
from plugin import plugin, require, alias
from colorama import Fore
from shazamio import Shazam
import pydub
import asyncio
import climage

requirements = ['ffmpeg']
try:
    import pyaudio
    import speech_recognition as sr
except ImportError:
    requirements.append(
        'voice_control_requirements (install portaudio + re-run setup.sh)')


@require(network=True, native=requirements)
@alias("shazam")
@plugin("music recognition")
class MusicRecognition:
    """A tool to recognize music through Shazam API."""

    def __init__(self):
        self.sound_recorded = tempfile.NamedTemporaryFile()
        self.selected_microphone = None
        self.shazam = Shazam()
        self.recognizer = sr.Recognizer()
        self.duration = 15

    def __call__(self, ally, s):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.music_recognition(ally))

    async def music_recognition(self, ally):
        """Main function.

        This function is the main menu, that will run
        until the user says otherwise.
        """

        ally.say('')
        ally.say('This tool will let you recognize a music')
        ally.say('To achieve this, a 15 seconds recording of your microphone is ' +
                   'done and sent to Shazam servers')

        while True:

            self.available_options(ally)
            user_input = ally.input('Your choice: ')
            user_input = user_input.lower()

            if user_input == 'q' or user_input == 'quit' or user_input == '3':
                ally.say("See you next time :D", Fore.CYAN)
                break

            # To select input device
            if user_input == '1':
                self.select_microphone(ally)

            # To recognize a music
            elif user_input == '2':
                await self.recognize_music(ally)

            # For an incorrectly entered option
            else:
                ally.incorrect_option()
                continue

    def available_options(self, ally):
        """
        Message displayed to prompt the user about actions of 
        music recognition plugin.
        """

        ally.say('\nSelect one of the following options:')
        ally.say('1: Select input microphone to use')
        ally.say('2: Record and recognize music')
        ally.say('3: Quit')

    def after_recording_options(self, ally):
        """
        Message displayed to prompt the user about actions 
        after microphone recording.
        """

        ally.say('\nSelect one of the following options:')
        ally.say('1: Play recorded sound')
        ally.say('2: Use the recorded sound for music recognition')
        ally.say('3: Record again')
        ally.say('4: Quit')

    def select_microphone(self, ally):
        """Select input device from the available ones"""

        input_devices = sr.Microphone.list_microphone_names()

        if not input_devices:
            ally.say('There are no input devices available', Fore.RED)
            return None

        ally.say('\nSelect one of following available input devices:')

        for i, val in enumerate(input_devices):
            ally.say(f"{i+1}: {val}")

        selected_input = ally.input_number(
            prompt='Your choice: ',
            rtype=int,
            rmin=1,
            rmax=len(input_devices)
        )

        self.selected_microphone = selected_input-1

        return input_devices[self.selected_microphone]

    async def get_shazam_info(self, ally):
        """
        Get music match from Shazam servers
        If available, draw a pixel art of the cover art
        """

        out = await self.shazam.recognize_song(self.sound_recorded.name)

        if not 'track' in out:
            ally.say('No match found', Fore.RED)
        else:
            ally.say('Match found:', Fore.GREEN)
            if 'images' in out['track'] and 'coverart' in out['track']['images']:
                try:
                    request = urllib.request.urlopen(
                        out['track']['images']['coverart'])
                    downloaded_image = BytesIO(request.read())
                    pixel_art = climage.convert(downloaded_image, width=50)
                    ally.say(pixel_art)
                except urllib.error.URLError:
                    pass
            ally.say(f"Song Title: {str(out['track']['title'])}", Fore.GREEN)
            ally.say(
                f"Song Artist: {str(out['track']['subtitle'])}", Fore.GREEN)

    def play_last_recorded_sound(self, ally):
        """Play the last recorded sound"""

        ally.say('-----Now playing last recorded sound-----', Fore.BLUE)
        mp3_file = pydub.AudioSegment.from_file(
            self.sound_recorded, format="mp3")
        pydub.playback.play(mp3_file)

    async def recognize_music(self, ally):
        """Function that does the music recognition flow"""

        if not self.record_microphone(ally):
            return None

        while True:

            self.after_recording_options(ally)
            user_input = ally.input('Your choice: ')
            user_input = user_input.lower()

            if user_input == 'q' or user_input == 'quit' or user_input == '4':
                break

            # To select input device
            if user_input == '1':
                self.play_last_recorded_sound(ally)

            # To get Shazam music info
            elif user_input == '2':
                await self.get_shazam_info(ally)

            # To record a new sound
            elif user_input == '3':
                self.record_microphone(ally)

            # For an incorrectly entered option
            else:
                ally.incorrect_option()
                continue

    def record_microphone(self, ally):
        """Record microphone input for 15 seconds"""

        # Although not following PEP 8, using is None because it can be 0
        if self.selected_microphone is None:
            ally.say('Microphone not yet selected...', Fore.RED)
            if not self.select_microphone(ally):
                return None

        my_mic = sr.Microphone(device_index=self.selected_microphone)

        with my_mic as source:
            self.sound_recorded.flush()

            ally.say('-----Now Recording for 15 seconds-----', Fore.BLUE)

            audio_recorded = self.recognizer.record(
                source=source, duration=self.duration)

            wav_file = pydub.AudioSegment.from_file(
                file=BytesIO(audio_recorded.get_wav_data()), format="wav")

            wav_file.export(self.sound_recorded, format="mp3")

            return self.sound_recorded
