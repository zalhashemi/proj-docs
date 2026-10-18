import { loadStripe } from '@stripe/stripe-js'

const stripe = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)

export default function Checkout() {
  return <button className="bg-brand text-white rounded px-4 py-2">Pay now</button>
}
