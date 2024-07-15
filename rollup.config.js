// get the config object from the package file
module.exports = [
  {
    input: `./node_modules/maplibre-gl/dist/maplibre-gl.js`,
    output: {
      file: `static/javascripts/maplibre-gl.js`,
      format: "iife",
    }
  },
];
