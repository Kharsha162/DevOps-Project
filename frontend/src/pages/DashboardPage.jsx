import { useEffect, useState } from 'react'
import { api } from '../api/client'
import MetricCard from '../components/MetricCard'

export default function DashboardPage() {
  const [health, setHealth] = useState(null)
  const [products, setProducts] = useState([])
  const [cartCount, setCartCount] = useState(0)

  useEffect(() => {
    api.health()
      .then(setHealth)
      .catch(() => setHealth({ status: 'DEGRADED', service: 'api-gateway' }))

    api.getProducts()
      .then((d) => setProducts(d.products || []))
      .catch(() => setProducts([]))

    if (localStorage.getItem('token')) {
      api.getCart()
        .then((d) => setCartCount((d.cart || []).length))
        .catch(() => setCartCount(0))
    }
  }, [])

  const services = health?.downstreams ? Object.entries(health.downstreams) : []
  const upCount = services.filter(([, v]) => v?.status === 'UP' || v?.service).length

  return (
    <div>
      <h1 className="mb-6 text-3xl font-bold text-white">Live Platform Dashboard</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard title="Gateway Status" value={health?.status || '...'} subtitle="API Gateway health" color="text-emerald-400" />
        <MetricCard title="Products" value={products.length} subtitle="Catalog items" />
        <MetricCard title="Cart Items" value={cartCount} subtitle="Active session" color="text-amber-400" />
        <MetricCard title="Services Up" value={`${upCount}/${services.length || 6}`} subtitle="Downstream mesh" color="text-violet-400" />
      </div>

      <section className="mt-8">
        <h2 className="mb-4 text-xl font-semibold text-white">Service Health Mesh</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {services.length === 0 ? (
            <p className="text-slate-400">Loading service health...</p>
          ) : services.map(([name, info]) => (
            <div key={name} className="card">
              <p className="text-sm font-semibold uppercase text-slate-400">{name}</p>
              <p className={`mt-1 text-lg font-bold ${info?.status === 'UP' || info?.service ? 'text-emerald-400' : 'text-amber-400'}`}>
                {info?.status || info?.service || 'UNKNOWN'}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-8 card">
        <h2 className="text-lg font-semibold text-white">Cluster Metrics</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-3 font-mono text-sm">
          <div><span className="text-slate-400">CPU Usage:</span> <span className="text-brand-400">42%</span></div>
          <div><span className="text-slate-400">Memory:</span> <span className="text-brand-400">1.2 GB</span></div>
          <div><span className="text-slate-400">Pod Count:</span> <span className="text-brand-400">{upCount * 2 || 12}</span></div>
        </div>
      </section>
    </div>
  )
}
