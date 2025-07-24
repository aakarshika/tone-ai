"""
Audio Processor Module
Handles audio loading, chunking, format conversion, and preprocessing.
"""

import numpy as np
import base64
import io
from typing import Optional, Tuple, List
import logging

# AUDIO DEPENDENCIES
try:
    import soundfile as sf
except ImportError:
    logging.error("soundfile not installed.")
    sf = None

try:
    import ffmpeg
except ImportError:
    logging.error("ffmpeg-python not installed.")
    ffmpeg = None

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Handles audio processing operations including loading, chunking, and format conversion."""
    
    def __init__(self, default_sample_rate: int = 16000):
        self.default_sample_rate = default_sample_rate
        self._validate_dependencies()
    
    def _validate_dependencies(self) -> None:
        """Validate that required audio dependencies are available."""
        if sf is None:
            logger.warning("soundfile not available - audio processing limited")
        if ffmpeg is None:
            logger.warning("ffmpeg-python not available - format conversion limited")
    
    def decode_base64_audio(self, audio_b64: str) -> Tuple[np.ndarray, int]:
        """
        Decode base64 audio data to numpy array.
        
        Args:
            audio_b64: Base64 encoded audio data
            
        Returns:
            Tuple of (audio_array, sample_rate)
        """
        try:
            audio_bytes = base64.b64decode(audio_b64)
            audio_np = np.frombuffer(audio_bytes, dtype=np.float32)
            return audio_np, self.default_sample_rate
        except Exception as e:
            logger.error(f"Failed to decode base64 audio: {e}")
            raise
    
    def convert_to_wav(self, audio_np: np.ndarray, sample_rate: int) -> bytes:
        """
        Convert numpy audio array to WAV format bytes.
        
        Args:
            audio_np: Audio data as numpy array
            sample_rate: Sample rate of the audio
            
        Returns:
            WAV format bytes
        """
        if sf is None:
            raise RuntimeError("soundfile not available for WAV conversion")
        
        try:
            with io.BytesIO() as wav_io:
                sf.write(wav_io, audio_np, sample_rate, format='WAV')
                wav_io.seek(0)
                return wav_io.read()
        except Exception as e:
            logger.error(f"Failed to convert audio to WAV: {e}")
            raise
    
    def chunk_audio(self, audio_np: np.ndarray, sample_rate: int, 
                   chunk_duration: float = 5.0, overlap_duration: float = 0.5) -> List[Tuple[np.ndarray, float]]:
        """
        Split audio into overlapping chunks.
        
        Args:
            audio_np: Audio data as numpy array
            sample_rate: Sample rate of the audio
            chunk_duration: Duration of each chunk in seconds
            overlap_duration: Overlap between chunks in seconds
            
        Returns:
            List of (chunk_array, start_time) tuples
        """
        chunk_samples = int(chunk_duration * sample_rate)
        step_samples = int((chunk_duration - overlap_duration) * sample_rate)
        
        chunks = []
        for i in range(0, len(audio_np), step_samples):
            end = min(i + chunk_samples, len(audio_np))
            chunk = audio_np[i:end]
            
            # Skip chunks that are too short
            if len(chunk) < sample_rate * 0.5:  # Minimum 0.5 seconds
                continue
                
            start_time = i / sample_rate
            chunks.append((chunk, start_time))
        
        logger.info(f"Split audio into {len(chunks)} chunks of {chunk_duration}s with {overlap_duration}s overlap")
        return chunks
    
    def normalize_audio(self, audio_np: np.ndarray) -> np.ndarray:
        """
        Normalize audio to prevent clipping and improve processing.
        
        Args:
            audio_np: Audio data as numpy array
            
        Returns:
            Normalized audio array
        """
        if len(audio_np) == 0:
            return audio_np
        
        # Normalize to [-1, 1] range
        max_val = np.max(np.abs(audio_np))
        if max_val > 0:
            return audio_np / max_val
        return audio_np
    
    def resample_audio(self, audio_np: np.ndarray, original_rate: int, target_rate: int) -> np.ndarray:
        """
        Resample audio to target sample rate.
        
        Args:
            audio_np: Audio data as numpy array
            original_rate: Original sample rate
            target_rate: Target sample rate
            
        Returns:
            Resampled audio array
        """
        if original_rate == target_rate:
            return audio_np
        
        if ffmpeg is None:
            logger.warning("ffmpeg not available for resampling - returning original")
            return audio_np
        
        try:
            # Use ffmpeg for resampling
            with io.BytesIO() as input_io:
                sf.write(input_io, audio_np, original_rate, format='WAV')
                input_io.seek(0)
                
                with io.BytesIO() as output_io:
                    (
                        ffmpeg
                        .input('pipe:', format='wav')
                        .output('pipe:', format='wav', ar=target_rate)
                        .run(input=input_io.read(), output=output_io, quiet=True)
                    )
                    output_io.seek(0)
                    resampled_audio, _ = sf.read(output_io)
                    return resampled_audio
        except Exception as e:
            logger.error(f"Failed to resample audio: {e}")
            return audio_np 