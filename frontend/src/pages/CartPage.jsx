import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function CartPage() {
  const [cart, setCart] = useState([])
  const [total, setTotal] = useState(0)
  const [log, setLog] = useState([])
  const [loading, setLoading] = useState(true)

  const addLog = (msg) => setLog((prev) => [{ id: Date.now(), msg }, ...prev])

  const loadCart = () => {
    setLoading(true)
    api.getCart()
      .then((data) => {
        setCart(data.cart || [])
        setTotal(data.total || 0)
      })
      .catch((err) => addLog(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadCart() }, [])

  const removeItem = async (productId) => {
    try {
      const data = await api.removeFromCart(productId)
      setCart(data.cart || [])
      setTotal(data.total || 0)
      addLog(`Removed ${productId}`)
    } catch (err) {
      addLog(err.message)
    }
  }

  const checkout = async () => {
    if (cart.length === 0) return addLog('Cart is empty')
    try {
      addLog('Creating order...')
      const order = await api.createOrder({ items: cart, total })
      addLog(`Order ${order.order_id || 'created'}`)
      const payment = await api.processPayment({ order_id: order.order_id, amount: total })
      addLog(`Payment ${payment.transaction_id || 'approved'}`)
      await api.sendNotification({ recipient: 'buyer@shop.com', body: `Order total $${total}` })
      addLog('Checkout complete!')
      loadCart()
    } catch (err) {
      addLog(`Checkout: ${err.message}`)
    }
  }

  if (loading) return <p className="text-slate-400">Loading cart...</p>

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="card">
        <h1 className="text-2xl font-bold text-white">Your Cart</h1>
        {cart.length === 0 ? (
          <p className="mt-4 text-slate-400">Cart is empty.</p>
        ) : (
          <ul className="mt-4 space-y-3">
            {cart.map((item) => (
              <li key={item.product_id} className="flex items-center justify-between border-b border-slate-800 pb-2">
                <div>
                  <p className="font-medium">{item.name}</p>
                  <p className="text-xs text-slate-400">Qty {item.quantity} x ${item.price}</p>
                </div>
                <button className="text-sm text-red-400 hover:underline" onClick={() => removeItem(item.product_id)}>Remove</button>
              </li>
            ))}
          </ul>
        )}
        <p className="mt-4 text-xl font-bold text-emerald-400">Total: ${total.toFixed(2)}</p>
        <button className="btn-primary mt-4 w-full" onClick={checkout} disabled={cart.length === 0}>Checkout</button>
      </div>
      <div className="card">
        <h2 className="text-lg font-semibold">Event Log</h2>
        <ul className="mt-3 max-h-64 space-y-2 overflow-y-auto font-mono text-xs text-slate-300">
          {log.map((e) => <li key={e.id}>{e.msg}</li>)}
        </ul>
      </div>
    </div>
  )
}
