const STEPS = [
  {
    title: 'Snap your outfit',
    text: 'Upload a photo or use your camera. We spot each item of clothing.',
    accent: 'bg-moss',
  },
  {
    title: 'See its footprint',
    text: 'Every item gets a carbon estimate in kg of CO2, based on type, material and condition.',
    accent: 'bg-clay',
  },
  {
    title: 'Earn for greener choices',
    text: 'Second-hand and lower-impact materials save carbon. Savings become points for partner offers.',
    accent: 'bg-ochre',
  },
]

export function HowItWorks() {
  return (
    <section aria-labelledby="how-it-works">
      <h2 id="how-it-works" className="font-display text-2xl font-semibold">
        How it works
      </h2>
      <ol className="mt-4 space-y-3">
        {STEPS.map((step, index) => (
          <li key={step.title} className="flex gap-4 rounded-2xl border border-sand bg-white/60 p-4">
            <span
              className={`${step.accent} flex size-9 shrink-0 items-center justify-center rounded-full font-display font-semibold text-linen`}
            >
              {index + 1}
            </span>
            <div>
              <h3 className="font-semibold">{step.title}</h3>
              <p className="mt-1 text-stone">{step.text}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}
