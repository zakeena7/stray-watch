import { useEffect, useState } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

const icons = { high: '🔴', medium: '🟡', info: '🔵' }

export default function Alerts() {
  const [alerts, setAlerts]   = useState([])
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)

  function loadAlerts() {
    axios.get(`${API}/alerts/`).then(r => setAlerts(r.data)).finally(() => setLoading(false))
  }

  useEffect(() => { loadAlerts() }, [])

  async function generateAlerts() {
    setRunning(true)
    await axios.post(`${API}/alerts/generate`)
    await loadAlerts()
    setRunning(false)
  }

  return (
    <div className="page">
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:20}}>
        <div className="page-title" style={{marginBottom:0}}>Active alerts</div>
        <button className="btn btn-primary" onClick={generateAlerts} disabled={running}>
          {running ? 'Generating...' : '⚡ Run alert check'}
        </button>
      </div>

      {loading ? <p style={{color:'#7a84a0'}}>Loading...</p> : (
        <div style={{display:'flex', flexDirection:'column', gap:10}}>
          {alerts.length === 0 && (
            <div className="card" style={{color:'#7a84a0', textAlign:'center', padding:40}}>
              No active alerts. Click "Run alert check" to scan all localities.
            </div>
          )}
          {alerts.map(a => (
            <div key={a.id} className="card" style={{
              borderLeft: `3px solid ${a.severity === 'high' ? '#ef4444' : a.severity === 'medium' ? '#f59e0b' : '#4f8ef7'}`,
              display:'flex', gap:12
            }}>
              <span style={{fontSize:20}}>{icons[a.severity] || '⚪'}</span>
              <div>
                <div style={{fontWeight:500, marginBottom:3}}>
                  {a.locality && <span style={{color:'#7a84a0', marginRight:8}}>{a.locality}</span>}
                  <span className={`badge badge-${a.severity}`}>{a.severity}</span>
                </div>
                <div style={{fontSize:13, color:'#b0b8cc', lineHeight:1.6}}>{a.message}</div>
                <div style={{fontSize:11, color:'#7a84a0', marginTop:4}}>
                  {new Date(a.created_at).toLocaleString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
