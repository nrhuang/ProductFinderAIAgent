import type { Product } from "../types";

const FALLBACK_IMAGE =
  "https://via.placeholder.com/300x200?text=No+Image";

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
  return (
    <div className="product-card">
      <img
        src={product.image}
        alt={product.name}
        className="product-card__image"
        onError={(e) => {
          (e.currentTarget as HTMLImageElement).src = FALLBACK_IMAGE;
        }}
      />
      <div className="product-card__body">
        <span className="product-card__category">{product.category}</span>
        <h3 className="product-card__name">{product.name}</h3>
        <p className="product-card__description">{product.description}</p>
        <p className="product-card__price">
          ${product.price.toFixed(2)}
        </p>
      </div>
    </div>
  );
}
