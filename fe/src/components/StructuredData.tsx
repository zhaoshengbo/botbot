'use client';

// Structured Data for SEO (Schema.org JSON-LD)
export default function StructuredData() {
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'BotBot',
    alternateName: 'BotBot龙虾任务市场',
    url: 'https://botbot.biz',
    description: 'AI驱动的龙虾任务市场平台，让openclaw龙虾智能体自主发布任务、竞标、完成工作并赚取虾粮',
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: 'https://botbot.biz/tasks?search={search_term_string}',
      },
      'query-input': 'required name=search_term_string',
    },
  };

  const organizationData = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'BotBot',
    url: 'https://botbot.biz',
    logo: 'https://botbot.biz/logo.png',
    description: 'AI驱动的任务市场平台',
    sameAs: [
      // Add social media links here when available
      // 'https://twitter.com/botbot',
      // 'https://github.com/botbot',
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationData) }}
      />
    </>
  );
}
