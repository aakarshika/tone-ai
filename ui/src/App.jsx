// File: src/App.jsx

import React, { useEffect, useState, useRef } from 'react';
import { HashRouter } from 'react-router-dom';
import { Capacitor } from '@capacitor/core';
import { StatusBar, Style } from '@capacitor/status-bar';

/**
 * Main App component that wraps the application with necessary providers and routing
 */
const App = () => {
  const [audioUrl, setAudioUrl] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    // Handle status bar for mobile platforms
    if (Capacitor.isNativePlatform()) {
      StatusBar.setOverlaysWebView({ overlay: true });
      StatusBar.setStyle({ style: Style.Light });
    }
  }, []);

  // Audio recording logic (basic, browser only)
  const startRecording = async () => {
    setTranscript('');
    setIsRecording(true);
    audioChunksRef.current = [];
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorderRef.current = new window.MediaRecorder(stream);
    mediaRecorderRef.current.ondataavailable = (e) => {
      audioChunksRef.current.push(e.data);
    };
    mediaRecorderRef.current.onstop = () => {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);
      // TODO: Send audioBlob to backend for speech-to-text and tone analysis
    };
    mediaRecorderRef.current.start();
  };

  const stopRecording = () => {
    setIsRecording(false);
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
  };

  const handleUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAudioUrl(URL.createObjectURL(file));
      // TODO: Send file to backend for processing
    }
  };

  return (
    <HashRouter>
      <div style={{ maxWidth: 600, margin: '0 auto', padding: 24 }}>
        <h1 style={{ textAlign: 'center', marginBottom: 24 }}>Tone AI</h1>
        {/* Audio Controls */}
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginBottom: 16 }}>
          <button onClick={isRecording ? stopRecording : startRecording}>
            {isRecording ? 'Stop Recording' : 'Record'}
          </button>
          <label style={{ cursor: 'pointer' }}>
            <input type="file" accept="audio/*" style={{ display: 'none' }} onChange={handleUpload} />
            Upload Audio
          </label>
        </div>
        {/* Audio Playback */}
        {audioUrl && (
          <div style={{ marginBottom: 16, textAlign: 'center' }}>
            <audio controls src={audioUrl} style={{ width: '100%' }} />
          </div>
        )}
        {/* Waveform Placeholder */}
        {audioUrl && (
          <div style={{ height: 60, background: '#eee', borderRadius: 8, marginBottom: 16, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#888' }}>
            [Waveform visualization coming soon]
          </div>
        )}
        {/* Real-time Text Display */}
        <div style={{ minHeight: 48, background: '#fafafa', border: '1px solid #eee', borderRadius: 8, padding: 12, marginBottom: 16 }}>
          <strong>Transcript:</strong>
          <div style={{ marginTop: 8 }}>{transcript || <span style={{ color: '#bbb' }}>[Speech-to-text output will appear here]</span>}</div>
        </div>
        {/* TODO: Add tone/emotion analysis results UI here */}
      </div>
    </HashRouter>
  );
};

export default App;