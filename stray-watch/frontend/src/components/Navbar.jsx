import { NavLink } from 'react-router-dom'

const links = [
  { to: '/',          label: 'Dashboard' },
  { to: '/map',       label: 'Map' },
  { to: '/dogs',      label: 'Registry' },
  { to: '/register',  label: 'Register Dog' },
  { to: '/identify',  label: 'AI Identify' },
  { to: '/alerts',    label: 'Alerts' },
]

export default function Navbar() {
  return (
    <nav style={{
      background: '#181c27', borderBottom: '1px solid #2a3047',
      padding: '0 24px', display: 'flex', alignItems: 'center', gap: '4px',
      position: 'sticky', top: 0, zIndex: 100,
    }}>
      <span style={{ fontWeight: 600, fontSize: 15, marginRight: 24, color: '#4f8ef7', padding: '14px 0' }}>
        🐾 Stray Watch
      </span>
      {links.map(l => (
        <NavLink key={l.to} to={l.to} end={l.to === '/'}
          style={({ isActive }) => ({
            padding: '14px 12px', fontSize: 13, color: isActive ? '#4f8ef7' : '#7a84a0',
            borderBottom: isActive ? '2px solid #4f8ef7' : '2px solid transparent',
            transition: 'color 0.15s',
          })}>
          {l.label}
        </NavLink>
      ))}
    </nav>
  )
}
