export default function ProductCard({ name, price }: { name: string; price: number }) {
  return (
    <div className="rounded border border-slate-200 p-4">
      <h2>{name}</h2>
      <p>${price}</p>
    </div>
  )
}
