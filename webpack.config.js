const path = require('path')

module.exports = {
  entry: '/octoprint_gcode_macro/static/src/gcode_macro.js',
  output: {
    filename: 'gcode_macro.js',
    path: path.resolve(__dirname, 'octoprint_gcode_macro/static/dist')
  },
  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      }
    ]
  }
}
