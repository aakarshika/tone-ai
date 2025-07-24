"""
Transcription Module
Handles speech-to-text processing using Whisper models.
"""

import io
from typing import Optional, List, Dict, Any
import logging

# SPEECH-TO-TEXT DEPENDENCIES
try:
    from faster_whisper import WhisperModel
except ImportError:
    logging.error("faster-whisper not installed.")
    WhisperModel = None

logger = logging.getLogger(__name__)


class TranscriptionProcessor:
    """Handles speech-to-text transcription using Whisper models."""
    
    def __init__(self, model_size: str = "tiny", device: str = "cpu", compute_type: str = "int8"):
        """
        Initialize transcription processor.
        
        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
            device: Device to run on ("cpu", "cuda")
            compute_type: Compute type for quantization ("int8", "float16", "float32")
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the Whisper model."""
        if WhisperModel is None:
            logger.error("faster-whisper not available")
            return
        
        try:
            self.model = WhisperModel(
                self.model_size, 
                device=self.device, 
                compute_type=self.compute_type
            )
            logger.info(f"Whisper {self.model_size} model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.model = None
    
    def transcribe_audio(self, audio_bytes: bytes, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio bytes to text.
        
        Args:
            audio_bytes: Audio data in WAV format
            language: Language code (optional, auto-detect if None)
            
        Returns:
            Dictionary with transcription results
        """
        if self.model is None:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            # Create BytesIO object for Whisper
            audio_io = io.BytesIO(audio_bytes)
            
            # Transcribe with Whisper
            segments, info = self.model.transcribe(
                audio_io,
                language=language,
                beam_size=5,
                best_of=5
            )
            
            # Extract text and timing information
            text_segments = []
            full_text = ""
            
            for segment in segments:
                segment_data = {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                    "words": getattr(segment, 'words', [])
                }
                text_segments.append(segment_data)
                full_text += segment.text.strip() + " "
            
            result = {
                "text": full_text.strip(),
                "segments": text_segments,
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration
            }
            
            logger.info(f"Transcribed {len(audio_bytes)} bytes to {len(full_text)} characters")
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    def transcribe_chunk(self, audio_bytes: bytes, chunk_idx: int, 
                        language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe a single audio chunk.
        
        Args:
            audio_bytes: Audio chunk data in WAV format
            chunk_idx: Index of the chunk
            language: Language code (optional)
            
        Returns:
            Dictionary with chunk transcription results
        """
        result = self.transcribe_audio(audio_bytes, language)
        result["chunk_idx"] = chunk_idx
        return result
    
    def get_available_models(self) -> List[str]:
        """Get list of available Whisper model sizes."""
        return ["tiny", "base", "small", "medium", "large"]
    
    def is_model_loaded(self) -> bool:
        """Check if the Whisper model is loaded."""
        return self.model is not None
    
    def reload_model(self, model_size: Optional[str] = None, 
                    device: Optional[str] = None, 
                    compute_type: Optional[str] = None) -> bool:
        """
        Reload the Whisper model with new parameters.
        
        Args:
            model_size: New model size (optional)
            device: New device (optional)
            compute_type: New compute type (optional)
            
        Returns:
            True if reload successful, False otherwise
        """
        if model_size:
            self.model_size = model_size
        if device:
            self.device = device
        if compute_type:
            self.compute_type = compute_type
        
        try:
            self._load_model()
            return self.model is not None
        except Exception as e:
            logger.error(f"Failed to reload model: {e}")
            return False 