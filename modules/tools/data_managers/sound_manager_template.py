import random
import pygame
import os
from modules.constants import constants, status, flags


class sound_manager_template:
    """
    Object that controls sounds
    """

    def __init__(self):
        """
        Description:
            Initializes this object
        Input:
            None
        Output:
            None
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
        Description:
            Fades out all active sound channels over the inputted number of milliseconds
        Input:
            None
        Output:
            None
        """
        pygame.mixer.fadeout(ms)

    def play_sound(self, file_name, volume=0.3):
        """
        Description:
            Plays the sound effect from the inputted file
        Input:
            string file_name: Name of .ogg/.wav file to play sound of
            double volume = 0.3: Volume from 0.0 to 1.0 to play sound at - mixer usually uses a default of 1.0
        Output:
            Channel: Returns the pygame mixer Channel object that the sound was played on
        """
        try:
            current_sound = pygame.mixer.Sound(f"sounds/{file_name}.ogg")
        except:
            current_sound = pygame.mixer.Sound(f"sounds/{file_name}.wav")
        current_sound.set_volume(volume)
        channel = pygame.mixer.find_channel(force=True)
        channel.play(current_sound)
        return channel

    def queue_sound(self, file_name, channel, volume=0.3):
        """
        Description:
            Queues the sound effect from the inputted file to be played once the inputted channel is done with its current sound
        Input:
            string file_name: Name of .ogg/.wav file to play sound of
            Channel channel: Pygame mixer channel to queue the sound in
            double volume = 0.3: Volume from 0.0 to 1.0 to play sound at - mixer usually uses a default of 1.0
        Output:
            None
        """
        try:
            current_sound = pygame.mixer.Sound(f"sounds/{file_name}.ogg")
        except:
            current_sound = pygame.mixer.Sound(f"sounds/{file_name}.wav")
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
                constants.event_manager.add_event(
                    pygame.mixer.music.set_volume,
                    [original_volume * (1 - (0.25 * i))],
                    time_passed,
                )

        if file_name:
            time_passed += time_interval
            constants.event_manager.add_event(
                self.play_music, [file_name, 0], time_passed
            )
            for i in range(1, 5):
                constants.event_manager.add_event(
                    pygame.mixer.music.set_volume,
                    [original_volume * (0.25 * i)],
                    time_passed,
                )
                time_passed += time_interval  # with each interval, time_interval time passes and volume increases by 0.25
        else:
            constants.event_manager.add_event(pygame.mixer.music.stop, [], time_passed)
            constants.event_manager.add_event(
                pygame.mixer.music.unload, [], time_passed
            )
            constants.event_manager.add_event(
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
        constants.event_manager.clear()
        original_volume = constants.default_music_volume
        pygame.mixer.music.set_volume(0)
        time_passed = 0
        for i in range(-5, 6):
            time_passed += time_interval
            if i > 0:
                constants.event_manager.add_event(
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
        Description:
            Called when a song finishes, plays a new random song for the same state, with the new song being different if possible
        Input:
            None
        Output:
            None
        """
        self.play_random_music(self.previous_state, self.previous_song)
