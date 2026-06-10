import { useEffect, useState } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

export default function DogRegistry() {
  const [dogs, setDogs]             = useState([])
  const [localities, setLocalities] = useState([])
  const [filterLoc, setFilterLoc]   = useState('')
  const [loading, setLoading]       = useState(true)

  useEffect(() => {
    axios.get(`${API}/localities/`).then(r => setLocalities(r.data))
  }, [])

  useEffect(() => {
    const url = filterLoc ? `${API}/dogs/?locality_id=${filterLoc}` : `${API}/dogs/`
    axios.get(url).then(r => setDogs(r.data)).finally(() => setLoading(false))
  }, [filterLoc])

  return (
    <div className="page">
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:20}}>
        <div className="page-title" style={{marginBottom:0}}>Dog registry</div>
        <select style={{width:180}} value={filterLoc} onChange={e => setFilterLoc(e.target.value)}>
          <option value="">All localities</option>
          {localities.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
        </select>
      </div>

      <div className="card" style={{padding:0, overflow:'hidden'}}>
        {loading ? <p style={{padding:20, color:'#7a84a0'}}>Loading...</p> : (
          <table>
            <thead>
              <tr>
                <th>Dog code</th><th>Color / Sex</th><th>Locality</th>
                <th>Vaccinated</th><th>Vax expiry</th><th>Sterilized</th>
              </tr>
            </thead>
            <tbody>
              {dogs.length === 0 && (
                <tr><td colSpan={6} style={{textAlign:'center', color:'#7a84a0', padding:32}}>No dogs registered yet.</td></tr>
              )}
              {dogs.map(d => (
                <tr key={d.id}>
                  <td style={{fontWeight:500, color:'#4f8ef7'}}>{d.dog_code}</td>
                  <td>{d.color || '—'} / {d.sex || '—'}</td>
                  <td>{localities.find(l => l.id === d.locality_id)?.name || d.locality_id}</td>
                  <td>
                    <span className={`badge ${d.vaccinated ? 'badge-low' : 'badge-high'}`}>
                      {d.vaccinated ? 'Yes' : 'No'}
                    </span>
                  </td>
                  <td>{d.vax_expiry ? new Date(d.vax_expiry).toLocaleDateString() : '—'}</td>
                  <td>{d.sterilized ? '✓' : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
