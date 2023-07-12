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
  stylesheets: `npx node-sass ${configPaths.scssPath} -o ${configPaths.stylesheetsOutputPath} --include-path ${configPaths.govukFrontendPath} --include-path ${configPaths.digitalLandFrontendPath}`,
}

scripts.copy = {
  govukAssets: `npx copyfiles -u 2 "${configPaths.govukFrontendPath}govuk/assets/**" ${configPaths.govukOutputPath}`
}

scripts.watch = {
  pages: `npx browser-sync start --proxy ${configPaths.serverURL} --files ${configPaths.templatesPath} ${configPaths.staticFilesPath}`,
  assets: `npx chokidar ${configPaths.watchPaths} -c "npm run nps build.javascripts && npm run nps build.stylesheets"`,
  stylesheets: `npx chokidar ${configPaths.watchPaths} -c "npm run nps build.stylesheets"`,
}

module.exports = { scripts }
