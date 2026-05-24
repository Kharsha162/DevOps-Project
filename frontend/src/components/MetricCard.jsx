export default function MetricCard({ title, value, subtitle, color = 'text-brand-500' }) {
  return (
    <div className="card">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">{title}</p>
      <p className={`mt-2 text-3xl font-bold ${color}`}>{value}</p>
      {subtitle && <p className="mt-1 text-sm text-slate-400">{subtitle}</p>}
    </div>
  )
}
