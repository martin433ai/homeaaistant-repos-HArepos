module.exports = {
  webpack: (config, { dev }) => {
    if (!dev) {
      // Disable eval-source-map for production
      config.devtool = 'source-map';
    }
    return config;
  },
};