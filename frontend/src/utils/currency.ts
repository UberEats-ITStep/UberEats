const priceFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
});

export const formatPrice = (price: string | number): string => {
  const numericPrice = typeof price === 'string' ? Number(price) : price;
  return Number.isFinite(numericPrice)
    ? priceFormatter.format(numericPrice)
    : String(price);
};
