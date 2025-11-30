import { useState, useEffect, useRef } from 'react'
import './App.css'
import { supabase } from './supabaseClient'

const API_URL = 'http://localhost:8000'

function App() {
  const [isRunning, setIsRunning] = useState(false)
  const [transcripts, setTranscripts] = useState([])
  const [processedCount, setProcessedCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [connectionStatus, setConnectionStatus] = useState('disconnected')
  const wsRef = useRef(null)

  // Fetch status on mount and every 5 seconds
  useEffect(() => {
    fetchStatus()
    loadAllTranscripts()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  // WebSocket connection
  useEffect(() => {
    if (isRunning) {
      connectWebSocket()
      const interval = setInterval(loadAllTranscripts, 30000) // Fallback polling
      return () => {
        clearInterval(interval)
        disconnectWebSocket()
      }
    } else {
      disconnectWebSocket()
    }
  }, [isRunning])

  const connectWebSocket = () => {
    try {
      wsRef.current = new WebSocket('ws://localhost:8000/ws')
      
      wsRef.current.onopen = () => {
        setConnectionStatus('connected')
        console.log('WebSocket connected')
      }
      
      wsRef.current.onmessage = (event) => {
        const message = JSON.parse(event.data)
        if (message.type === 'new_transcript') {
          setTranscripts(prev => [message.data, ...prev])
        }
      }
      
      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnectionStatus('error')
      }
      
      wsRef.current.onclose = () => {
        setConnectionStatus('disconnected')
        console.log('WebSocket disconnected')
      }
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
    }
  }

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }

  const loadAllTranscripts = async () => {
    if (supabase) {
      try {
        const { data, error } = await supabase
          .from('transcripts')
          .select('*')
          .order('timestamp', { ascending: false })
          .limit(50)
        
        if (error) throw error
        if (data) {
          setTranscripts(data)
        }
      } catch (err) {
        console.error('Failed to load from Supabase:', err)
        // Fallback to API
        await fetchTranscripts()
      }
    } else {
      // No Supabase, use API
      await fetchTranscripts()
    }
  }

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/status`)
      const data = await response.json()
      setIsRunning(data.is_running)
      setProcessedCount(data.processed_count)
    } catch (err) {
      console.error('Failed to fetch status:', err)
    }
  }

  const fetchTranscripts = async () => {
    try {
      const response = await fetch(`${API_URL}/api/transcripts?limit=50`)
      if (!response.ok) {
        console.error('Failed to fetch transcripts:', response.statusText)
        return
      }
      const data = await response.json()
      if (Array.isArray(data)) {
        setTranscripts(data)
      } else {
        console.error('Invalid transcripts format:', data)
      }
    } catch (err) {
      console.error('Failed to fetch transcripts:', err)
    }
  }

  const handleStart = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_URL}/api/start`, { method: 'POST' })
      const data = await response.json()
      if (response.ok) {
        setIsRunning(true)
        loadAllTranscripts()
      } else {
        setError(data.error || 'Failed to start monitoring')
      }
    } catch (err) {
      setError('Failed to connect to backend: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleStop = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_URL}/api/stop`, { method: 'POST' })
      const data = await response.json()
      if (response.ok) {
        setIsRunning(false)
      } else {
        setError(data.error || 'Failed to stop monitoring')
      }
    } catch (err) {
      setError('Failed to connect to backend: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const formatTimestamp = (isoString) => {
    const date = new Date(isoString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Monitor Agent</h1>
        <div className="header-info">
          <div className="status-badge">
            <span className={`status-dot ${isRunning ? 'active' : ''}`}></span>
            <span>{isRunning ? 'Active' : 'Stopped'}</span>
          </div>
          <div className="ws-badge">
            <span className={`ws-dot ${connectionStatus === 'connected' ? 'connected' : ''}`}></span>
            <span>{connectionStatus === 'connected' ? 'Live' : 'Offline'}</span>
          </div>
          <div className="count-badge">
            {processedCount} Transcripts
          </div>
        </div>
      </header>

      <div className="controls">
        {error && <div className="error-message">{error}</div>}
        
        <div className="button-group">
          <button
            onClick={handleStart}
            disabled={loading || isRunning}
            className="btn btn-start"
          >
            {loading ? 'Starting...' : 'Start Monitoring'}
          </button>
          <button
            onClick={handleStop}
            disabled={loading || !isRunning}
            className="btn btn-stop"
          >
            {loading ? 'Stopping...' : 'Stop Monitoring'}
          </button>
          <button
            onClick={loadAllTranscripts}
            className="btn btn-refresh"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="transcripts-container">
        {transcripts.length === 0 ? (
          <div className="empty-state">
            <p>No transcripts yet</p>
            <p className="empty-hint">Start monitoring to begin capturing transcripts</p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table className="transcripts-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Transcript</th>
                  <th>Summary</th>
                </tr>
              </thead>
              <tbody>
                {transcripts.map((transcript, index) => (
                  <tr key={transcript.id || index}>
                    <td className="timestamp-cell">
                      {formatTimestamp(transcript.timestamp)}
                    </td>
                    <td className="transcript-cell">
                      <div className="transcript-text">{transcript.transcript}</div>
                    </td>
                    <td className="summary-cell">
                      <div className="summary-text">{transcript.summary}</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
