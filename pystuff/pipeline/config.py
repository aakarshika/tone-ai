"""
Pipeline Configuration Module
Manages configuration settings for the audio processing pipeline.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import json
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class AudioConfig:
    """Audio processing configuration."""
    default_sample_rate: int = 16000
    chunk_duration: float = 5.0
    overlap_duration: float = 0.5
    min_chunk_duration: float = 0.5
    normalize_audio: bool = True


@dataclass
class TranscriptionConfig:
    """Transcription configuration."""
    model_size: str = "tiny"
    device: str = "cpu"
    compute_type: str = "int8"
    language: Optional[str] = None
    beam_size: int = 5
    best_of: int = 5


@dataclass
class PipelineConfig:
    """Main pipeline configuration."""
    audio: AudioConfig = field(default_factory=AudioConfig)
    transcription: TranscriptionConfig = field(default_factory=TranscriptionConfig)
    enable_speaker_diarization: bool = False
    enable_emotion_detection: bool = False
    enable_scene_classification: bool = False
    log_level: str = "INFO"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "audio": {
                "default_sample_rate": self.audio.default_sample_rate,
                "chunk_duration": self.audio.chunk_duration,
                "overlap_duration": self.audio.overlap_duration,
                "min_chunk_duration": self.audio.min_chunk_duration,
                "normalize_audio": self.audio.normalize_audio
            },
            "transcription": {
                "model_size": self.transcription.model_size,
                "device": self.transcription.device,
                "compute_type": self.transcription.compute_type,
                "language": self.transcription.language,
                "beam_size": self.transcription.beam_size,
                "best_of": self.transcription.best_of
            },
            "enable_speaker_diarization": self.enable_speaker_diarization,
            "enable_emotion_detection": self.enable_emotion_detection,
            "enable_scene_classification": self.enable_scene_classification,
            "log_level": self.log_level
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'PipelineConfig':
        """Create configuration from dictionary."""
        config = cls()
        
        if "audio" in config_dict:
            audio_config = config_dict["audio"]
            config.audio.default_sample_rate = audio_config.get("default_sample_rate", 16000)
            config.audio.chunk_duration = audio_config.get("chunk_duration", 5.0)
            config.audio.overlap_duration = audio_config.get("overlap_duration", 0.5)
            config.audio.min_chunk_duration = audio_config.get("min_chunk_duration", 0.5)
            config.audio.normalize_audio = audio_config.get("normalize_audio", True)
        
        if "transcription" in config_dict:
            trans_config = config_dict["transcription"]
            config.transcription.model_size = trans_config.get("model_size", "tiny")
            config.transcription.device = trans_config.get("device", "cpu")
            config.transcription.compute_type = trans_config.get("compute_type", "int8")
            config.transcription.language = trans_config.get("language")
            config.transcription.beam_size = trans_config.get("beam_size", 5)
            config.transcription.best_of = trans_config.get("best_of", 5)
        
        config.enable_speaker_diarization = config_dict.get("enable_speaker_diarization", False)
        config.enable_emotion_detection = config_dict.get("enable_emotion_detection", False)
        config.enable_scene_classification = config_dict.get("enable_scene_classification", False)
        config.log_level = config_dict.get("log_level", "INFO")
        
        return config
    
    def save_to_file(self, filepath: str) -> bool:
        """Save configuration to JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            logger.info(f"Configuration saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> Optional['PipelineConfig']:
        """Load configuration from JSON file."""
        try:
            if not os.path.exists(filepath):
                logger.warning(f"Configuration file not found: {filepath}")
                return None
            
            with open(filepath, 'r') as f:
                config_dict = json.load(f)
            
            config = cls.from_dict(config_dict)
            logger.info(f"Configuration loaded from {filepath}")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return None


def get_default_config() -> PipelineConfig:
    """Get default pipeline configuration."""
    return PipelineConfig()


def create_config_file(filepath: str = "pipeline_config.json") -> bool:
    """Create a default configuration file."""
    config = get_default_config()
    return config.save_to_file(filepath) 