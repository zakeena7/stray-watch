import { useEffect, useState } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

function riskColor(score) {
  if (score >= 70) return '#ef4444'
  if (score >= 40) return '#f59e0b'
  return '#34c98a'
}

export default function Dashboard() {
  const [localities, setLocalities] = useState([])
  const [loading, setLoading]       = useState(true)

  useEffect(() => {
    axios.get(`${API}/localities/`)
      .then(r => setLocalities(r.data))
      .finally(() => setLoading(false))
  }, [])

  const totalDogs     = localities.reduce((s, l) => s + l.stats.total_dogs, 0)
  const totalVax      = localities.reduce((s, l) => s + l.stats.vaccinated, 0)
  const totalUnvax    = localities.reduce((s, l) => s + l.stats.unvaccinated, 0)
  const highRisk      = localities.filter(l => l.risk_score >= 70).length

  return (
    <div className="page">
      <div className="page-title">Dashboard</div>

      <div className="stat-cards">
        <div className="stat-card"><div className="stat-label">Total dogs</div><div className="stat-value">{totalDogs}</div></div>
        <div className="stat-card"><div className="stat-label">Vaccinated</div><div className="stat-value" style={{color:'#34c98a'}}>{totalVax}</div></div>
        <div className="stat-card"><div className="stat-label">Unvaccinated</div><div className="stat-value" style={{color:'#ef4444'}}>{totalUnvax}</div></div>
        <div className="stat-card"><div className="stat-label">High risk zones</div><div className="stat-value" style={{color:'#ef4444'}}>{highRisk}</div></div>
      </div>

      {loading ? <p style={{color:'#7a84a0'}}>Loading localities...</p> : (
        <div style={{display:'flex', flexDirection:'column', gap:10}}>
          {localities.length === 0 && (
            <div className="card" style={{color:'#7a84a0', textAlign:'center', padding:40}}>
              No localities yet. Add one via the API or Thunder Client.
            </div>
          )}
          {localities.map(loc => (
            <div key={loc.id} className="card">
              <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:10}}>
                <span style={{fontWeight:500, fontSize:15}}>{loc.name}</span>
                <span className={`badge badge-${loc.risk_score >= 70 ? 'high' : loc.risk_score >= 40 ? 'medium' : 'low'}`}>
                  {loc.risk_score >= 70 ? 'High risk' : loc.risk_score >= 40 ? 'Medium risk' : 'Low risk'} · {loc.risk_score}
                </span>
              </div>
              <div className="progress-bg">
                <div className="progress-fill" style={{
                  width: `${loc.stats.coverage_percent}%`,
                  background: riskColor(loc.risk_score)
                }}/>
              </div>
              <div style={{display:'flex', gap:20, fontSize:12, color:'#7a84a0', marginTop:6}}>
                <span>{loc.stats.total_dogs} dogs total</span>
                <span>{loc.stats.vaccinated} vaccinated ({loc.stats.coverage_percent}%)</span>
                <span>{loc.stats.unvaccinated} unvaccinated</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
