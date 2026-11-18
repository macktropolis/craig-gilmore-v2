// Thumbnail lookup for WordPress uploads. scripts/make-thumbs.py writes
// thumbs.json; galleries and cards show the thumbnail, and the lightbox
// opens the full-size original. Falls back to the original when an image
// has no thumbnail yet (re-run the script after adding images).
import thumbs from './thumbs.json';

export interface Thumb {
  src: string;
  width?: number;
  height?: number;
}

const manifest = thumbs as Record<string, { src: string; width: number; height: number }>;

export function thumb(src: string): Thumb {
  return manifest[src] ?? { src };
}
