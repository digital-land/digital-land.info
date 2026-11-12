const fs = require('fs')
let scripts = {}

function readJsonFile (filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'))
}

let configPaths = require('./default.paths.json')
const optionalConfigPath = 'digital-land-frontend.config.json'

if (fs.existsSync(optionalConfigPath)) {
  configPaths = {
    ...configPaths,
    ...readJsonFile(optionalConfigPath)
  }
}

scripts.build = {
  stylesheets: `npx sass ${configPaths.scssPath}:${configPaths.stylesheetsOutputPath} --load-path=node_modules`,
}

// Uses Node's built-in fs.cpSync rather than copyfiles, which is unmaintained
// and pulls in the end-of-life glob@7. govuk-frontend v5 ships its assets
// under dist/govuk.
const govukSource = 'node_modules/govuk-frontend/dist/govuk'
const govukDest = `${configPaths.govukOutputPath}govuk`

scripts.copy = {
  govukAssets: `node -e "require('fs').cpSync('${govukSource}', '${govukDest}', { recursive: true })"`
}

scripts.watch = {
  pages: `npx browser-sync start --proxy ${configPaths.serverURL} --files ${configPaths.templatesPath} ${configPaths.staticFilesPath}`,
  assets: `npx chokidar ${configPaths.watchPaths} -c "npm run nps build.javascripts && npm run nps build.stylesheets"`,
  stylesheets: `npx chokidar ${configPaths.watchPaths} -c "npm run nps build.stylesheets"`,
}

module.exports = { scripts }
