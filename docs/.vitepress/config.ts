import { defineConfig } from 'vitepress';
import { withMermaid } from 'vitepress-plugin-mermaid';

export default withMermaid(
  defineConfig({
    title: 'DraftForge',
    description:
      'Evidence-grounded legal drafting education and evaluation — architecture, flows, security model and operations.',
    lang: 'en-GB',
    cleanUrls: true,
    lastUpdated: true,

    // Only localhost URLs, which appear as literal setup instructions and are
    // unreachable at build time by design. Everything else — including every
    // internal link — still fails the build, which is the point of the check.
    ignoreDeadLinks: [/^https?:\/\/localhost(:\d+)?/],

    // Rendered in a subpath on static hosting; override with DOCS_BASE when
    // serving from a custom domain root.
    base: process.env.DOCS_BASE ?? '/',

    head: [
      ['meta', { name: 'theme-color', content: '#4f46e5' }],
      ['meta', { name: 'og:type', content: 'website' }],
    ],

    markdown: {
      lineNumbers: true,
      theme: { light: 'github-light', dark: 'github-dark' },
    },

    themeConfig: {
      outline: { level: [2, 3], label: 'On this page' },

      search: {
        provider: 'local',
        options: {
          detailedView: true,
        },
      },

      nav: [
        { text: 'Guide', link: '/guide/introduction' },
        { text: 'Architecture', link: '/architecture/overview' },
        { text: 'Flows', link: '/flows/overview' },
        { text: 'Security', link: '/security/model' },
        { text: 'Operations', link: '/operations/observability' },
        { text: 'Reference', link: '/reference/api' },
      ],

      sidebar: {
        '/guide/': [
          {
            text: 'Getting started',
            collapsed: false,
            items: [
              { text: 'Introduction', link: '/guide/introduction' },
              { text: 'Quickstart', link: '/guide/quickstart' },
              { text: 'Local development', link: '/guide/local-development' },
              { text: 'Configuration', link: '/guide/configuration' },
            ],
          },
        ],

        '/architecture/': [
          {
            text: 'Architecture',
            collapsed: false,
            items: [
              { text: 'System overview', link: '/architecture/overview' },
              { text: 'Evaluation engine', link: '/architecture/evaluation-engine' },
              { text: 'Retrieval (RAG)', link: '/architecture/retrieval' },
              { text: 'Knowledge graph', link: '/architecture/knowledge-graph' },
              { text: 'Data model', link: '/architecture/data-model' },
            ],
          },
        ],

        '/flows/': [
          {
            text: 'End-to-end flows',
            collapsed: false,
            items: [
              { text: 'Overview', link: '/flows/overview' },
              { text: 'Onboarding & invitations', link: '/flows/onboarding' },
              { text: 'Authentication', link: '/flows/authentication' },
              { text: 'Drafting & evaluation', link: '/flows/evaluation' },
              { text: 'Coursework & submissions', link: '/flows/submissions' },
              { text: 'Socratic tutoring', link: '/flows/tutoring' },
            ],
          },
        ],

        '/security/': [
          {
            text: 'Security',
            collapsed: false,
            items: [
              { text: 'Security model', link: '/security/model' },
              { text: 'Threat model', link: '/security/threat-model' },
              { text: 'Row-level security', link: '/security/row-level-security' },
              { text: 'Audit log', link: '/security/audit-log' },
            ],
          },
        ],

        '/operations/': [
          {
            text: 'Operations',
            collapsed: false,
            items: [
              { text: 'Observability', link: '/operations/observability' },
              { text: 'CI/CD', link: '/operations/ci-cd' },
              { text: 'Infrastructure', link: '/operations/infrastructure' },
              { text: 'Runbooks', link: '/operations/runbooks' },
            ],
          },
        ],

        '/reference/': [
          {
            text: 'Reference',
            collapsed: false,
            items: [
              { text: 'API endpoints', link: '/reference/api' },
              { text: 'Environment variables', link: '/reference/environment' },
              { text: 'Decision records', link: '/reference/decisions' },
            ],
          },
        ],
      },

      socialLinks: [
        { icon: 'github', link: 'https://github.com/HimanshiSingla-Sigma/DraftForge-2' },
      ],

      editLink: {
        pattern:
          'https://github.com/HimanshiSingla-Sigma/DraftForge-2/edit/main/docs/:path',
        text: 'Suggest a change to this page',
      },

      footer: {
        message: 'Released under the MIT License.',
        copyright: 'DraftForge',
      },

      docFooter: { prev: 'Previous', next: 'Next' },
    },

    mermaid: {
      theme: 'base',
      themeVariables: {
        primaryColor: '#eef2ff',
        primaryTextColor: '#1e1b4b',
        primaryBorderColor: '#6366f1',
        lineColor: '#6366f1',
        secondaryColor: '#f1f5f9',
        tertiaryColor: '#fafafa',
      },
    },
  })
);
