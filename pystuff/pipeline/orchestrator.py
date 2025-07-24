"""
Pipeline Orchestrator
Main coordinator for the audio processing pipeline.
"""

import asyncio
from typing import Dict, Any, Optional, List
import logging
import time

from .audio_processor import AudioProcessor
from .transcription import TranscriptionProcessor
from .config import PipelineConfig

# Import dependencies for status checking
try:
    import soundfile as sf
except ImportError:
    sf = None

try:
    import ffmpeg
except ImportError:
    ffmpeg = None

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Main orchestrator for the audio processing pipeline."""
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize the pipeline orchestrator.
        
        Args:
            config: Pipeline configuration (uses default if None)
        """
        self.config = config or PipelineConfig()
        self.audio_processor = AudioProcessor(self.config.audio.default_sample_rate)
        self.transcription_processor = TranscriptionProcessor(
            model_size=self.config.transcription.model_size,
            device=self.config.transcription.device,
            compute_type=self.config.transcription.compute_type
        )
        
        # Set up logging
        logging.basicConfig(level=getattr(logging, self.config.log_level))
        
        logger.info("Pipeline orchestrator initialized")
    
    async def process_audio_chunk(self, audio_b64: str, chunk_idx: int, 
                                sample_rate: int) -> Dict[str, Any]:
        """
        Process a single audio chunk through the pipeline.
        
        Args:
            audio_b64: Base64 encoded audio data
            chunk_idx: Index of the chunk
            sample_rate: Sample rate of the audio
            
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        
        try:
            # Step 1: Audio Processing
            logger.info(f"Processing chunk {chunk_idx + 1}")
            
            # Decode base64 audio
            audio_np, _ = self.audio_processor.decode_base64_audio(audio_b64)
            
            # Normalize audio if enabled
            if self.config.audio.normalize_audio:
                audio_np = self.audio_processor.normalize_audio(audio_np)
            
            # Convert to WAV format
            wav_bytes = self.audio_processor.convert_to_wav(audio_np, sample_rate)
            
            # Step 2: Transcription
            transcription_result = self.transcription_processor.transcribe_chunk(
                wav_bytes, chunk_idx, self.config.transcription.language
            )
            
            # Step 3: Prepare final result
            processing_time = time.time() - start_time
            
            result = {
                "chunk_idx": chunk_idx,
                "transcript": transcription_result["text"],
                "segments": transcription_result["segments"],
                "language": transcription_result["language"],
                "processing_time": processing_time,
                "audio_duration": transcription_result["duration"],
                "status": "success"
            }
            
            logger.info(f"Chunk {chunk_idx + 1} processed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Failed to process chunk {chunk_idx + 1}: {e}")
            
            return {
                "chunk_idx": chunk_idx,
                "transcript": f"[ERROR] {str(e)}",
                "processing_time": processing_time,
                "status": "error",
                "error": str(e)
            }
    
    async def process_audio_file(self, audio_b64: str, sample_rate: int) -> List[Dict[str, Any]]:
        """
        Process a complete audio file by chunking and processing each chunk.
        
        Args:
            audio_b64: Base64 encoded audio data
            sample_rate: Sample rate of the audio
            
        Returns:
            List of processing results for each chunk
        """
        try:
            # Decode and chunk the audio
            audio_np, _ = self.audio_processor.decode_base64_audio(audio_b64)
            
            if self.config.audio.normalize_audio:
                audio_np = self.audio_processor.normalize_audio(audio_np)
            
            chunks = self.audio_processor.chunk_audio(
                audio_np, 
                sample_rate,
                self.config.audio.chunk_duration,
                self.config.audio.overlap_duration
            )
            
            logger.info(f"Processing {len(chunks)} chunks")
            
            # Process each chunk
            results = []
            for chunk_idx, (chunk_audio, start_time) in enumerate(chunks):
                # Convert chunk to WAV
                wav_bytes = self.audio_processor.convert_to_wav(chunk_audio, sample_rate)
                
                # Transcribe chunk
                transcription_result = self.transcription_processor.transcribe_chunk(
                    wav_bytes, chunk_idx, self.config.transcription.language
                )
                
                result = {
                    "chunk_idx": chunk_idx,
                    "transcript": transcription_result["text"],
                    "segments": transcription_result["segments"],
                    "start_time": start_time,
                    "duration": transcription_result["duration"],
                    "status": "success"
                }
                
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to process audio file: {e}")
            raise
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get the current status of all pipeline components."""
        return {
            "audio_processor": {
                "available": True,
                "dependencies": {
                    "soundfile": sf is not None,
                    "ffmpeg": ffmpeg is not None
                }
            },
            "transcription_processor": {
                "available": self.transcription_processor.is_model_loaded(),
                "model_size": self.transcription_processor.model_size,
                "device": self.transcription_processor.device,
                "compute_type": self.transcription_processor.compute_type
            },
            "configuration": {
                "chunk_duration": self.config.audio.chunk_duration,
                "overlap_duration": self.config.audio.overlap_duration,
                "enable_speaker_diarization": self.config.enable_speaker_diarization,
                "enable_emotion_detection": self.config.enable_emotion_detection,
                "enable_scene_classification": self.config.enable_scene_classification
            }
        }
    
    def update_config(self, new_config: PipelineConfig) -> bool:
        """
        Update pipeline configuration.
        
        Args:
            new_config: New configuration
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            self.config = new_config
            
            # Update audio processor
            self.audio_processor.default_sample_rate = new_config.audio.default_sample_rate
            
            # Update transcription processor if needed
            if (new_config.transcription.model_size != self.transcription_processor.model_size or
                new_config.transcription.device != self.transcription_processor.device or
                new_config.transcription.compute_type != self.transcription_processor.compute_type):
                
                self.transcription_processor.reload_model(
                    new_config.transcription.model_size,
                    new_config.transcription.device,
                    new_config.transcription.compute_type
                )
            
            logger.info("Pipeline configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False 