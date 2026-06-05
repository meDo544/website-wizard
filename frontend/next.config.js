/** @type {import('next').NextConfig} */

const path = require("path");

const nextConfig = {

  allowedDevOrigins: [
    "34.27.91.3",
  ],

  turbopack: {
    root: path.join(__dirname),
  },

};

module.exports = nextConfig;
