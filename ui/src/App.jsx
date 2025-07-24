// File: src/App.jsx

import React, { useEffect, useState, useRef, useCallback } from 'react';
import { Capacitor } from '@capacitor/core';
import { StatusBar, Style } from '@capacitor/status-bar';

const WS_URL = 'ws://127.0.0.1:8000/ws/audio';

const statusColors = {
  connected: 'bg-green-500',
  disconnected: 'bg-red-500',
  connecting: 'bg-yellow-400',
};

function arrayBufferToBase64(buffer) {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}

function base64ToWavBlob(base64, sampleRate) {
  const binaryString = atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  
  // Create WAV header
  const wavHeader = new ArrayBuffer(44);
  const view = new DataView(wavHeader);
  
  // RIFF header
  view.setUint32(0, 0x52494646, false); // "RIFF"
  view.setUint32(4, 36 + bytes.length, true); // File size
  view.setUint32(8, 0x57415645, false); // "WAVE"
  
  // fmt chunk
  view.setUint32(12, 0x666D7420, false); // "fmt "
  view.setUint32(16, 16, true); // fmt chunk size
  view.setUint16(20, 1, true); // Audio format (PCM)
  view.setUint16(22, 1, true); // Channels
  view.setUint32(24, sampleRate, true); // Sample rate
  view.setUint32(28, sampleRate * 2, true); // Byte rate
  view.setUint16(32, 2, true); // Block align
  view.setUint16(34, 16, true); // Bits per sample
  
  // data chunk
  view.setUint32(36, 0x64617461, false); // "data"
  view.setUint32(40, bytes.length, true); // Data size
  
  const wavBlob = new Blob([wavHeader, bytes], { type: 'audio/wav' });
  return wavBlob;
}

// Function to merge overlapping transcripts intelligently
function mergeOverlappingTranscripts(transcripts) {
  if (transcripts.length === 0) return '';
  if (transcripts.length === 1) return transcripts[0];
  
  let merged = transcripts[0];
  
  for (let i = 1; i < transcripts.length; i++) {
    const current = transcripts[i].trim();
    if (!current) continue;
    
    // Find the best overlap point
    const overlapPoint = findBestOverlap(merged, current);
    
    if (overlapPoint > 0) {
      // Remove the overlapping part from the current transcript
      const nonOverlapping = current.substring(overlapPoint);
      merged += ' ' + nonOverlapping;
    } else {
      // No significant overlap, just append
      merged += ' ' + current;
    }
  }
  
  return merged.trim();
}

// Helper function to find the best overlap between two transcript segments
function findBestOverlap(prev, current) {
  const words1 = prev.split(/\s+/).filter(w => w.length > 0);
  const words2 = current.split(/\s+/).filter(w => w.length > 0);
  
  // Look for overlap of at least 2 words (reduced from 3 for better performance)
  for (let overlap = Math.min(words1.length, words2.length, 3); overlap >= 2; overlap--) {
    const end1 = words1.slice(-overlap).join(' ').toLowerCase();
    const start2 = words2.slice(0, overlap).join(' ').toLowerCase();
    
    if (end1 === start2) {
      return current.toLowerCase().indexOf(start2) + start2.length;
    }
  }
  
  return 0; // No significant overlap found
}

const App = () => {
  const [wsStatus, setWsStatus] = useState('disconnected');
  const [transcript, setTranscript] = useState('');
  const [logs, setLogs] = useState('');
  const [audioUrl, setAudioUrl] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [chunkTable, setChunkTable] = useState([]); // [{idx, created, sent, received, transcript, audioB64, sampleRate}]
  const CHUNK_SEC = 5; // Increased from 3s to 5s for better performance
  const OVERLAP_SEC = 0.5; // Reduced overlap from 1s to 0.5s
  const STEP_SEC = CHUNK_SEC - OVERLAP_SEC; // 4.5 second step size
  const BATCH_MODE = true; // Enable batch processing for better performance
  const audioPlayerRef = useRef(null);
  const wsRef = useRef(null);
  const chunkIdxRef = useRef(0);
  const mergeTimeoutRef = useRef(null);
  const pendingTranscriptsRef = useRef([]);

  // Debounced transcript merging
  const debouncedMergeTranscripts = useCallback(() => {
    if (mergeTimeoutRef.current) {
      clearTimeout(mergeTimeoutRef.current);
    }
    
    mergeTimeoutRef.current = setTimeout(() => {
      if (pendingTranscriptsRef.current.length > 0) {
        const mergedTranscript = mergeOverlappingTranscripts(pendingTranscriptsRef.current);
        setTranscript(mergedTranscript);
        pendingTranscriptsRef.current = [];
      }
    }, 100); // 100ms debounce
  }, []);

  useEffect(() => {
    if (Capacitor.isNativePlatform()) {
      StatusBar.setOverlaysWebView({ overlay: true });
      StatusBar.setStyle({ style: Style.Light });
    }
    wsRef.current = new window.WebSocket(WS_URL);
    wsRef.current.onopen = () => {
      setLogs((prev) => prev + '[WS] Connected\n');
      setWsStatus('connected');
    };
    wsRef.current.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      setLogs((prev) => prev + `[WS] Received transcript for chunk ${msg.chunk_idx + 1}\n`);
      
      // Update chunk table with received transcript
      setChunkTable((prev) => {
        const updated = prev.map(row =>
          row.idx === msg.chunk_idx ? { ...row, received: true, transcript: msg.transcript } : row
        );
        
        // Add to pending transcripts for debounced merging
        const receivedTranscripts = updated
          .filter(row => row.received && row.transcript)
          .sort((a, b) => a.idx - b.idx) // Sort by chunk index
          .map(row => row.transcript);
        
        pendingTranscriptsRef.current = receivedTranscripts;
        debouncedMergeTranscripts();
        
        return updated;
      });
    };
    wsRef.current.onclose = () => {
      setLogs((prev) => prev + '[WS] Disconnected\n');
      setWsStatus('disconnected');
    };
    wsRef.current.onerror = (err) => {
      setLogs((prev) => prev + '[WS] Error: ' + err.message + '\n');
      setWsStatus('disconnected');
    };
    return () => {
      wsRef.current && wsRef.current.close();
      if (mergeTimeoutRef.current) {
        clearTimeout(mergeTimeoutRef.current);
      }
    };
  }, []);

  const sendChunkToWS = (audioBuffer, sampleRate, chunkIdx, isFile = false) => {
    if (!wsRef.current || wsRef.current.readyState !== 1) {
      setLogs((prev) => prev + '[WS] Not connected, cannot send chunk.\n');
      return;
    }
    let float32Buffer;
    if (audioBuffer instanceof ArrayBuffer) {
      float32Buffer = new Float32Array(audioBuffer);
    } else if (audioBuffer instanceof Blob) {
      const reader = new FileReader();
      reader.onload = () => {
        const arr = new Float32Array(reader.result);
        const audioB64 = arrayBufferToBase64(reader.result);
        const msg = {
          chunk_idx: chunkIdx,
          sample_rate: sampleRate,
          audio: audioB64
        };
        wsRef.current.send(JSON.stringify(msg));
        setLogs((prev) => prev + `[WS] Sent chunk ${msg.chunk_idx + 1}\n`);
        setChunkTable((prev) => prev.map(row =>
          row.idx === chunkIdx ? { ...row, sent: true, audioB64, sampleRate } : row
        ));
      };
      reader.readAsArrayBuffer(audioBuffer);
      return;
    } else {
      setLogs((prev) => prev + '[WS] Unknown audio buffer type.\n');
      return;
    }
    const audioB64 = arrayBufferToBase64(float32Buffer.buffer);
    const msg = {
      chunk_idx: chunkIdx,
      sample_rate: sampleRate,
      audio: audioB64
    };
    wsRef.current.send(JSON.stringify(msg));
    setLogs((prev) => prev + `[WS] Sent chunk ${msg.chunk_idx + 1}\n`);
    setChunkTable((prev) => prev.map(row =>
      row.idx === chunkIdx ? { ...row, sent: true, audioB64, sampleRate } : row
    ));
  };


  const handleUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAudioUrl(URL.createObjectURL(file));
      setTranscript('');
      setLogs((prev) => prev + `[UI] File uploaded: ${file.name}, type: ${file.type}, size: ${file.size} bytes\n`);
      chunkIdxRef.current = 0;
      setChunkTable([]);
      const reader = new FileReader();
      reader.onload = async () => {
        try {
          setLogs((prev) => prev + '[UI] FileReader loaded. Checking type...\n');
          if (!(reader.result instanceof ArrayBuffer)) {
            setLogs((prev) => prev + '[UI] FileReader did not return ArrayBuffer.\n');
            return;
          }
          if (file.size > 10 * 1024 * 1024) {
            setLogs((prev) => prev + '[UI] File too large for browser decoding.\n');
            return;
          }
          setLogs((prev) => prev + '[UI] Decoding audio data...\n');
          const audioContext = new (window.AudioContext || window.webkitAudioContext)();
          const audioBuffer = await audioContext.decodeAudioData(reader.result);
          setLogs((prev) => prev + '[UI] Audio decoded. Chunking...\n');
          const sampleRate = audioBuffer.sampleRate;
          const channelData = audioBuffer.getChannelData(0);
          const chunkSamples = sampleRate * CHUNK_SEC; // 3s chunks
          const stepSamples = sampleRate * STEP_SEC; // 2s step size
          let chunkRows = [];
          for (let i = 0; i < channelData.length; i += stepSamples) {
            const chunk = channelData.slice(i, i + chunkSamples);
            // Skip chunks that are too short (less than 1 second)
            if (chunk.length < sampleRate) continue;
            const chunkBuffer = new Float32Array(chunk);
            const audioB64 = arrayBufferToBase64(chunkBuffer.buffer);
            const idx = chunkIdxRef.current++;
            chunkRows.push({ idx, created: true, sent: false, received: false, transcript: '', audioB64, sampleRate });
          }
          setChunkTable(chunkRows);
        } catch (err) {
          setLogs((prev) => prev + '[UI] Error decoding audio file: ' + (err.stack || err.message) + '\n');
        }
      };
      reader.onerror = (err) => {
        setLogs((prev) => prev + '[UI] FileReader error: ' + err.message + '\n');
      };
      reader.readAsArrayBuffer(file);
    }
  };

  // Track which chunks have been sent
  const sentChunksRef = useRef(new Set());

  // Send chunk by index
  const sendChunkByIdx = (idx) => {
    setChunkTable(prev => prev.map(row =>
      row.idx === idx ? { ...row, sent: true } : row
    ));
    const row = chunkTable.find(row => row.idx === idx);
    if (row && !row.sent) {
      const msg = {
        chunk_idx: row.idx,
        sample_rate: row.sampleRate,
        audio: row.audioB64
      };
      wsRef.current.send(JSON.stringify(msg));
      setLogs((prev) => prev + `[WS] Sent file chunk ${row.idx + 1}\n`);
      sentChunksRef.current.add(idx);
    }
  };

  // Audio playback event handler
  useEffect(() => {
    if (!audioPlayerRef.current) return;
    const audio = audioPlayerRef.current;
    const onTimeUpdate = () => {
      const currentTime = audio.currentTime;
      // For each chunk, if playback has crossed its start and it hasn't been sent, send it
      chunkTable.forEach(row => {
        const chunkStart = row.idx * STEP_SEC; // Use STEP_SEC for overlapping chunks
        if (currentTime >= chunkStart && !row.sent && !sentChunksRef.current.has(row.idx)) {
          sendChunkByIdx(row.idx);
        }
      });
    };
    audio.addEventListener('timeupdate', onTimeUpdate);
    return () => {
      audio.removeEventListener('timeupdate', onTimeUpdate);
    };
  }, [audioUrl, chunkTable]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col items-stretch justify-stretch p-0">
      <div className="w-full h-full flex flex-col gap-6 p-8">
        <div className="flex items-center justify-between mb-2 w-full">
          <h1 className="text-3xl font-bold tracking-tight text-indigo-700">Tone AI</h1>
          <span className={`ml-4 px-3 py-1 rounded-full text-xs font-semibold text-white ${statusColors[wsStatus]}`}>{wsStatus.charAt(0).toUpperCase() + wsStatus.slice(1)}</span>
        </div>
        {/* Hide mic controls for now, only show file upload */}
        {/*
        <div className="flex flex-col md:flex-row gap-4 items-center justify-center w-full">
          <button
            className={`px-6 py-2 rounded-lg text-lg font-semibold shadow transition-all duration-150 ${isRecording ? 'bg-red-500 text-white' : 'bg-indigo-600 text-white hover:bg-indigo-700'}`}
            onClick={isRecording ? stopRecording : startRecording}
            title={isRecording ? 'Stop Recording' : 'Start Recording'}
          >
            {isRecording ? 'Stop Recording' : 'Record'}
          </button>
        </div>
        */}
        <div className="flex flex-col md:flex-row gap-4 items-center justify-center w-full">
          <label className="cursor-pointer px-6 py-2 rounded-lg bg-gray-200 text-gray-700 font-semibold shadow hover:bg-gray-300 transition-all duration-150" title="Upload an audio file">
            <input type="file" accept="audio/*" style={{ display: 'none' }} onChange={handleUpload} />
            Upload Audio
          </label>
        </div>
        {audioUrl && (
          <div className="w-full flex flex-col items-center gap-2">
            <audio ref={audioPlayerRef} controls src={audioUrl} className="w-full rounded" />
            <div className="w-full h-12 bg-gradient-to-r from-indigo-200 to-blue-100 rounded flex items-center justify-center text-indigo-400 text-sm font-mono">
              [Waveform visualization coming soon]
            </div>
          </div>
        )}
        <div className="w-full">
          <h2 className="text-lg font-semibold text-indigo-700 mb-1">Transcript</h2>
          <div className="bg-gray-50 border border-indigo-200 rounded-lg p-4 h-40 overflow-y-auto text-gray-800 font-mono whitespace-pre-wrap text-sm shadow-inner">
            {transcript || <span className="text-gray-400">[Speech-to-text output will appear here]</span>}
          </div>
        </div>
        {/* <div className="w-full">
          <h2 className="text-lg font-semibold text-indigo-700 mb-1">Logs</h2>
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 h-200 overflow-y-auto text-green-200 font-mono whitespace-pre-wrap text-xs shadow-inner">
            {logs || <span className="text-gray-500">[System logs will appear here]</span>}
          </div>
        </div> */}
        <div className="w-full mt-4 text-indigo-700">
          <h2 className="text-lg font-semibold text-indigo-700 mb-1">Chunks</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border border-indigo-200 rounded-lg text-xs shadow">
              <thead>
                <tr className="bg-indigo-100 text-indigo-700">
                  <th className="px-2 py-1">Chunk</th>
                  <th className="px-2 py-1">Created</th>
                  <th className="px-2 py-1">Sent</th>
                  <th className="px-2 py-1">Received</th>
                  <th className="px-2 py-1">Transcript</th>
                  <th className="px-2 py-1">Play</th>
                </tr>
              </thead>
              <tbody>
                {chunkTable.map((row) => (
                  <tr key={row.idx} className="border-t border-indigo-100">
                    <td className="px-2 py-1 text-center">{row.idx + 1}</td>
                    <td className="px-2 py-1 text-center">{row.created ? '✅' : ''}</td>
                    <td className="px-2 py-1 text-center">{row.sent ? '✅' : ''}</td>
                    <td className="px-2 py-1 text-center">{row.received ? '✅' : ''}</td>
                    <td className="px-2 py-1 font-mono whitespace-pre-wrap">{row.transcript}</td>
                    <td className="px-2 py-1 text-center">
                      {row.isMic && row.blob ? (
                        <button
                          className="px-2 py-1 bg-indigo-500 text-white rounded hover:bg-indigo-700 transition"
                          onClick={() => {
                            const url = URL.createObjectURL(row.blob);
                            const audio = new window.Audio(url);
                            audio.play();
                          }}
                          title="Play chunk"
                        >
                          ▶️
                        </button>
                      ) : row.audioB64 ? (
                        <button
                          className="px-2 py-1 bg-indigo-500 text-white rounded hover:bg-indigo-700 transition"
                          onClick={() => {
                            const blob = base64ToWavBlob(row.audioB64, row.sampleRate);
                            const url = URL.createObjectURL(blob);
                            const audio = new window.Audio(url);
                            audio.play();
                          }}
                          title="Play chunk"
                        >
                          ▶️
                        </button>
                      ) : (
                        <span className="text-gray-300">--</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="text-center text-xs text-gray-400 mt-2 w-full">&copy; {new Date().getFullYear()} Tone AI &mdash; Real-time Speech-to-Text Demo</div>
      </div>
    </div>
  );
};

export default App;