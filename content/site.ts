// All the words on the site live here, so you can edit them without touching any layout code.
// This is Philips Bek's personal portfolio: everything is written in the first person ("I").

export const site = {
  name: 'PHILIPS BEK',
  year: new Date().getFullYear(),
  email: 'philipsbekwork@gmail.com',
  whatsapp: '60179812010', // country code + number, no + or spaces (floating button + contact form)

  statement: {
    headline: 'I build interactive modern websites.',
    intro:
      "I'm Philips Bek, a developer who designs and builds fast, modern websites — from landing pages and portfolios to full web apps that look sharp and feel great to use.",
  },

  // Tools Used marquee. Logos live in public/logos/ (official brand marks).
  tools: [
    { name: 'Codex', logo: '/logos/codex.svg' },
    { name: 'Claude', logo: '/logos/claude.svg' },
    { name: 'Blender', logo: '/logos/blender.svg' },
    { name: 'Grok', logo: '/logos/grok.svg' },
    { name: 'Gemini', logo: '/logos/gemini.svg' },
    { name: 'Kling', logo: '/logos/kling.svg' },
  ],

  // What I Build: the kinds of websites I offer. Images live in public/work/ (mock-ups
  // built from my own 3D models; sources in blender/mockups/).
  work: [
    {
      title: 'Landing Pages',
      image: '/work/build-landing.jpg',
      description:
        'I can build one focused page to launch your product and turn visitors into customers, live within a week.',
      services: ['Design', 'Copywriting', 'Analytics'],
      // Lab arcade: tile colour + icon, and the info panel's extra detail
      arcade: { color: '#22e4ff', icon: 'landing' },
      details:
        'Perfect for a product launch, an event, a campaign or a new business that needs to look credible fast. I write and design every section to move visitors towards one clear action.',
      includes: ['Custom design for desktop and mobile', 'Persuasive copy and clear calls to action', 'Contact, sign-up or pre-order form', 'Speed, SEO basics and analytics set up'],
      timeline: '1 – 2 weeks',
    },
    {
      title: 'Business Websites',
      image: '/work/build-business.jpg',
      description:
        'I can build a multi-page site for your business, with online booking and content your team can edit without calling me.',
      services: ['CMS', 'SEO', 'Responsive'],
      arcade: { color: '#ff4fd8', icon: 'business' },
      details:
        'A complete home for your business online: who you are, what you offer and how to reach you, with pages you can update yourself whenever things change.',
      includes: ['Home, About, Services and Contact pages', 'Easy editing for your own team (CMS)', 'Online booking, enquiry or quote forms', 'Google-ready SEO and business listing setup'],
      timeline: '2 – 4 weeks',
    },
    {
      title: 'Online Stores',
      image: '/work/build-store.jpg',
      description: 'I can build shops that load fast, show your products beautifully and check out smoothly on any device.',
      services: ['E-commerce', 'Payments', 'Inventory'],
      arcade: { color: '#b6ff3b', icon: 'store' },
      details:
        'Sell online with a store that is fast, easy to browse and simple to manage, from a handful of products to a full catalogue.',
      includes: ['Product pages, categories and search', 'Cart and checkout with local payment options', 'Stock, orders and shipping management', 'Promo codes, email receipts and sales reports'],
      timeline: '3 – 6 weeks',
    },
    {
      title: 'Web Apps',
      image: '/work/build-app.jpg',
      description: 'I can build dashboards, booking systems and portals with accounts, live data and real-time views.',
      services: ['Accounts', 'Databases', 'APIs'],
      arcade: { color: '#ffb020', icon: 'app' },
      details:
        'Custom tools for the way your business works: booking systems, customer portals, internal dashboards and more, built to save your team time.',
      includes: ['User accounts, roles and secure login', 'Dashboards with live data and reports', 'Bookings, payments or approvals workflows', 'Integrations with the tools you already use'],
      timeline: '4 – 10 weeks',
    },
  ],

  capabilities: {
    statement:
      'I handle design, development and launch myself — so your website looks right, works fast and actually brings in customers.',
    columns: [
      {
        title: 'Design',
        copy: 'I design clean, modern layouts around your brand and what your visitors need to do.',
        tags: ['UI/UX', 'Wireframes', 'Branding', 'Prototypes'],
      },
      {
        title: 'Development',
        copy: 'I build fast, responsive sites with modern, AI-assisted tools, so they launch sooner and work on every screen.',
        tags: ['Next.js', 'React', 'Responsive', 'CMS'],
      },
      {
        title: 'Growth',
        copy: 'I build sites to be found and to convert: search-ready, quick to load and easy to track.',
        tags: ['SEO', 'Speed', 'Analytics', 'Copywriting'],
      },
      {
        title: 'Care & Support',
        copy: 'I host, update and look after your site after launch, so you never have to worry about it.',
        tags: ['Hosting', 'Maintenance', 'Updates', 'Support'],
      },
    ],
  },

  // Small notes that pop up next to each person on the People floor when you click them.
  // Every person in the office is Philips, doing something different.
  people: {
    hero: {
      name: 'Philips',
      role: 'Developer',
      status: 'Turned round to say hi',
      note: "Hi, I'm Philips! I design and build websites, including this whole office. You clicked, so I swivelled. Want something built? Say hi on WhatsApp.",
    },
    typer: {
      name: 'Philips',
      role: 'Developer · Deep focus mode',
      status: 'Shipping a feature',
      note: 'Headphones on, ultrawide full of code, one more commit. If it compiles first try, I will pretend that was the plan all along.',
    },
  } as Record<string, { name: string; role: string; status: string; note: string }>,

  // Memo cards opened by clicking things in the 3D office (key = the "#id" link)
  memos: {
    nap: {
      name: 'Philips',
      role: 'Developer · After an all-nighter',
      status: 'Do not disturb (compiling)',
      note: "Not sleeping, just running a very long build. In my head. With my eyes closed. Most of my best bugs get fixed in dreams anyway, so honestly it's research.",
      facts: [
        ['Naps today', '3 (and counting)'],
        ['Favourite stack', 'Pillow.js'],
        ['Best feature shipped', 'Sleep mode'],
      ],
      signoff: 'Shh. Leave a coffee next to me and back away slowly.',
      sleepy: true,
    },
    simrig: {
      name: 'The Sim Rig',
      role: 'Racing cockpit · My official "meeting room"',
      status: 'Lap 2 of 3 · P1',
      note: "Three screens, a bucket seat and a wheel that's seen more action than my whiteboard. Every big decision I make gets settled here: if I lose the race, I write the documentation.",
      facts: [
        ['Top speed on screen', '248 km/h'],
        ['Track record', '1:32.4 (disputed)'],
        ['Docs written after losing', 'All of them'],
      ],
      signoff: 'Buckle up. Mirrors, signal, ship it.',
    },
    pinball: {
      name: 'The Pinball',
      role: 'Neon pinball · Stress relief department',
      status: 'Ball 3 · Multiball ready',
      note: "My unofficial QA tool. If I can't break a website, I can at least break the high score. Client feedback gets read here, one flipper at a time.",
      facts: [
        ['High score', '13,370,000'],
        ['Tilts this week', "I don't talk about it"],
        ['Balls lost under the sofa', '7'],
      ],
      signoff: 'Insert coin. Keep both hands on the flippers.',
    },
    chill: {
      name: 'The Chill Zone',
      role: 'Couch co-op · Creative recharge station',
      status: 'Player 2 has entered the game',
      note: "Where my big ideas go to respawn. Stuck on a design? I grab a pad, lose a round, and come back with the answer. It works more often than I'd like to admit.",
      facts: [
        ['Controllers', '2 (the cyan one is mine)'],
        ['Bean bags', '3 (nobody sits in the orange one)'],
        ['Brainstorms per match', 'At least one'],
      ],
      signoff: 'Press any button to continue.',
    },
  } as Record<
    string,
    { name: string; role: string; status: string; note: string; facts: string[][]; signoff: string; sleepy?: boolean }
  >,

  contact: {
    slogan: 'Got a project in mind?',
    note: "Tell me a little about it. Hitting send opens WhatsApp with your message ready to go, and I usually reply within a day.",
    services: ['Landing page', 'Business website', 'Online store', 'Web app', 'Not sure yet'],
    budgets: ['Under RM 3k', 'RM 3k – 8k', 'RM 8k – 20k', 'RM 20k+', 'Not sure yet'],
  },
}
