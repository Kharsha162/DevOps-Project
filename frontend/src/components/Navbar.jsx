import { Link, NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth()

  const linkClass = ({ isActive }) =>
    `rounded-lg px-3 py-2 text-sm font-medium transition ${
      isActive ? 'bg-brand-600 text-white' : 'text-slate-300 hover:bg-slate-800'
    }`

  return (
    <nav className="border-b border-slate-800 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
        <Link to="/" className="text-lg font-bold text-white">
          CloudShop <span className="text-brand-500">DevOps</span>
        </Link>
        <div className="flex items-center gap-2">
          <NavLink to="/" className={linkClass} end>Dashboard</NavLink>
          <NavLink to="/products" className={linkClass}>Products</NavLink>
          {isAuthenticated && <NavLink to="/cart" className={linkClass}>Cart</NavLink>}
          {!isAuthenticated ? (
            <>
              <NavLink to="/login" className={linkClass}>Login</NavLink>
              <NavLink to="/signup" className="btn-primary text-sm">Sign Up</NavLink>
            </>
          ) : (
            <>
              <span className="hidden text-sm text-slate-400 sm:inline">{user?.username}</span>
              <button onClick={logout} className="btn-secondary text-sm">Logout</button>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
