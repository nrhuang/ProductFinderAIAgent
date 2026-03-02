import { useState } from "react";
import type { Product } from "../types";

interface ProductCardProps {
  product: Product;
}

function ImageFallback() {
  return (
    <div className="product-card__image product-card__image--fallback">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="48"
        height="48"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#9ca3af"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <polyline points="21 15 16 10 5 21" />
        <line x1="2" y1="2" x2="22" y2="22" />
      </svg>
      <span>Image not found</span>
    </div>
  );
}

export default function ProductCard({ product }: ProductCardProps) {
  const [imgError, setImgError] = useState(!product.image);

  return (
    <div className="product-card">
      {imgError ? (
        <ImageFallback />
      ) : (
        <img
          src={product.image}
          alt={product.name}
          className="product-card__image"
          onError={() => setImgError(true)}
        />
      )}
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
