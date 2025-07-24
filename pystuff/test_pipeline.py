"""
Test Script for Modular Pipeline
Validates the new pipeline architecture and components.
"""

import asyncio
import base64
import numpy as np
import logging
from pipeline import PipelineOrchestrator, PipelineConfig, AudioProcessor, TranscriptionProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_test_audio(duration_seconds: float = 3.0, sample_rate: int = 16000) -> bytes:
    """Create a simple test audio signal."""
    # Generate a simple sine wave
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds))
    audio = np.sin(2 * np.pi * 440 * t) * 0.1  # 440 Hz sine wave
    
    # Convert to WAV bytes
    import soundfile as sf
    import io
    
    with io.BytesIO() as wav_io:
        sf.write(wav_io, audio, sample_rate, format='WAV')
        wav_io.seek(0)
        return wav_io.read()


def test_audio_processor():
    """Test the audio processor module."""
    logger.info("Testing AudioProcessor...")
    
    processor = AudioProcessor()
    
    # Test audio creation
    test_audio = create_test_audio(3.0)
    
    # Test chunking
    audio_np = np.frombuffer(test_audio[44:], dtype=np.int16).astype(np.float32) / 32768.0
    chunks = processor.chunk_audio(audio_np, 16000, chunk_duration=1.0, overlap_duration=0.2)
    
    logger.info(f"Created {len(chunks)} chunks")
    
    # Test WAV conversion
    wav_bytes = processor.convert_to_wav(audio_np, 16000)
    logger.info(f"WAV conversion successful: {len(wav_bytes)} bytes")
    
    return True


def test_transcription_processor():
    """Test the transcription processor module."""
    logger.info("Testing TranscriptionProcessor...")
    
    processor = TranscriptionProcessor(model_size="tiny")
    
    if not processor.is_model_loaded():
        logger.warning("Whisper model not loaded - skipping transcription test")
        return False
    
    # Create test audio
    test_audio = create_test_audio(2.0)
    
    # Test transcription
    try:
        result = processor.transcribe_audio(test_audio)
        logger.info(f"Transcription successful: {result['text']}")
        return True
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return False


async def test_pipeline_orchestrator():
    """Test the pipeline orchestrator."""
    logger.info("Testing PipelineOrchestrator...")
    
    config = PipelineConfig()
    orchestrator = PipelineOrchestrator(config)
    
    # Test pipeline status
    status = orchestrator.get_pipeline_status()
    logger.info(f"Pipeline status: {status}")
    
    # Create test audio
    test_audio = create_test_audio(3.0)
    audio_b64 = base64.b64encode(test_audio).decode('utf-8')
    
    # Test chunk processing
    try:
        result = await orchestrator.process_audio_chunk(audio_b64, 0, 16000)
        logger.info(f"Pipeline processing successful: {result}")
        return True
    except Exception as e:
        logger.error(f"Pipeline processing failed: {e}")
        return False


async def main():
    """Run all tests."""
    logger.info("Starting pipeline tests...")
    
    # Test individual components
    audio_ok = test_audio_processor()
    transcription_ok = test_transcription_processor()
    pipeline_ok = await test_pipeline_orchestrator()
    
    # Summary
    logger.info("Test Results:")
    logger.info(f"  AudioProcessor: {'✅ PASS' if audio_ok else '❌ FAIL'}")
    logger.info(f"  TranscriptionProcessor: {'✅ PASS' if transcription_ok else '❌ FAIL'}")
    logger.info(f"  PipelineOrchestrator: {'✅ PASS' if pipeline_ok else '❌ FAIL'}")
    
    if all([audio_ok, transcription_ok, pipeline_ok]):
        logger.info("🎉 All tests passed!")
    else:
        logger.warning("⚠️  Some tests failed")


if __name__ == "__main__":
    asyncio.run(main()) 