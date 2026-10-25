export interface CreditEntry {
  name?: string;
  url?: string;
}

export interface GalleryImageMeta {
  credit1?: CreditEntry;
  credit2?: CreditEntry;
  credit3?: CreditEntry;
  description?: string;
}

export interface ProcessedCredit {
  name: string;
  url?: string;
}

export interface ProcessedGalleryImageMeta {
  year: string;
  credits: ProcessedCredit[];
  description?: string;
}

/**
 * Gallery image metadata registry keyed by filename (e.g. '2025_01.jpg', '2021_01.png', etc.).
 * Up to three optional credit entries (each containing name and url) can be specified.
 * The year is always extracted from the filename pattern (e.g. `YYYY_NN`).
 */
export const galleryMetadata: Record<string, GalleryImageMeta> = {
  '2025_01.jpg': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: 'Tuesday The Sky - Indoor Enthusiast promotional photo',
  },
  '2021_01.png': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: 'Tuesday The Sky - The Blurred Horizon promotional portrait',
  },
  '2017_02.jpg': {
    credit1: { name: 'Markus Wiedenmann', url: 'https://www.instagram.com/markus.wiedenmann.photography/' },
    description: 'Jim Matheos (Fates Warning) Haarlem 2017',
  },
  '2017_01.jpg': {
    credit1: { name: 'Lindsay Matheos', url: '' },
    description: 'Tuesday The Sky - Drift promotional portrait',
  },
};

export function getGalleryImageMeta(filename: string): ProcessedGalleryImageMeta {
  const custom = galleryMetadata[filename] || {};

  // Parse YYYY from filename pattern like 2025_01.jpg
  const match = filename.match(/^(\d{4})/i) || filename.match(/(\d{4})_\d+/i);
  const year = match ? match[1] : '';

  // Process up to three optional credit entries
  const rawCredits = [custom.credit1, custom.credit2, custom.credit3];
  const credits: ProcessedCredit[] = [];

  for (const entry of rawCredits) {
    if (entry && entry.name && entry.name.trim().length > 0) {
      credits.push({
        name: entry.name.trim(),
        url: entry.url && entry.url.trim().length > 0 ? entry.url.trim() : undefined,
      });
    }
  }

  const description =
    custom.description && custom.description.trim().length > 0 ? custom.description.trim() : undefined;

  return {
    year,
    credits,
    description,
  };
}
