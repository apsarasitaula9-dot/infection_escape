# generate_assets.py
"""
Programmatically generates 16-bit PCM mono WAV audio assets for the game.
This eliminates dependencies on external file downloads, keeping the game fully portable.
"""

import os
import wave
import struct
import math
import random

def save_wav(filename, samples, sample_rate=22050):
    """
    Saves a list of audio sample floats (-1.0 to 1.0) into a 16-bit mono WAV file.
    """
    dir_path = os.path.dirname(filename)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
        
    print(f"Generating: {filename}...")
    try:
        with wave.open(filename, 'w') as f:
            f.setnchannels(1)       # Mono
            f.setsampwidth(2)       # 16-bit (2 bytes)
            f.setframerate(sample_rate)
            
            # Pack samples into binary 16-bit signed integers
            binary_data = bytearray()
            for s in samples:
                # Clamp sample to -1.0 to 1.0
                s_clamped = max(-1.0, min(1.0, s))
                # Scale to 16-bit range
                val = int(s_clamped * 32767)
                binary_data.extend(struct.pack('<h', val))
                
            f.writeframesraw(binary_data)
    except Exception as e:
        print(f"Error generating {filename}: {e}")

def generate_gunshot():
    """Generates a gunshot sound using decaying white noise and a low click."""
    duration = 0.3
    sr = 22050
    num_samples = int(duration * sr)
    samples = []
    
    for i in range(num_samples):
        t = i / sr
        # Quick exponential decay
        envelope = math.exp(-15 * t)
        # White noise
        noise = random.uniform(-1.0, 1.0)
        # Low frequency punch
        punch = math.sin(2 * math.pi * 90 * t) * math.exp(-120 * t)
        
        samples.append((noise * 0.75 + punch * 0.25) * envelope)
    return samples

def generate_growl():
    """Generates a zombie growl sound using frequency-modulated low frequencies and noise."""
    duration = 0.8
    sr = 22050
    num_samples = int(duration * sr)
    samples = []
    
    for i in range(num_samples):
        t = i / sr
        # Pitch wobbling/vibrato
        vibrato = math.sin(2 * math.pi * 28 * t) * 18
        freq = 85 + vibrato
        
        # Base wave
        base_wave = math.sin(2 * math.pi * freq * t)
        # Add raspy noise
        noise = random.uniform(-1.0, 1.0) * 0.4
        
        # Envelope: quick attack, slow decay
        if t < 0.1:
            envelope = t / 0.1
        else:
            envelope = math.exp(-3 * (t - 0.1))
            
        samples.append((base_wave * 0.6 + noise * 0.4) * envelope * 0.7)
    return samples

def generate_infection():
    """Generates an infection sound using a descending square wave and low-frequency wobble."""
    duration = 0.6
    sr = 22050
    num_samples = int(duration * sr)
    samples = []
    
    for i in range(num_samples):
        t = i / sr
        # Descending pitch
        freq = 380 - (t * 400)
        if freq < 40:
            freq = 40
            
        # Frequency modulation
        mod = math.sin(2 * math.pi * 12 * t) * 0.2
        sine_val = math.sin(2 * math.pi * freq * t * (1.0 + mod))
        # Hard square wave clipping for raw retro sound
        wave_val = 1.0 if sine_val >= 0 else -1.0
        
        # Decaying volume envelope
        envelope = math.exp(-4 * t)
        samples.append(wave_val * 0.35 * envelope)
    return samples

def generate_loot():
    """Generates a looting pickup sound (rising double chime)."""
    duration = 0.15
    sr = 22050
    num_samples = int(duration * sr)
    samples = []
    
    for i in range(num_samples):
        t = i / sr
        # Rapidly rising pitch
        freq = 700 + (t * 3000)
        wave_val = math.sin(2 * math.pi * freq * t)
        
        # Envelope
        envelope = math.exp(-12 * t)
        samples.append(wave_val * 0.4 * envelope)
    return samples

def generate_rescue():
    """Generates a pleasant rescue sound (arpeggiated major chord)."""
    duration = 0.4
    sr = 22050
    num_samples = int(duration * sr)
    samples = []
    
    # C major triad: C5 (523.25), E5 (659.25), G5 (783.99), C6 (1046.50)
    notes = [523.25, 659.25, 783.99, 1046.50]
    
    for i in range(num_samples):
        t = i / sr
        note_idx = int((t / duration) * len(notes))
        if note_idx >= len(notes):
            note_idx = len(notes) - 1
            
        freq = notes[note_idx]
        # Main sine wave + a bit of triangle overlay for sweetness
        wave_val = math.sin(2 * math.pi * freq * t)
        tri_val = abs((t * freq) % 1 - 0.5) * 4 - 1
        
        envelope = 1.0 - (t / duration)
        samples.append((wave_val * 0.7 + tri_val * 0.3) * envelope * 0.3)
    return samples

def generate_click():
    """Generates a brief click/tick sound for UI."""
    duration = 0.05
    sr = 22050
    num_samples = int(duration * sr)
    samples = []
    
    for i in range(num_samples):
        t = i / sr
        # High frequency sine decay
        wave_val = math.sin(2 * math.pi * 2200 * t)
        envelope = math.exp(-90 * t)
        samples.append(wave_val * 0.3 * envelope)
    return samples

def generate_hurt():
    """Generates a flesh impact/grunt sound."""
    duration = 0.2
    sr = 22050
    num_samples = int(duration * sr)
    samples = []
    
    for i in range(num_samples):
        t = i / sr
        # Descending grunt pitch
        freq = 180 - (t * 500)
        if freq < 50:
            freq = 50
            
        wave_val = math.sin(2 * math.pi * freq * t)
        # Mix in rough red-noise approximation
        noise = random.uniform(-1.0, 1.0) * 0.5
        
        envelope = math.exp(-18 * t)
        samples.append((wave_val * 0.5 + noise * 0.5) * envelope * 0.5)
    return samples

def generate_music():
    """Generates a looping dark-synth soundtrack (8.0 seconds)."""
    duration = 8.0
    sr = 22050
    num_samples = int(duration * sr)
    samples = []
    
    # Chord progression (A minor, F major, G major, E minor)
    # Bass notes: A2 (110.0), F2 (87.3), G2 (98.0), E2 (82.4)
    bass_freqs = [110.0, 87.3, 98.0, 82.4]
    
    # Melodic motif in A minor
    melody_notes = [440.0, 523.25, 659.25, 587.33, 523.25, 440.0, 392.00, 329.63]
    
    for i in range(num_samples):
        t = i / sr
        bar_idx = int(t / 2.0) % 4
        
        # Bass synth: sine + octave harmonic + third harmonic
        b_freq = bass_freqs[bar_idx]
        bass_wave = math.sin(2 * math.pi * b_freq * t)
        bass_wave += 0.4 * math.sin(2 * math.pi * (2 * b_freq) * t)
        bass_wave += 0.2 * math.sin(2 * math.pi * (3 * b_freq) * t)
        # Distort bass slightly by clipping
        bass_wave = max(-1.0, min(1.0, bass_wave * 1.2))
        bass_volume = 0.2
        
        # Kick drum beat on every quarter note (0.5s intervals)
        beat_t = t % 0.5
        kick_wave = 0.0
        if beat_t < 0.18:
            # Descending frequency sweep
            k_freq = 160 * math.exp(-25 * beat_t)
            kick_wave = math.sin(2 * math.pi * k_freq * beat_t) * math.exp(-15 * beat_t)
        kick_volume = 0.35
        
        # Snare/hi-hat click on off-beat (0.25s intervals offset by 0.25)
        hat_t = (t - 0.25) % 0.5
        hat_wave = 0.0
        if hat_t < 0.06:
            hat_wave = random.uniform(-1.0, 1.0) * math.exp(-70 * hat_t)
        hat_volume = 0.1
        
        # Melodic synthesizer (note change every 1.0s)
        mel_t = t % 1.0
        mel_wave = 0.0
        note_idx = int(t) % len(melody_notes)
        m_freq = melody_notes[note_idx]
        
        # Play note with a decaying envelope
        if mel_t < 0.7:
            # Square wave melody for retro synth vibe
            m_sine = math.sin(2 * math.pi * m_freq * t)
            mel_wave = (1.0 if m_sine >= 0 else -1.0) * math.exp(-4 * mel_t)
            # Add delay/echo effect (simulated)
            echo_t = mel_t - 0.25
            if echo_t > 0:
                echo_sine = math.sin(2 * math.pi * m_freq * (t - 0.25))
                mel_wave += 0.4 * (1.0 if echo_sine >= 0 else -1.0) * math.exp(-4 * echo_t)
        mel_volume = 0.08
        
        # Mix audio channels
        mixed_val = (
            (bass_wave * bass_volume) +
            (kick_wave * kick_volume) +
            (hat_wave * hat_volume) +
            (mel_wave * mel_volume)
        )
        samples.append(mixed_val)
        
    return samples

def generate_all_sounds():
    """Generates and saves all WAV audio files in assets/sounds/."""
    # Ensure assets directory exists
    os.makedirs("assets/sounds", exist_ok=True)
    
    sound_generators = {
        "assets/sounds/gunshot.wav": generate_gunshot,
        "assets/sounds/zombie_growl.wav": generate_growl,
        "assets/sounds/infection.wav": generate_infection,
        "assets/sounds/loot.wav": generate_loot,
        "assets/sounds/rescue.wav": generate_rescue,
        "assets/sounds/click.wav": generate_click,
        "assets/sounds/hurt.wav": generate_hurt,
        "assets/sounds/bg_music.wav": generate_music
    }
    
    for path, generator in sound_generators.items():
        if not os.path.exists(path):
            samples = generator()
            save_wav(path, samples)
        else:
            print(f"Skipping (already exists): {path}")
            
    print("All audio assets successfully generated!")

if __name__ == "__main__":
    generate_all_sounds()
