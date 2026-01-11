const gulp = require('gulp');
const sass = require('gulp-sass')(require('sass'));

// Define the Sass compilation task
function compileSass() {
  return gulp.src('app/source/sass/**/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('app/static/css'));
}

// Define a watch task to run the compiler automatically on file changes
function watchFiles() {
  gulp.watch('app/source/sass/**/*.scss', compileSass);
}

// Export tasks to be run from the command line
exports.sass = compileSass;
exports.watch = watchFiles;
exports.default = watchFiles;