import { useEffect, useState } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

export default function RegisterDog() {
  const [localities, setLocalities] = useState([])
  const [form, setForm] = useState({
    locality_id:'', sex:'unknown', color:'', vaccinated:false,
    vax_date:'', vax_expiry:'', sterilized:false, notes:''
  })
  const [photo, setPhoto]     = useState(null)
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

  useEffect(() => {
    axios.get(`${API}/localities/`).then(r => setLocalities(r.data))
  }, [])

  function handleChange(e) {
    const { name, value, type, checked } = e.target
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }))
  }

  async function handleSubmit() {
    if (!form.locality_id) { setError('Please select a locality.'); return }
    setLoading(true); setError(''); setResult(null)
    try {
      const data = new FormData()
      Object.entries(form).forEach(([k, v]) => data.append(k, v))
      if (photo) data.append('photo', photo)
      const res = await axios.post(`${API}/dogs/`, data)
      setResult(res.data)
      setForm({ locality_id:'', sex:'unknown', color:'', vaccinated:false, vax_date:'', vax_expiry:'', sterilized:false, notes:'' })
      setPhoto(null)
    } catch(e) {
      setError(e.response?.data?.detail || 'Something went wrong.')
    } finally { setLoading(false) }
  }

  return (
    <div className="page" style={{maxWidth:560}}>
      <div className="page-title">Register a dog</div>
      <div className="card">
        <div className="form-group">
          <label>Locality *</label>
          <select name="locality_id" value={form.locality_id} onChange={handleChange}>
            <option value="">Select locality</option>
            {localities.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
          </select>
        </div>
        <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12}}>
          <div className="form-group">
            <label>Sex</label>
            <select name="sex" value={form.sex} onChange={handleChange}>
              <option value="unknown">Unknown</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>
          <div className="form-group">
            <label>Coat color</label>
            <input name="color" value={form.color} onChange={handleChange} placeholder="e.g. brown, black and white" />
          </div>
        </div>
        <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12}}>
          <div className="form-group">
            <label>Vaccination date</label>
            <input type="date" name="vax_date" value={form.vax_date} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Vaccination expiry</label>
            <input type="date" name="vax_expiry" value={form.vax_expiry} onChange={handleChange} />
          </div>
        </div>
        <div style={{display:'flex', gap:24, marginBottom:14}}>
          <label style={{display:'flex', alignItems:'center', gap:8, cursor:'pointer', marginBottom:0}}>
            <input type="checkbox" name="vaccinated" checked={form.vaccinated} onChange={handleChange} style={{width:'auto'}}/>
            <span style={{fontSize:13, color:'#e8eaf0'}}>Vaccinated</span>
          </label>
          <label style={{display:'flex', alignItems:'center', gap:8, cursor:'pointer', marginBottom:0}}>
            <input type="checkbox" name="sterilized" checked={form.sterilized} onChange={handleChange} style={{width:'auto'}}/>
            <span style={{fontSize:13, color:'#e8eaf0'}}>Sterilized (ABC)</span>
          </label>
        </div>
        <div className="form-group">
          <label>Notes</label>
          <textarea name="notes" value={form.notes} onChange={handleChange} rows={2} placeholder="Any observations, markings, behaviour..." />
        </div>
        <div className="form-group">
          <label>Photo (optional)</label>
          <input type="file" accept="image/*" style={{padding:'7px 12px'}} onChange={e => setPhoto(e.target.files[0])} />
          {photo && <div style={{fontSize:12, color:'#34c98a', marginTop:4}}>📷 {photo.name}</div>}
        </div>
        {error && <div style={{color:'#ef4444', fontSize:13, marginBottom:12}}>{error}</div>}
        {result && (
          <div style={{background:'#0d3320', border:'1px solid #34c98a', borderRadius:8, padding:12, marginBottom:12, fontSize:13}}>
            ✓ Registered as <strong>{result.dog_code}</strong>
          </div>
        )}
        <button className="btn btn-primary" onClick={handleSubmit} disabled={loading} style={{width:'100%', justifyContent:'center'}}>
          {loading ? 'Registering...' : 'Register dog'}
        </button>
      </div>
    </div>
  )
}
