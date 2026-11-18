import { getCollection, type CollectionEntry } from 'astro:content';

export type Project = CollectionEntry<'portfolio'>;

export const TAG_LABELS: Record<string, string> = {
  'feature-film': 'Feature Film',
  television: 'Television',
  'video-game': 'Video Game',
  commercial: 'Commercial',
  props: 'Props',
  ethereal: 'Ethereal',
  'inks-only': 'Inks',
  'pencils-inks': 'Pencils / Inks',
  'pencils-inks-colors': 'Pencils / Inks / Colors',
  'cover-and-interior-pencils': 'Cover & Interior Pencils',
};

export const TYPE_LABELS: Record<string, string> = {
  storyboards: 'Storyboards',
  'concept-art': 'Concept Art',
  comics: 'Comics',
};

export const PUBLISHERS = [
  { id: 'dc-comics', label: 'DC Comics' },
  { id: 'marvel', label: 'Marvel Comics' },
  { id: 'comics-other', label: 'Other Comic Books' },
] as const;

/** Newest first; ties keep a stable alphabetical order. */
export async function getProjects(filter?: (p: Project) => boolean): Promise<Project[]> {
  const all = await getCollection('portfolio', filter);
  return all.sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf() || a.data.title.localeCompare(b.data.title));
}

export const projectUrl = (p: Project) => `/portfolio/${p.id}/`;

// The most specific section a project belongs to: where "back" goes, and the
// set that previous/next step through.
export function sectionOf(p: Project) {
  const { tags, types } = p.data;
  if (tags.includes('ethereal')) return { key: 'ethereal', href: '/ethereal/', label: 'Ethereal: A Tale' };
  if (types.includes('comics')) return { key: 'comics', href: '/comics/', label: 'Comics' };
  if (types.includes('storyboards')) return { key: 'storyboards', href: '/storyboards/', label: 'Storyboards' };
  if (types.includes('concept-art')) return { key: 'concept-art', href: '/concept-art/', label: 'Concept Art' };
  return { key: 'portfolio', href: '/portfolio/', label: 'Portfolio' };
}
