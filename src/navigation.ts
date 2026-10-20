import { getPermalink, getBlogPermalink, getAsset } from './utils/permalinks';

export const headerData = {
  links: [
    {
      text: 'News',
      href: getBlogPermalink(),
    },
    {
      text: 'Bio',
      href: getPermalink('/bio'),
    },
    {
      text: 'Music',
      href: getPermalink('/music'),
    },
    {
      text: 'Videos',
      href: getPermalink('/videos'),
    },
    {
      text: 'Images',
      href: getPermalink('/images'),
    },
    {
      text: 'Contact',
      href: getPermalink('/contact'),
    },
  ],
};

export const footerData = {
  links: [
    {
      title: 'News',
      links: [
        { text: 'All Posts', href: '/news' },
        { text: 'News Only', href: '/category/news' },
        { text: 'Videos Only', href: '/tag/video' },
      ],
    },
    {
      title: 'Other Links',
      links: [
        { text: 'Bio', href: '/bio' },
        { text: 'Music', href: '/music' },
        { text: 'Videos', href: '/videos' },
        { text: 'Images', href: '/images' },
        { text: 'Contact', href: '/contact' },
      ],
    },
  ],
  secondaryLinks: [
    { text: 'Terms', href: getPermalink('/terms') },
    { text: 'Privacy Policy', href: getPermalink('/privacy') },
  ],
  socialLinks: [
    { ariaLabel: 'X', icon: 'tabler:brand-x', href: 'https://x.com/NorthSea_Echoes' },
    { ariaLabel: 'Instagram', icon: 'tabler:brand-instagram', href: 'https://www.instagram.com/northseaechoes/' },
    { ariaLabel: 'Facebook', icon: 'tabler:brand-facebook', href: 'https://www.facebook.com/NorthSeaEchoesOFFICIAL' },
    { ariaLabel: 'RSS', icon: 'tabler:rss', href: getAsset('/rss.xml') },
  ],
  footNote: `
  © 2026 North Sea Echoes<br />
  Site by <a class="text-muted hover:text-gray-700 hover:underline dark:text-gray-400 transition duration-150 ease-in-out" href="https://michaelkizer.com/" target="_blank">Michael Kizer</a><br />
  "How to Cast a Shadow" Artwork by <a class="text-muted hover:text-gray-700 hover:underline dark:text-gray-400 transition duration-150 ease-in-out" href="https://www.cfriel.com/home" target="_blank">Chris Friel</a><br />
  "Really Good Terrible Things" Artwork by <a class="text-muted hover:text-gray-700 hover:underline dark:text-gray-400 transition duration-150 ease-in-out" href="https://identity-media.co.uk/" target="_blank">Simon Ward</a>
  `,
};
