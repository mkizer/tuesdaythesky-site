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
 * Gallery image metadata registry keyed by filename (e.g. '2026_03_DescText.png', '2024_01_KoMvideo.jpg').
 * Up to three optional credit entries (each containing name and url) can be specified.
 * The year is always extracted from the filename pattern (e.g. `YYYY_NN`).
 */
export const galleryMetadata: Record<string, GalleryImageMeta> = {
  '2024_01.jpg': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: '',
  },
  '2024_02.jpg': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: '',
  },
  '2024_03.jpg': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: '',
  },
  '2024_04.jpg': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: '',
  },
  '2024_05.jpg': {
    credit1: { name: 'Laurie Matheos', url: '' },
    description: '',
  },
  '2024_06.jpg': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: '',
  },
  '2024_07.jpg': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: '',
  },
  '2024_08.jpg': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: '',
  },
  '2024_09.png': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: '',
  },
  '2024_10.jpg': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: '',
  },
  '2024_11.jpg': {
    credit1: { name: 'Laurie Matheos', url: '' },
    description: '',
  },
  '2024_12.jpg': {
    credit1: { name: 'Laurie Matheos', url: '' },
    description: '',
  },
  '2024_13.jpg': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: '',
  },
  '2024_14.jpg': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: '',
  },
  '2024_15.jpg': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: '',
  },
  '2024_16.jpg': {
    credit1: { name: 'Laurie Matheos', url: '' },
    description: '',
  },
  '2024_17.jpg': {
    credit1: { name: 'Laurie Matheos', url: '' },
    description: '',
  },
  '2024_18.jpg': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: '',
  },
  '2024_19.jpg': {
    credit1: { name: 'Laurie Matheos', url: '' },
    description: '',
  },
  '2026_01.jpg': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: '',
  },
  '2026_02.jpg': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: '',
  },
  '2026_03.png': {
    credit1: { name: 'Jeremy Saffer', url: 'https://jeremysaffer.com/' },
    description: '',
  },
};

export function getGalleryImageMeta(filename: string): ProcessedGalleryImageMeta {
  const custom = galleryMetadata[filename] || {};

  // Parse YYYY from filename pattern like 2024_01_KoM.jpg
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
