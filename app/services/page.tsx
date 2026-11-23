import Link from 'next/link'

export default function Services() {
  return (
    <section className="panel">
      <h1>What I Build</h1>
      <p>
        Landing pages, business websites, online stores and web apps. Pick one at the arcade in the{' '}
        <Link href="/lab" style={{ textDecoration: 'underline' }}>Lab</Link> to see what&apos;s included.
      </p>
    </section>
  )
}
