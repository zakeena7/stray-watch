import { useState } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

export default function AIIdentify() {
  const [photo, setPhoto]     = useState(null)
  const [preview, setPreview] = useState(null)
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

  function handlePhoto(e) {
    const file = e.target.files[0]
    if (!file) return
    setPhoto(file)
    setPreview(URL.createObjectURL(file))
    setResult(null)
  }

  async function handleIdentify() {
    if (!photo) { setError('Please upload a photo first.'); return }
    setLoading(true); setError(''); setResult(null)
    try {
      const data = new FormData()
      data.append('photo', photo)
      const res = await axios.post(`${API}/dogs/identify`, data)
      setResult(res.data)
    } catch(e) {
      setError(e.response?.data?.detail || 'Identification failed.')
    } finally { setLoading(false) }
  }

  const statusColors = { matched: '#34c98a', needs_review: '#f59e0b', no_match: '#ef4444' }
  const statusLabels = { matched: 'Match found', needs_review: 'Needs review', no_match: 'No match' }

  return (
    <div className="page" style={{maxWidth:520}}>
      <div className="page-title">AI dog identification</div>
      <div className="card" style={{marginBottom:12}}>
        <p style={{color:'#7a84a0', fontSize:13, lineHeight:1.6, marginBottom:16}}>
          Upload a photo of a stray dog. The AI extracts a visual fingerprint using MobileNetV2
          and compares it against all registered dogs using cosine similarity.
        </p>
        <div style={{
          border: '1.5px dashed #2a3047', borderRadius:10, padding:28,
          textAlign:'center', cursor:'pointer', marginBottom:12,
          background: preview ? 'transparent' : '#1f2535',
          position:'relative', overflow:'hidden'
        }} onClick={() => document.getElementById('ai-upload').click()}>
          {preview
            ? <img src={preview} alt="preview" style={{maxHeight:200, maxWidth:'100%', borderRadius:8}}/>
            : <><div style={{fontSize:32, marginBottom:8}}>📷</div>
               <div style={{color:'#7a84a0', fontSize:13}}>Click to upload a dog photo</div></>
          }
          <input id="ai-upload" type="file" accept="image/*" style={{display:'none'}} onChange={handlePhoto}/>
        </div>
        {error && <div style={{color:'#ef4444', fontSize:13, marginBottom:12}}>{error}</div>}
        <button className="btn btn-primary" onClick={handleIdentify} disabled={loading || !photo} style={{width:'100%', justifyContent:'center'}}>
          {loading ? 'Analysing photo...' : 'Identify dog'}
        </button>
      </div>

      {result && (
        <div className="card">
          <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:12}}>
            <span style={{fontWeight:500}}>Result</span>
            <span className="badge" style={{background: statusColors[result.status] + '22', color: statusColors[result.status]}}>
              {statusLabels[result.status]}
            </span>
          </div>
          <div style={{fontSize:28, fontWeight:600, color: statusColors[result.status], marginBottom:4}}>
            {result.confidence}% <span style={{fontSize:14, color:'#7a84a0', fontWeight:400}}>confidence</span>
          </div>
          <p style={{fontSize:13, color:'#7a84a0', marginBottom: result.match ? 12 : 0}}>{result.message}</p>
          {result.match && (
            <div style={{background:'#1f2535', borderRadius:8, padding:12, fontSize:13}}>
              <div style={{fontWeight:500, marginBottom:4}}>{result.match.dog_code}</div>
              <div style={{color:'#7a84a0'}}>{result.match.color} · {result.match.locality}</div>
              <div style={{marginTop:4}}>
                <span className={`badge ${result.match.vaccinated ? 'badge-low' : 'badge-high'}`}>
                  {result.match.vaccinated ? 'Vaccinated' : 'Not vaccinated'}
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
