'use client'

// Contact form that "submits" to WhatsApp: it builds a tidy message from the fields and
// opens wa.me with it prefilled, so the visitor just taps Send in WhatsApp.
// (Sending silently without the visitor's WhatsApp would need the paid WhatsApp Business API.)

import { useState } from 'react'
import { site } from '@/content/site'
import WhatsAppIcon from './WhatsAppIcon'

export default function ContactForm() {
  const [service, setService] = useState<string | null>(null)
  const [sent, setSent] = useState(false)

  function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const f = new FormData(e.currentTarget)
    const val = (k: string) => String(f.get(k) ?? '').trim()
    const lines = [
      "Hi Philips, I'm interested in your services and would like to know more!",
      '',
      `*Name:* ${val('name')}`,
      val('company') ? `*Company:* ${val('company')}` : null,
      val('email') ? `*Email:* ${val('email')}` : null,
      service ? `*Looking for:* ${service}` : null,
      val('budget') ? `*Budget:* ${val('budget')}` : null,
      '',
      `*Message:*`,
      val('message'),
    ].filter((l): l is string => typeof l === 'string')
    const url = `https://wa.me/${site.whatsapp}?text=${encodeURIComponent(lines.join('\n'))}`
    const win = window.open(url, '_blank', 'noopener,noreferrer')
    if (!win) window.location.href = url // popup blocked: open in this tab instead
    setSent(true)
  }

  return (
    <form className="contact-form" onSubmit={onSubmit}>
      <div className="field-row">
        <label className="field">
          <span className="field-label">Name <b>*</b></span>
          <input name="name" required autoComplete="name" placeholder="Your name" />
        </label>
        <label className="field">
          <span className="field-label">Company</span>
          <input name="company" autoComplete="organization" placeholder="Optional" />
        </label>
      </div>
      <label className="field">
        <span className="field-label">Email</span>
        <input name="email" type="email" autoComplete="email" placeholder="So I can send you a proposal (optional)" />
      </label>
      <div className="field">
        <span className="field-label" id="service-label">What do you need?</span>
        <div className="chips" role="group" aria-labelledby="service-label">
          {site.contact.services.map((s) => (
            <button
              key={s}
              type="button"
              className="chip"
              aria-pressed={service === s}
              onClick={() => setService(service === s ? null : s)}
            >
              {s}
            </button>
          ))}
        </div>
      </div>
      <label className="field">
        <span className="field-label">Budget</span>
        <select name="budget" defaultValue="">
          <option value="">Select a range (optional)</option>
          {site.contact.budgets.map((b) => (
            <option key={b} value={b}>{b}</option>
          ))}
        </select>
      </label>
      <label className="field">
        <span className="field-label">Message <b>*</b></span>
        <textarea name="message" required placeholder="Tell me about your project, goals and timeline" />
      </label>
      <button type="submit" className="send-btn">
        <WhatsAppIcon size={22} />
        Send via WhatsApp
      </button>
      <p className={sent ? 'form-hint ok' : 'form-hint'} role="status">
        {sent
          ? 'WhatsApp is opening with your message. Just tap Send there.'
          : 'Opens WhatsApp with your message filled in, ready to send.'}
      </p>
    </form>
  )
}
