import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar      from './components/Navbar'
import Dashboard   from './pages/Dashboard'
import MapView     from './pages/MapView'
import DogRegistry from './pages/DogRegistry'
import RegisterDog from './pages/RegisterDog'
import AIIdentify  from './pages/AIIdentify'
import Alerts      from './pages/Alerts'

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/"         element={<Dashboard />} />
        <Route path="/map"      element={<MapView />} />
        <Route path="/dogs"     element={<DogRegistry />} />
        <Route path="/register" element={<RegisterDog />} />
        <Route path="/identify" element={<AIIdentify />} />
        <Route path="/alerts"   element={<Alerts />} />
      </Routes>
    </BrowserRouter>
  )
}
