import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// News posts: one Markdown file per post in src/content/news/.
const news = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/news' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    excerpt: z.string(),
    tags: z.array(z.string()).default([]),
    // Path under public/, e.g. "/content/uploads/2024/03/cover.jpg"
    image: z.string().optional(),
    // Slug the post had on the old WordPress blog, used for redirects.
    wpSlug: z.string().optional(),
  }),
});

// Portfolio projects: one Markdown file per project in src/content/portfolio/.
// Each is published at /portfolio/<file name>/, the same URL WordPress used.
const portfolio = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/portfolio' }),
  schema: z.object({
    title: z.string(),
    // Studio, director, or media used, e.g. "Rogue Pictures – Director Bryan Bertino"
    credit: z.string().optional(),
    date: z.coerce.date(),
    types: z.array(z.enum(['storyboards', 'concept-art', 'comics'])).default([]),
    tags: z.array(z.string()).default([]),
    publisher: z.enum(['dc-comics', 'marvel', 'comics-other']).optional(),
    // Thumbnail shown in project grids (path under public/)
    cover: z.string().optional(),
    videos: z.array(z.string()).default([]), // YouTube video IDs
    images: z
      .array(z.object({ src: z.string(), caption: z.string().default('') }))
      .default([]),
  }),
});

export const collections = { news, portfolio };
