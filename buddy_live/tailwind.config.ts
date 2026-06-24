import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        buddy: {
          primary: '#4A90E2',
          secondary: '#7B68EE',
          accent: '#FF6B6B',
          bg: '#F0F4FF',
          surface: '#FFFFFF',
          online: '#4CAF50',
          offline: '#9E9E9E',
          away: '#FF9800',
        },
      },
      backgroundImage: {
        'buddy-gradient': 'linear-gradient(135deg, #4A90E2 0%, #7B68EE 100%)',
      },
    },
  },
  plugins: [],
}

export default config
