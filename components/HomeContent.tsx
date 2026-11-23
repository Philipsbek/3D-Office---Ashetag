// Everything below the 3D hero on the homepage. Text comes from content/site.ts.

import Link from 'next/link'
import { site } from '@/content/site'
import ContactForm from '@/components/ContactForm'

export default function HomeContent() {
  return (
    <div className="home">
      {/* ---------- statement ---------- */}
      <section className="block statement" aria-labelledby="statement-title">
        <h1 id="statement-title" className="display-hero">{site.statement.headline}</h1>
        <p className="body intro">{site.statement.intro}</p>
      </section>

      {/* ---------- tools used: nonstop marquee ---------- */}
      <section className="block" aria-labelledby="tools-title">
        <h2 id="tools-title" className="eyebrow muted">Tools Used</h2>
        <div className="marquee">
          {/* two identical tracks so the loop is seamless; the copy is hidden from screen readers */}
          {[0, 1].map((copy) => (
            <ul key={copy} className="marquee-track" aria-hidden={copy === 1 ? true : undefined}>
              {site.tools.map((t) => (
                <li key={t.name} className="tool-cell">
                  <img src={t.logo} alt="" width={40} height={40} />
                  <span>{t.name}</span>
                </li>
              ))}
            </ul>
          ))}
        </div>
      </section>

      {/* ---------- what I build ---------- */}
      <section id="work" className="block" aria-labelledby="work-title">
        <h2 id="work-title" className="display-section rule-under">
          What I Build<sup className="counter">({site.work.length})</sup>
        </h2>
        <ol className="projects">
          {site.work.map((p) => (
            <li key={p.title} className="project">
              <div className="project-media">
                <img src={p.image} alt={p.title} width={1600} height={900} loading="lazy" />
              </div>
              <p className="body concrete project-desc">{p.description}</p>
              <h3 className="project-title">{p.title}</h3>
              <ul className="project-services body">
                {p.services.map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            </li>
          ))}
        </ol>
      </section>

      {/* ---------- capabilities ---------- */}
      <section id="services" className="block" aria-labelledby="services-title">
        <h2 id="services-title" className="eyebrow muted">
          Services<sup className="counter">({site.capabilities.columns.length})</sup>
        </h2>
        <p className="display-section concrete capabilities-statement">{site.capabilities.statement}</p>
        <div className="capabilities">
          {site.capabilities.columns.map((c) => (
            <div key={c.title} className="capability">
              <h3 className="body">{c.title}</h3>
              <p className="body concrete">{c.copy}</p>
              <ul className="tags">
                {c.tags.map((t) => (
                  <li key={t} className="tag">{t}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* ---------- contact ---------- */}
      <section id="contact" className="block contact" aria-labelledby="contact-title">
        <div className="contact-intro">
          <h2 id="contact-title" className="eyebrow muted">Contact</h2>
          <p className="display-section concrete">{site.contact.slogan}</p>
          <p className="body contact-note">{site.contact.note}</p>
          <a className="body contact-mail" href={`mailto:${site.email}`}>
            {site.email}
          </a>
        </div>
        <ContactForm />
      </section>

      {/* ---------- footer ---------- */}
      <footer className="footer">
        <svg className="wordmark" viewBox="0 0 1000 150" role="img" aria-label={site.name}>
          <text x="0" y="141" textLength="1000" lengthAdjust="spacingAndGlyphs">
            {site.name}
          </text>
        </svg>
        <div className="footer-row">
          <nav className="footer-nav" aria-label="Footer">
            <Link href="/">Home</Link>
            <Link href="/#work">Work<sup className="counter">({site.work.length})</sup></Link>
            <Link href="/#services">Services</Link>
            <Link href="/lab">Lab</Link>
            <Link href="/#contact">Contact</Link>
          </nav>
          <p className="footer-legal">© {site.year} {site.name}. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
