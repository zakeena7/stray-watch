import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import axios from 'axios'
import 'leaflet/dist/leaflet.css'

const API = 'http://localhost:8000'

function riskColor(score) {
  if (score >= 70) return '#ef4444'
  if (score >= 40) return '#f59e0b'
  return '#34c98a'
}

export default function MapView() {
  const [localities, setLocalities] = useState([])

  useEffect(() => {
    axios.get(`${API}/localities/`).then(r => setLocalities(r.data))
  }, [])

  // Default center: Chennai
  const center = [13.0827, 80.2707]

  return (
    <div className="page">
      <div className="page-title">Locality risk map</div>
      <div style={{marginBottom:12, display:'flex', gap:16, fontSize:12, color:'#7a84a0'}}>
        <span><span style={{display:'inline-block',width:10,height:10,borderRadius:'50%',background:'#ef4444',marginRight:5}}/>High risk (score ≥ 70)</span>
        <span><span style={{display:'inline-block',width:10,height:10,borderRadius:'50%',background:'#f59e0b',marginRight:5}}/>Medium risk (40–69)</span>
        <span><span style={{display:'inline-block',width:10,height:10,borderRadius:'50%',background:'#34c98a',marginRight:5}}/>Low risk (below 40)</span>
      </div>
      <MapContainer center={center} zoom={12} style={{height:480, width:'100%', borderRadius:10}}>
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {localities.map(loc => (
          <CircleMarker
            key={loc.id}
            center={[loc.lat, loc.lng]}
            radius={16}
            pathOptions={{ color: riskColor(loc.risk_score), fillColor: riskColor(loc.risk_score), fillOpacity: 0.7 }}
          >
            <Popup>
              <strong>{loc.name}</strong><br/>
              Risk score: {loc.risk_score}<br/>
              Dogs: {loc.stats.total_dogs}<br/>
              Vaccinated: {loc.stats.vaccinated} ({loc.stats.coverage_percent}%)<br/>
              Unvaccinated: {loc.stats.unvaccinated}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  )
}
