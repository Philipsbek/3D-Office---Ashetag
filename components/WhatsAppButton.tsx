// Floating WhatsApp chat button (bottom right, every page). Official WhatsApp glyph (white),
// on a plain black button. Opens a chat with a prefilled message.

import { site } from '@/content/site'
import WhatsAppIcon from './WhatsAppIcon'

const PHONE = site.whatsapp
const MESSAGE = "Hi Philips, I'm interested in your services and would like to know more!"
const HREF = `https://wa.me/${PHONE}?text=${encodeURIComponent(MESSAGE)}`

export default function WhatsAppButton() {
  return (
    <a className="wa-float" href={HREF} target="_blank" rel="noopener noreferrer" aria-label="Chat with me on WhatsApp">
      <WhatsAppIcon size={30} fill="#ffffff" />
    </a>
  )
}
