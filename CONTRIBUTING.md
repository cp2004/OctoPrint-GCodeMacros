Contributions are welcome to all my projects on GitHub, and this is no exception.

## Building the frontend code

This plugin uses sass to manage compiling the CSS files. This requires a recent version of NodeJS.

- Run `npm install` to install the dependencies
- Run `npm start` to start the development environment, this will watch & build the SCSS files in development mode
- Run `npm run release` if you want to test the production-ready, minimized build.

The compiled CSS files are not checked in as this build is automatically done on release. A GitHub action is in place
that will build individual commits if you do not want to build it locally.

## Creating PRs

Please test your contribution, and explain its purpose clearly when you create commits & a PR.
Make sure you don't include the compiled CSS files, though they should be automatically ignored by Git.
