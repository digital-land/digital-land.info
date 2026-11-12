// MapLibre v6+ only ships ES modules. We re-bundle it as a classic script that
// sets the `maplibregl` global, so templates can keep loading it with a plain
// <script> tag and the existing inline map code keeps working unchanged.
module.exports = [
  {
    input: `./node_modules/maplibre-gl/dist/maplibre-gl.mjs`,
    output: {
      file: `static/javascripts/maplibre-gl.js`,
      format: "iife",
      name: "maplibregl",
    }
  },
  // MapLibre loads its web worker from `maplibre-gl-worker.mjs` next to the
  // main script, so it must be published alongside it.
  {
    input: `./node_modules/maplibre-gl/dist/maplibre-gl-worker.mjs`,
    output: {
      file: `static/javascripts/maplibre-gl-worker.mjs`,
      format: "es",
    }
  },
];
