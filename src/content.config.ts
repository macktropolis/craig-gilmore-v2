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
  }),
});

export const collections = { news };
