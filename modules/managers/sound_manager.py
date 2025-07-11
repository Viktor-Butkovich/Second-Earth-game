# Contains sound effect and music management singleton

import random
import pygame
import os
import pydub
import numpy as np
import pedalboard
import io
from modules.constants import constants, status, flags


class sound_manager:
    """
    Object that controls sounds
    """

    def __init__(self):
        """
        Initializes this object
        """
        self.default_music_dict = {
            "earth": [
                ("generic/" + current_song[:-4])
                for current_song in os.listdir("sounds/music/generic")
            ],  # remove file extensions
            "main menu": ["main theme"],
        }
        self.previous_state = None
        self.previous_song = None

    def busy(self):
        """
        Description:
            Returns whether the Pygame mixer is currently busy
        Input:
            None
        Output:
            bool: Returns whether the Pygame mixer is currently busy
        """
        return pygame.mixer.get_busy()

    def fadeout(self, ms=500):
        """
        Fades out all active sound channels over the inputted number of milliseconds
        """
        pygame.mixer.fadeout(ms)

    def apply_radio_effect(self, sound: pygame.mixer.Sound) -> pygame.mixer.Sound:
        """
        Description:
            Applies a radio effect to the inputted sound
        Input:
            pygame.mixer.Sound sound: Sound to apply the radio effect to
        Output:
            pygame.mixer.Sound: Returns the sound with the radio effect applied
        """
        # Convert pygame sound to pydub audio segment
        sample_rate = 44100
        audio: pydub.AudioSegment = pydub.AudioSegment.from_file(
            io.BytesIO(sound.get_raw()),
            format="raw",
            frame_rate=sample_rate,
            sample_width=2,
            channels=2,
        )
        # Remove silent starts and ends of the audio
        audio = audio.strip_silence(silence_len=100, silence_thresh=-40)

        # Use pedalboard to resample and decrease the quality of the audio
        samples = np.array(audio.get_array_of_samples())

        # Convert static_fraction of the samples to random static
        static_fraction = 0.3
        num_samples_to_change = round(len(samples) * static_fraction)
        indices_to_change = np.random.choice(
            len(samples), num_samples_to_change, replace=False
        )
        samples[indices_to_change] = np.random.randint(
            300, 1500, num_samples_to_change, dtype=np.int16
        )

        resample_fraction = 0.1
        bitcrush_magnitude = 10
        low_cutoff, high_cutoff = 300, 3000
        reverb_magnitude = 0.2
        compressor_db, compressor_ratio = -10.0, 2.0
        board = pedalboard.Pedalboard(
            [
                pedalboard.Resample(
                    target_sample_rate=round(audio.frame_rate * resample_fraction)
                ),  # Decrease horizontal quality
                pedalboard.Bitcrush(bitcrush_magnitude),  # Decrease vertical quality
                pedalboard.HighpassFilter(
                    cutoff_frequency_hz=low_cutoff
                ),  # Remove low frequencies
                pedalboard.LowpassFilter(
                    cutoff_frequency_hz=high_cutoff
                ),  # Remove high frequencies
                pedalboard.Reverb(room_size=reverb_magnitude),  # Add slight reverb
                pedalboard.Compressor(
                    threshold_db=compressor_db, ratio=compressor_ratio
                ),  # Compress high and low volumes
            ]
        )

        # Convert to 32-bit float and apply pedalboard effects
        effected = board(
            samples.astype(np.float32) / 32768.0,
            sample_rate=sample_rate // 2,
            buffer_size=8192,
            reset=True,
        )

        effected = (effected * 32768.0).astype(np.int16)  # Convert back to 16-bit int

        sound = pygame.mixer.Sound(
            buffer=effected.tobytes(),
        )  # Convert edited pedalboard audio segment back to pygame sound

        return sound

    def play_sound(
        self, file_name: str, volume: float = 0.3, radio_effect: bool = False
    ):
        """
        Description:
            Plays the sound effect from the inputted file
        Input:
            string file_name: Name of .ogg/.wav file to play sound of
            double volume = 0.3: Volume from 0.0 to 1.0 to play sound at - mixer usually uses a default of 1.0
            bool radio_effect = False: Whether to apply a radio effect to the sound
        Output:
            Channel: Returns the pygame mixer Channel object that the sound was played on
        """
        if not file_name:
            return None

        try:
            current_sound = pygame.mixer.Sound(f"sounds/{file_name}.ogg")
        except:
            current_sound = pygame.mixer.Sound(f"sounds/{file_name}.wav")

        if radio_effect:
            current_sound = self.apply_radio_effect(current_sound)

        channel = current_sound.play()
        if channel:
            try:
                channel.set_volume(volume)
            except:
                raise Exception(
                    f"Error: Could not set volume to {volume} for sound {file_name}"
                )
        return channel

    def queue_sound(
        self,
        file_name: str,
        channel: pygame.mixer.Channel,
        volume: float = 0.3,
        radio_effect: bool = False,
    ):
        """
        Description:
            Queues the sound effect from the inputted file to be played once the inputted channel is done with its current sound
        Input:
            string file_name: Name of .ogg/.wav file to play sound of
            Channel channel: Pygame mixer channel to queue the sound in
            double volume = 0.3: Volume from 0.0 to 1.0 to play sound at - mixer usually uses a default of 1.0
            bool radio_effect = False: Whether to apply a radio effect to the sound
        Output:
            None
        """
        try:
            current_sound = pygame.mixer.Sound(f"sounds/{file_name}.ogg")
        except:
            current_sound = pygame.mixer.Sound(f"sounds/{file_name}.wav")
        if radio_effect:
            current_sound = self.apply_radio_effect(current_sound)
        current_sound.set_volume(volume)
        channel.queue(current_sound)

    def play_music(self, file_name, volume=-0.1):
        """
        Description:
            Starts playing the music from the inputted file, replacing any current music
        Input:
            string file_name: Name of .wav file to play music of
            double volume = -0.1: Volume from 0.0 to 1.0 to play sound at - replaces negative or absent volume input with default
        Output:
            None
        """
        if volume < 0:  # negative volume value -> use default
            volume = constants.default_music_volume
        try:
            pygame.mixer.music.load(f"sounds/music/{file_name}.ogg")
        except:
            pygame.mixer.music.load(f"sounds/music/{file_name}.wav")
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(0)  # music loops when loop argument is -1

    def music_transition(self, file_name, time_interval=0.75):
        """
        Description:
            Fades out the current song and plays a new song at the previous volume
        Input:
            string file_name: Name of .wav file to play music of, or None if music should fade out but not restart
            double time_interval = 0.75: Time to wait between each volume change event
        Output:
            None
        """
        original_volume = constants.default_music_volume
        pygame.mixer.music.set_volume(original_volume)
        time_passed = 0
        if (
            pygame.mixer.music.get_busy()
        ):  # only delay starting music for fade out if there is any current music to fade out
            for i in range(1, 5):
                time_passed += time_interval  # with each interval, time_interval time passes and volume decreases by 0.25
                constants.JobScheduler.schedule_job(
                    pygame.mixer.music.set_volume,
                    [original_volume * (1 - (0.25 * i))],
                    time_passed,
                )

        if file_name:
            time_passed += time_interval
            constants.JobScheduler.schedule_job(
                self.play_music, [file_name, 0], time_passed
            )
            for i in range(1, 5):
                constants.JobScheduler.schedule_job(
                    pygame.mixer.music.set_volume,
                    [original_volume * (0.25 * i)],
                    time_passed,
                )
                time_passed += time_interval  # with each interval, time_interval time passes and volume increases by 0.25
        else:
            constants.JobScheduler.schedule_job(
                pygame.mixer.music.stop, [], time_passed
            )
            constants.JobScheduler.schedule_job(
                pygame.mixer.music.unload, [], time_passed
            )
            constants.JobScheduler.schedule_job(
                pygame.mixer.music.set_volume, [original_volume], time_passed
            )

    def dampen_music(self, time_interval=0.5):
        """
        Description:
            Temporarily reduces the volume of the music to allow for other sounds
        Input:
            double time_interval = 0.5: Time to wait between each volume change event
        Output:
            None
        """
        constants.JobScheduler.clear()
        original_volume = constants.default_music_volume
        pygame.mixer.music.set_volume(0)
        time_passed = 0
        for i in range(-5, 6):
            time_passed += time_interval
            if i > 0:
                constants.JobScheduler.schedule_job(
                    pygame.mixer.music.set_volume,
                    [original_volume * i * 0.1],
                    time_passed,
                )

    def play_random_music(self, current_state, previous_song=None):
        """
        Description:
            Plays random music depending on the current state of the game, like 'main menu' or 'earth'
        Input:
            string current_state: Descriptor for the current state of the game to play music for
            string previous_song: The previous song that just ended, if any, to avoid playing it again unless it is the only option
        Output:
            None
        """
        self.previous_song = None
        original_state = self.previous_state
        if not (self.previous_state == current_state):
            state_changed = True
        else:
            state_changed = False
        self.previous_state = current_state
        possible_songs = self.default_music_dict[current_state]
        if len(possible_songs) == 1:
            chosen_song = random.choice(possible_songs)
        elif len(possible_songs) > 0:
            chosen_song = random.choice(possible_songs)
            if previous_song:  # Plays different song if multiple choices available
                while chosen_song == previous_song:
                    chosen_song = random.choice(possible_songs)
        else:
            chosen_song = None
        if (chosen_song and not state_changed) or (not original_state):
            # Start music immediately on startup or if last song finished
            # Should result in music starting immediately when main menu starts up, while waiting until after loading/creating new game
            self.play_music(chosen_song)
        else:  # Otherwise, fade out current music and fade in new music
            self.music_transition(chosen_song, time_interval=0.75)
        self.previous_song = chosen_song

    def song_done(self):
        """
        Called when a song finishes, plays a new random song for the same state, with the new song being different if possible
        """
        self.play_random_music(self.previous_state, self.previous_song)

    def start_looping_sound(self, file_name: str, volume: float = 0.3):
        """
        Description:
            Loops the sound effect from the inputted file until told to stop
        Input:
            string file_name: Name of .ogg/.wav file to play sound of
            double volume = 0.3: Volume from 0.0 to 1.0 to play sound at - mixer usually uses a default of 1.0
            bool radio_effect = False: Whether to apply a radio effect to the sound
        Output:
            Channel: Returns the pygame mixer Channel object that the sound is played on
                Make sure this channel is tracked to allow stopping it later
        """
        if not file_name:
            return None

        try:
            current_sound = pygame.mixer.Sound(f"sounds/{file_name}.ogg")
        except:
            current_sound = pygame.mixer.Sound(f"sounds/{file_name}.wav")
        channel = pygame.mixer.find_channel(force=True)
        channel.play(current_sound, loops=-1)
        if channel:
            try:
                channel.set_volume(volume)
            except:
                raise Exception(
                    f"Error: Could not set volume to {volume} for sound {file_name}"
                )
        return channel

    def stop_looping_sound(self, channel: pygame.mixer.Channel):
        """
        Description:
            Stops the looping sound on the given channel - use to stop a looped sound
        Input:
            Channel channel: Pygame mixer channel to stop the sound on
        Output:
            None
        """
        if channel:
            channel.fadeout(2000)
