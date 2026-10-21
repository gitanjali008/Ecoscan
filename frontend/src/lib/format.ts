const kgFormat = new Intl.NumberFormat('en', { maximumFractionDigits: 1 })

/** 13.2 -> "13.2 kg", 2 -> "2 kg" */
export function formatKg(kg: number): string {
  return `${kgFormat.format(kg)} kg`
}

/** "t-shirt" -> "T-shirt" */
export function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1)
}
