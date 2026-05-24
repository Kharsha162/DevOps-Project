import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function ProductsPage() {
  const { isAuthenticated } = useAuth()
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')

  useEffect(() => {
    api.getProducts()
      .then((data) => setProducts(data.products || []))
      .catch(() => setProducts([
        { id: 'prod-1', name: 'Microservices Handbook', price: 49.99, stock: 12 },
        { id: 'prod-2', name: 'DevOps Mug', price: 19.99, stock: 85 },
        { id: 'prod-3', name: 'Kubernetes Jacket', price: 129.99, stock: 5 },
      ]))
      .finally(() => setLoading(false))
  }, [])

  const addToCart = async (prod) => {
    if (!isAuthenticated) {
      setMessage('Please login to add items to cart.')
      return
    }
    try {
      await api.addToCart({ product_id: prod.id, name: prod.name, price: prod.price, quantity: 1 })
      setMessage(`Added ${prod.name} to cart.`)
    } catch (err) {
      setMessage(err.message)
    }
  }

  if (loading) return <p className="text-slate-400">Loading products...</p>

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Product Catalog</h1>
        {isAuthenticated && <Link to="/cart" className="btn-secondary text-sm">View Cart</Link>}
      </div>
      {message && <p className="mb-4 text-sm text-brand-400">{message}</p>}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {products.map((prod) => (
          <div key={prod.id} className="card flex flex-col justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">{prod.name}</h3>
              <p className="mt-2 text-2xl font-bold text-brand-500">${prod.price}</p>
              <p className="mt-1 text-xs text-slate-400">Stock: {prod.stock ?? 'N/A'}</p>
            </div>
            <button className="btn-primary mt-4 w-full" onClick={() => addToCart(prod)}>Add to Cart</button>
          </div>
        ))}
      </div>
    </div>
  )
}
