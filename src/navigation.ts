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
        { text: 'All Posts', href: getBlogPermalink() },
        { text: 'News Only', href: getPermalink('news', 'category') },
        { text: 'Videos Only', href: getPermalink('video', 'tag') },
      ],
    },
    {
      title: 'Explore',
      links: [
        { text: 'Bio', href: getPermalink('/bio') },
        { text: 'Music', href: getPermalink('/music') },
        { text: 'Videos', href: getPermalink('/videos') },
        { text: 'Images', href: getPermalink('/images') },
        { text: 'Contact', href: getPermalink('/contact') },
      ],
    },
  ],
  secondaryLinks: [
    { text: 'Terms', href: getPermalink('/terms') },
    { text: 'Privacy Policy', href: getPermalink('/privacy') },
  ],
  socialLinks: [
    { ariaLabel: 'Facebook', icon: 'tabler:brand-facebook', href: 'https://www.facebook.com/TuesdaytheSky/' },
    { ariaLabel: 'RSS', icon: 'tabler:rss', href: getAsset('/rss.xml') },
  ],
  footNote: `
  © 2026 Tuesday The Sky<br />
  Site by <a class="text-muted hover:text-gray-700 hover:underline dark:text-gray-400 transition duration-150 ease-in-out" href="https://michaelkizer.com/" target="_blank">Michael Kizer</a><br />
  "Indoor Enthusiast" Artwork by <a class="text-muted hover:text-gray-700 hover:underline dark:text-gray-400 transition duration-150 ease-in-out" href="https://identity-media.co.uk/" target="_blank">Simon Ward</a>
  `,
};
