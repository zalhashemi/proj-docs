import ProductCard from '../components/ProductCard'

const API = import.meta.env.VITE_API_URL

export default function Home() {
  return (
    <main className="mx-auto max-w-5xl p-6">
      <h1 className="font-display text-4xl text-brand-700">Fresh from the makers</h1>
      <ProductCard name="Ceramic mug" price={24} />
    </main>
  )
}
