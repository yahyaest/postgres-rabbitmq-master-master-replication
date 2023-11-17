
const {
 PHASE_DEVELOPMENT_SERVER,
 PHASE_PRODUCTION_BUILD,
 PHASE_PRODUCTION_SERVER,
} = require("next/constants");

/** @type {import('next').NextConfig} */
// const nextConfig = {}

// module.exports = nextConfig

module.exports = (phase) => {
 if (phase === PHASE_DEVELOPMENT_SERVER) {
   return {
     reactStrictMode: true,
     images: {
       domains: [
         // "media.kitsu.io",
       ],
     },
     env: {
      DJANGO_BASE_URL: process.env.DJANGO_BASE_URL,
     },
   };
 }

 // production
 return {
   reactStrictMode: true,
   images: {
     domains: [
       // "media.kitsu.io",
     ],
   },
   env: {
    DJANGO_BASE_URL: process.env.DJANGO_BASE_URL,
   },
 };
};
